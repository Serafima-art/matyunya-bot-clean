import logging
from typing import Any, Dict, Tuple

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.help_core.dispatchers.help_handler import (
    call_dynamic_solver,
    clean_html_tags,
    format_basic_solution,
)
from matunya_bot_final.help_core.humanizers.template_humanizers.task_11_humanizer import (
    humanize_solution_11,
)
from matunya_bot_final.help_core.prompts.task_11_dialog_prompts import get_task_11_dialog_prompt
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set
from matunya_bot_final.keyboards.navigation.help_dialog_navigation import (
    get_help_panel_keyboard,
)
from matunya_bot_final.states.states import GPState
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
)
from uuid import uuid4

logger = logging.getLogger(__name__)
router = Router(name="task_11_help_router")

_HELP_PANEL_TAG = "task_11_help_panel"


async def _build_task_11_solution(task_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    # Create formatted help text for task 11 using unified solver flow.
    task_subtype = task_data.get('subtype')
    if not task_subtype:
        raise ValueError('task_11_data missing subtype')

    solution_core = await call_dynamic_solver('11', task_subtype, task_data)
    if solution_core is None:
        raise RuntimeError(f'Solver returned no data for subtype {task_subtype!r}')

    try:
        help_text = humanize_solution_11(solution_core)
        help_text = clean_html_tags(help_text)
    except Exception as exc:
        logger.exception('Task 11: humanizer failed', exc_info=exc)
        help_text = format_basic_solution(solution_core)

    return help_text, solution_core

@router.callback_query(TaskCallback.filter(F.action == "11_get_help"))
async def handle_task_11_help(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """Send structured help for task 11 and keep the panel on screen."""

    chat_id = callback.message.chat.id if callback.message else callback.from_user.id

    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")
    await cleanup_messages_by_category(bot, state, chat_id, "help_panels")

    data = await state.get_data()
    task_data = data.get("task_11_data")
    if not isinstance(task_data, dict):
        logger.error("Task 11 help: task_11_data is missing in FSM state")
        await callback.answer("Данные задания не найдены.", show_alert=True)
        return

    try:
        help_text, solution_core = await _build_task_11_solution(task_data)
    except Exception as exc:  # pragma: no cover
        logger.exception("Task 11 help: failed to build solution", exc_info=exc)
        await callback.answer("Не удалось подготовить подсказку.", show_alert=True)
        return

    await state.update_data(task_11_solution_core=solution_core)

    keyboard = get_help_panel_keyboard(task_num="11", subtype=task_data.get("subtype"), question_num=11)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=help_text,
        reply_markup=keyboard,
        message_tag=_HELP_PANEL_TAG,
        category="help_panels",
    )

    await callback.answer()


@router.callback_query(TaskCallback.filter(F.action == "11_ask_gpt"))
async def handle_task_11_ask_gpt(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """Warm up GPT after a template solution and invite the student to dialog."""

    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await callback.answer()

    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")

    data = await state.get_data()
    task_data = data.get("task_11_data")
    if not isinstance(task_data, dict):
        logger.error("Task 11 ask_gpt: task_11_data is missing in state")
        await bot.send_message(chat_id, "Не удалось найти данные задания.")
        return

    solution_core = data.get("task_11_solution_core")
    if solution_core is None:
        try:
            _, solution_core = await _build_task_11_solution(task_data)
        except Exception as exc:  # pragma: no cover
            logger.exception("Task 11 ask_gpt: solver failed", exc_info=exc)
            await bot.send_message(chat_id, "Не удалось подготовить решение для обсуждения.")
            return
        await state.update_data(task_11_solution_core=solution_core)

    student_name = data.get("student_name")
    gender = data.get("gender")
    subtype = task_data.get("subtype")

    task_type_value = task_data.get("task_type")
    golden_set = await get_golden_set((subtype or ""), task_type=task_type_value or 11)

    system_prompt = get_task_11_dialog_prompt(

        solution_core=solution_core,

        student_name=student_name,

        gender=gender,

        golden_set=golden_set,

    )


    previous_state = await state.get_state()

    await state.update_data(
        gpt_dialog_context="task_11",
        gpt_system_prompt=system_prompt,
        gpt_dialog_history=[],
        gpt_previous_state=previous_state,
    )
    await state.set_state(GPState.in_dialog)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text="Спрашивай! Я готов помочь разобраться в этом решении.",
        reply_markup=None,
        message_tag=f"task_11_gpt_prompt_{uuid4().hex}",
        category="dialog_messages",
    )

