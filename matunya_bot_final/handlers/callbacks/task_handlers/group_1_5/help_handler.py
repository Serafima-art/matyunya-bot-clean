import logging
import random
from typing import Callable, Optional

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.help_core.dispatchers.task_1_5.help_handler_1_5 import SOLVER_DISPATCHER
from matunya_bot_final.help_core.humanizers.solution_humanizer import humanize_solution
from matunya_bot_final.help_core.prompts.dialog_prompts import get_help_dialog_prompt
from matunya_bot_final.gpt.phrases.ask_question_phrases import ASK_QUESTION_PHRASES
from matunya_bot_final.keyboards.navigation.help_dialog_navigation import (
    get_help_panel_keyboard,
)
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import (
    build_focused_keyboard,
)
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set
from matunya_bot_final.states.states import GPState
from matunya_bot_final.utils.db_manager import get_task_by_id
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
)
from uuid import uuid4


logger = logging.getLogger(__name__)
router = Router(name="group_1_5_help_router")

_HELP_PANEL_TAG_TEMPLATE = "help_for_task_{question}"
_DIALOG_CATEGORY = "dialog_messages"
_HELP_CATEGORY = "help_panels"


def _resolve_solver(skill_source_id: str) -> Optional[Callable]:
    """Pick solver based on the skill_source_id embedded in the task."""
    if not skill_source_id:
        return None
    for question_idx, solver in SOLVER_DISPATCHER.items():
        if f"q{question_idx}" in skill_source_id:
            return solver
    return None


@router.callback_query(TaskCallback.filter(F.action == "1-5_get_help"))
async def handle_group_1_5_help(
    callback: CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
    state: FSMContext,
    session_maker: async_sessionmaker,
) -> None:
    """Render structured help for the current task within group 1–5."""

    chat_id = callback.message.chat.id if callback.message else callback.from_user.id

    await callback.answer("Готовлю подсказку... 🤖", show_alert=False)

    await cleanup_messages_by_category(bot, state, chat_id, _DIALOG_CATEGORY)
    await cleanup_messages_by_category(bot, state, chat_id, _HELP_CATEGORY)

    data = await state.get_data()

    task_ids = data.get("task_ids", [])
    current_task_index = data.get("current_task_index", 0)

    if not task_ids or current_task_index >= len(task_ids):
        logger.error("Group 1-5 help: invalid task index in state")
        await callback.answer("Данные задания не найдены.", show_alert=True)
        return

    task_id = task_ids[current_task_index]
    async with session_maker() as session:
        task_obj = await get_task_by_id(session, task_id)

    if task_obj is None:
        logger.error("Group 1-5 help: task with ID=%s not found", task_id)
        await callback.answer("Задание отсутствует.", show_alert=True)
        return

    task_1_5_data = data.get("task_1_5_data") or {}
    tasks = task_1_5_data.get("tasks", [])
    if current_task_index >= len(tasks):
        logger.error("Group 1-5 help: task_1_5_data.tasks shorter than expected")
        await callback.answer("Нет данных для подсказки.", show_alert=True)
        return

    current_task = tasks[current_task_index]
    solver_function = _resolve_solver(current_task.get("skill_source_id", ""))
    if solver_function is None:
        logger.error("Group 1-5 help: solver not resolved for %s", current_task.get("skill_source_id"))
        await callback.answer("Подсказка не поддерживается для этого задания.", show_alert=True)
        return

    question_num = callback_data.question_num or (current_task_index + 1)

    try:
        solution_core = solver_function(task_1_5_data)
        await state.update_data(
            solution_core=solution_core,
            task_1_5_solution_core=solution_core,
            last_help_task_id=task_obj.id,
        )

        student_name = data.get("student_name", "друг")
        gender = data.get("gender")
        humanized_explanation = await humanize_solution(solution_core, state, student_name, gender)

        help_text = f"<b>Подсказка к заданию {question_num}:</b>\n\n{humanized_explanation}"
        keyboard = get_help_panel_keyboard(
            task_num="1-5",
            subtype=current_task.get("skill_source_id"),
            question_num=question_num,
        )

        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=help_text,
            reply_markup=keyboard,
            message_tag=_HELP_PANEL_TAG_TEMPLATE.format(question=question_num),
            category=_HELP_CATEGORY,
        )

    except Exception as exc:  # pragma: no cover
        logger.error("Group 1-5 help: solver failure for task_id=%s", task_obj.id, exc_info=exc)
        await bot.send_message(chat_id, "Не удалось подготовить подсказку. Попробуйте позже.")
        await callback.answer("Ошибка")


@router.callback_query(TaskCallback.filter(F.action == "1-5_ask_gpt"))
async def handle_group_1_5_ask_gpt(
    callback: CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
    state: FSMContext,
) -> None:
    """Warm up GPT for follow-up questions about a solved 1–5 task."""

    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await callback.answer()

    await cleanup_messages_by_category(bot, state, chat_id, _DIALOG_CATEGORY)

    data = await state.get_data()
    task_1_5_data = data.get("task_1_5_data") or {}
    solution_core = data.get("task_1_5_solution_core") or data.get("solution_core")
    if solution_core is None:
        logger.error("Group 1-5 ask_gpt: solution_core missing in state")
        await bot.send_message(chat_id, "Сначала запросите подсказку, затем задавайте вопросы.")
        return

    question_num = callback_data.question_num or data.get("current_task_index", 0) + 1
    student_name = data.get("student_name") or "друг"
    gender = data.get("gender")

    subtype_for_prompt = (

        task_1_5_data.get("metadata", {}).get("subtype")

        or task_1_5_data.get("subtype")

        or data.get("current_subtype")

        or ""

    )

    task_type_for_prompt = (
        task_1_5_data.get("metadata", {}).get("task_type")
        or task_1_5_data.get("task_type")
    )
    golden_set = await get_golden_set(subtype_for_prompt, task_type=task_type_for_prompt)

    system_prompt = get_help_dialog_prompt(

        task_1_5_data=task_1_5_data,

        solution_core=solution_core,

        dialog_history=[],

        student_name=student_name,

        gender=gender or "",

        golden_set=golden_set,

    )


    previous_state = await state.get_state()

    await state.update_data(
        dialog_context="task_1_5",
        gpt_dialog_context="task_1_5",
        gpt_system_prompt=system_prompt,
        dialog_history=[],
        gpt_dialog_history=[],
        gpt_previous_state=previous_state,
        task_1_5_solution_core=solution_core,
        last_help_question_num=question_num,
    )
    await state.set_state(GPState.in_dialog)

    phrase = random.choice(ASK_QUESTION_PHRASES)
    prompt_text = phrase.format(student_name=student_name)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=prompt_text,
        reply_markup=None,
        category=_DIALOG_CATEGORY,
        message_tag=f"task_1_5_gpt_prompt_{uuid4().hex}",
    )
