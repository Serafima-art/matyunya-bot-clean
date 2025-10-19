import logging
import random
from uuid import uuid4

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.gpt.phrases.ask_question_phrases import ASK_QUESTION_PHRASES
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set
from matunya_bot_final.help_core.prompts.dialog_prompts import get_help_dialog_prompt
from matunya_bot_final.states.states import GPState
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
)


logger = logging.getLogger(__name__)
router = Router(name="group_1_5_help_router")

_DIALOG_CATEGORY = "dialog_messages"


@router.callback_query(TaskCallback.filter(F.action == "1-5_ask_gpt"))
async def handle_group_1_5_ask_gpt(
    callback: CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
    state: FSMContext,
) -> None:
    """Warm up GPT for follow-up questions about a solved 1-5 task."""

    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await callback.answer()

    await cleanup_messages_by_category(bot, state, chat_id, _DIALOG_CATEGORY)

    data = await state.get_data()
    task_1_5_data = data.get("task_1_5_data") or {}
    solution_core = data.get("task_1_5_solution_core") or data.get("solution_core")
    if solution_core is None:
        logger.error("Group 1-5 ask_gpt: solution_core missing in state")
        await bot.send_message(chat_id, "Сначала решим задачку, потом сможем обсудить.")
        return

    question_num = callback_data.question_num or data.get("current_task_index", 0) + 1
    student_name = data.get("student_name") or "наш герой"
    gender = data.get("gender") or data.get("student_gender") or "neutral"

    if gender == "male":
        glad_word = "рад"
    elif gender == "female":
        glad_word = "рада"
    else:
        glad_word = "рада(‑)"

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
    prompt_text = phrase.format(student_name=student_name, glad_word=glad_word)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=prompt_text,
        reply_markup=None,
        category=_DIALOG_CATEGORY,
        message_tag=f"task_1_5_gpt_prompt_{uuid4().hex}",
    )
