from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.gpt.gpt_utils import ask_gpt_with_history
from matunya_bot_final.help_core.prompts.dialog_prompts import get_help_dialog_prompt
from matunya_bot_final.help_core.prompts.task_11_dialog_prompts import get_task_11_dialog_prompt
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set
from matunya_bot_final.keyboards.navigation.help_dialog_navigation import get_gpt_dialog_keyboard
from matunya_bot_final.utils.text_formatters import sanitize_gpt_response
from matunya_bot_final.states.states import GPState
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
    track_existing_message,
)
from uuid import uuid4


logger = logging.getLogger(__name__)
router = Router(name="gpt_dialog_control_router")

_DIALOG_CATEGORY = "dialog_messages"
_HELP_PANEL_CATEGORY = "help_panels"

_DIALOG_CONTEXT_KEYS: Sequence[str] = ("dialog_context", "gpt_dialog_context")
_HISTORY_KEYS: Sequence[str] = ("dialog_history", "gpt_dialog_history")
_SYSTEM_PROMPT_KEY = "gpt_system_prompt"
_PREVIOUS_STATE_KEY = "gpt_previous_state"
_TASK_1_5_DATA_KEY = "task_1_5_data"
_TASK_1_5_SOLUTION_KEYS: Sequence[str] = ("task_1_5_solution_core", "solution_core")
_STUDENT_NAME_KEY = "student_name"
_GENDER_KEY = "gender"

_FAREWELL_TAG = "gpt_dialog_farewell"
_PROMPT_TAG = "gpt_dialog_prompt"
_ANSWER_TAG = "gpt_dialog_answer"



