from __future__ import annotations

import logging
import random
import importlib
import pkgutil
import matunya_bot_final.help_core.dialog_contexts as dialog_contexts

from typing import Any, Dict, Iterable, List, Optional, Sequence, Awaitable, Callable

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.gpt.gpt_utils import ask_gpt_with_history
from matunya_bot_final.keyboards.navigation.help_dialog_navigation import get_gpt_dialog_keyboard
from matunya_bot_final.utils.text_formatters import sanitize_gpt_response
from matunya_bot_final.states.states import GPState
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
    track_existing_message,
)
from uuid import uuid4
from matunya_bot_final.gpt.phrases.ask_question_phrases import ASK_QUESTION_PHRASES
from matunya_bot_final.gpt.phrases.thinking_phrases import THINKING_PHRASES


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


DIALOG_CONTEXT_HANDLERS: Dict[str, Callable[[Dict[str, Any], List[Dict[str, Any]]], Awaitable[Optional[str]]]] = {}


def register_context(name: str):
    def wrapper(func):
        DIALOG_CONTEXT_HANDLERS[name] = func
        logger.info("Registered dialog context: %s", name)
        return func
    return wrapper


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


@router.callback_query(TaskCallback.filter(F.action == "ask_question"))
async def handle_ask_question(callback: CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext) -> None:
    """
    Запускает живой GPT-диалог по нажатию кнопки «❓ Задать вопрос».
    """
    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    data = await state.get_data()

    # Определяем контекст задачи
    task_type = callback_data.question_num or callback_data.task_id or None
    subtype = callback_data.subtype_key or data.get("current_subtype")

    # Нормализуем название контекста диалога по типу задания
    dialog_context: str
    task_type_str = str(task_type) if task_type is not None else ""

    # 1. Группа заданий 1-5 (Шины, Печки и т.д.)
    if task_type_str.isdigit() and int(task_type_str) in range(1, 6):
        dialog_context = "task_1_5"

    # 2. Отдельные задания (Явный список)
    elif task_type_str == "6":
        dialog_context = "task_6"
    elif task_type_str == "8":
        dialog_context = "task_8"  # <--- Наше новое!
    elif task_type_str == "11":
        dialog_context = "task_11"
    elif task_type_str == "20":
        dialog_context = "task_20"

    # 3. Fallback (для будущих заданий, если забыли прописать явно)
    elif task_type:
        dialog_context = f"task_{task_type}"
    else:
        dialog_context = "generic"

    # Сохраняем контекст и активируем диалоговое состояние
    await state.update_data(
        dialog_context=dialog_context,
        gpt_dialog_history=[],
        gpt_system_prompt=None,
        current_subtype=subtype,
    )
    await state.set_state(GPState.in_dialog)

    # Подбираем приветственную фразу для начала диалога
    student_name = data.get("student_name", "друг")
    gender = data.get("gender", "neutral")

    glad_word = "рада" if gender == "female" else "рад"
    ready_word = "готова" if gender == "female" else "готов"
    sure_word = "уверена" if gender == "female" else "уверен"

    phrase_template = random.choice(ASK_QUESTION_PHRASES)
    start_text = phrase_template.format(
        student_name=student_name,
        glad_word=glad_word,
        ready_word=ready_word,
        sure_word=sure_word,
    )

    # Отправляем приглашение к разговору с GPT (без кнопок)
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=start_text,
        reply_markup=None,  # 👈 убрали клавиатуру
        category="dialog_messages",
        message_tag="gpt_dialog_start",
    )

    await callback.answer("Диалог с GPT запущен")


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


@router.callback_query(TaskCallback.filter(F.action == "hide_help"))
async def handle_hide_help(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await cleanup_messages_by_category(bot, state, chat_id, "solution_result")
    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")
    logger.info("Help panel closed (solution_result cleared)")
    await callback.answer("Помощь закрыта")


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

    # 0) Трекаем сообщение ученика (чтобы тоже чистилось)
    await track_existing_message(
        state=state,
        message_id=message.message_id,
        message_tag=f"gpt_dialog_user_{message.message_id}",
        category=_DIALOG_CATEGORY,
    )

    data = await state.get_data()

    # 1) Контекст диалога обязателен
    context = _pick_first(data, _DIALOG_CONTEXT_KEYS)
    if not context:
        logger.warning("GPState.in_dialog triggered without dialog context")
        await message.answer("Диалог ещё не запущен. Попробуй снова открыть помощь.")
        return

    # 2) История
    history = _ensure_history(_pick_first(data, _HISTORY_KEYS))

    # 3) Хендлер контекста
    handler = DIALOG_CONTEXT_HANDLERS.get(context)
    if not handler:
        logger.error("Unsupported dialog context '%s'", context)
        await message.answer("Пока не умею обсуждать эту подсказку.")
        return

    # 4) System prompt
    system_prompt = await handler(data, history)
    if not system_prompt:
        await message.answer("Не удалось найти данные задачи. Попроси помощь ещё раз.")
        return

    # ------------------------------------------------------------------
    # 🔹 Показываем «Секундочку…» и ОБЯЗАТЕЛЬНО трекаем вручную,
    # чтобы cleanup_messages_by_category точно его удалял.
    # ------------------------------------------------------------------
    thinking_text = random.choice(THINKING_PHRASES)
    try:
        thinking_msg = await bot.send_message(
            chat_id=chat_id,
            text=thinking_text,
            reply_markup=None,
        )
        await track_existing_message(
            state=state,
            message_id=thinking_msg.message_id,
            message_tag=_make_tag("gpt_thinking"),
            category=_DIALOG_CATEGORY,
        )
    except Exception as exc:  # pragma: no cover
        # Если не получилось показать "ожидание" — не ломаем диалог
        logger.warning("Failed to send/track thinking message", exc_info=exc)

    # 5) GPT-ответ
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

    # 6) Сохраняем историю
    history_updates = {key: updated_history for key in _HISTORY_KEYS}
    await state.update_data(**history_updates)

    # 7) Отправляем ответ и трекаем (как раньше)
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


for module_info in pkgutil.iter_modules(dialog_contexts.__path__):
    importlib.import_module(f"{dialog_contexts.__name__}.{module_info.name}")