def _make_tag(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _pick_first(data: Dict[str, Any], keys: Iterable[str]) -> Any:
    """Return the first non-None value stored under the provided keys."""
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return None


def _ensure_history(value: Any) -> List[Dict[str, Any]]:
    """Normalise dialog history to a mutable list of message dicts."""
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return list(value)


@router.callback_query(TaskCallback.filter(F.action == "dismiss_help_panel"))
async def handle_dismiss_help_panel(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await cleanup_messages_by_category(bot, state, chat_id, _HELP_PANEL_CATEGORY)
    await cleanup_messages_by_category(bot, state, chat_id, _DIALOG_CATEGORY)

    data = await state.get_data()
    keyboard_payload = data.get("keyboard_to_restore")

    if keyboard_payload:
        message_id = keyboard_payload.get("message_id")
        markup_data = keyboard_payload.get("reply_markup")
        target_chat_id = keyboard_payload.get("chat_id") or chat_id

        try:
            if message_id and markup_data:
                restored_markup = InlineKeyboardMarkup.model_validate(markup_data)
                await bot.edit_message_reply_markup(
                    chat_id=target_chat_id,
                    message_id=message_id,
                    reply_markup=restored_markup,
                )
        except Exception as restore_exc:  # pragma: no cover
            logger.warning("Не удалось восстановить клавиатуру исходного сообщения", exc_info=restore_exc)
        finally:
            await state.update_data(keyboard_to_restore=None)
    else:
        if "keyboard_to_restore" in data:
            await state.update_data(keyboard_to_restore=None)

    await callback.answer("Помощь скрыта")


@router.callback_query(TaskCallback.filter(F.action == "end_gpt_dialog"))
async def handle_end_gpt_dialog(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await cleanup_messages_by_category(bot, state, chat_id, _DIALOG_CATEGORY)

    data = await state.get_data()
    previous_state = data.get(_PREVIOUS_STATE_KEY)

    for key in _DIALOG_CONTEXT_KEYS:
        data.pop(key, None)
    for key in _HISTORY_KEYS:
        data.pop(key, None)
    data.pop(_SYSTEM_PROMPT_KEY, None)
    data.pop(_PREVIOUS_STATE_KEY, None)

    await state.update_data(**data)

    if previous_state:
        await state.set_state(previous_state)
    else:
        await state.set_state(None)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text="Рад был помочь!",
        message_tag=_FAREWELL_TAG,
        category=_DIALOG_CATEGORY,
    )

    await callback.answer("Диалог завершён")


@router.callback_query(TaskCallback.filter(F.action == "continue_gpt_dialog"))
async def handle_continue_gpt_dialog(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    chat_id = callback.message.chat.id if callback.message else callback.from_user.id

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text="Что ещё хочешь спросить?",
        reply_markup=None,
        message_tag=_make_tag(_PROMPT_TAG),
        category=_DIALOG_CATEGORY,
    )

    await callback.answer()


@router.message(GPState.in_dialog, F.text)
async def handle_gpt_dialog_message(message: Message, state: FSMContext, bot: Bot) -> None:
    chat_id = message.chat.id

    await track_existing_message(
        state=state,
        message_id=message.message_id,
        message_tag=f"gpt_dialog_user_{message.message_id}",
        category=_DIALOG_CATEGORY,
    )

    data = await state.get_data()

    context = _pick_first(data, _DIALOG_CONTEXT_KEYS)
    if not context:
        logger.warning("GPState.in_dialog triggered without dialog context")
        await message.answer("Диалог ещё не запущен. Попробуй снова открыть помощь.")
        return

    history = _ensure_history(_pick_first(data, _HISTORY_KEYS))
    system_prompt: Optional[str]

    if context == "task_1_5":
        task_1_5_data = data.get(_TASK_1_5_DATA_KEY)
        solution_core = _pick_first(data, _TASK_1_5_SOLUTION_KEYS)
        if task_1_5_data is None or solution_core is None:
            logger.error("Task 1-5 dialog missing context: task_1_5_data=%s, solution_core=%s", bool(task_1_5_data), bool(solution_core))
            await message.answer("Не могу найти данные задачи. Попроси помощь ещё раз.")
            return

        subtype = (
            task_1_5_data.get("metadata", {}).get("subtype")
            or task_1_5_data.get("subtype")
            or data.get("current_subtype")
            or ""
        )
        task_type = task_1_5_data.get("task_type")
        golden_set = await get_golden_set(subtype, task_type=task_type)
        system_prompt = get_help_dialog_prompt(
            task_1_5_data=task_1_5_data,
            solution_core=solution_core,
            dialog_history=history,
            student_name=data.get(_STUDENT_NAME_KEY),
            gender=data.get(_GENDER_KEY),
            golden_set=golden_set,
        )
    elif context == "task_11":
        task_11_data = data.get("task_11_data", {})
        subtype = task_11_data.get("subtype") or ""
        task_type_11 = task_11_data.get("task_type")
        golden_set = await get_golden_set(subtype, task_type=task_type_11 or 11)
        solution_core_11 = data.get("task_11_solution_core")
        system_prompt = get_task_11_dialog_prompt(
            solution_core=solution_core_11,
            student_name=data.get(_STUDENT_NAME_KEY),
            gender=data.get(_GENDER_KEY),
            golden_set=golden_set,
        )
        if not system_prompt:
            system_prompt = data.get(_SYSTEM_PROMPT_KEY)
        if not system_prompt:
            logger.error("Task 11 dialog missing system prompt")
            await message.answer("Не удалось восстановить подсказку. Нажми «Задать вопрос» ещё раз.")
            return
    else:
        logger.error("Unsupported dialog context '%s'", context)
        await message.answer("Пока не умею обсуждать эту подсказку.")
        return


    try:
        reply_text, updated_history = await ask_gpt_with_history(
            user_prompt=message.text,
            dialog_history=history,
            system_prompt=system_prompt,
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("ask_gpt_with_history failed", exc_info=exc)
        await message.answer("Не удалось получить ответ от GPT. Попробуй ещё раз позже.")
        return

    history_updates = {key: updated_history for key in _HISTORY_KEYS}
    await state.update_data(**history_updates)

    sanitized_reply = sanitize_gpt_response(reply_text)
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=sanitized_reply,
        reply_markup=get_gpt_dialog_keyboard(),
        message_tag=_make_tag(_ANSWER_TAG),
        category=_DIALOG_CATEGORY,
    )


__all__ = ["router"]

