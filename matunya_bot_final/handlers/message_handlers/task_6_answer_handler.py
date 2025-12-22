import logging
import re
import random
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from matunya_bot_final.states.states import TaskState
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    get_message_id_by_tag,
    send_tracked_message,
)
from matunya_bot_final.utils.text_formatters import escape_for_telegram, format_task
from matunya_bot_final.utils.answer_utils import answers_equal
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    get_task_completed_keyboard,
)
from matunya_bot_final.gpt.phrases.tasks.correct_answer_feedback import get_random_feedback
from matunya_bot_final.gpt.phrases.tasks.incorrect_answer_feedback import (
    INCORRECT_FEEDBACK_PHRASES,
)

logger = logging.getLogger(__name__)
router = Router()

_ANSWER_TAG = "task_6_main_text"
_ANSWER_LINE_PATTERN = re.compile(r"^Ответ:.*$", flags=re.MULTILINE)


@router.message(TaskState.waiting_for_answer_6, F.text)
async def handle_task_6_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает текстовый ответ пользователя для задания 6."""
    user_answer_raw = (message.text or "").strip()
    user_id = message.from_user.id
    logger.info(
        "Task 6: получен ответ от пользователя %s: '%s'",
        user_id,
        user_answer_raw,
    )

    # Пытаемся удалить сообщение пользователя (чтобы не плодить мусор в чате)
    try:
        await message.delete()
        logger.info("Task 6: сообщение пользователя %s удалено.", user_id)
    except Exception as exc:  # pragma: no cover
        logger.error(
            "Task 6: не удалось удалить сообщение пользователя %s: %s",
            user_id,
            exc,
        )

    # Чистим старые диалоговые сообщения (подсказки, комментарии)
    await cleanup_messages_by_category(
        bot=message.bot,
        state=state,
        chat_id=message.chat.id,
        category="dialog_messages",
    )

    data = await state.get_data()
    task_data = data.get("task_6_data")
    if not isinstance(task_data, dict):
        logger.error("Task 6: данные задания не найдены в FSM.")
        return

    formatted_text = data.get("task_6_formatted_text")
    base_text = formatted_text or _build_base_text(task_data)

    correct_answer = task_data.get("answer")
    if correct_answer is None:
        logger.error("Task 6: эталонный ответ отсутствует в task_data.")
        return

    task_message_id = await get_message_id_by_tag(state, _ANSWER_TAG)
    if task_message_id is None:
        logger.error(
            "Task 6: не удалось получить message_id по тегу '%s'.",
            _ANSWER_TAG,
        )
        return

    # --- Проверяем ответ ученика ---
    is_correct = _compare_single_answer(user_answer_raw, correct_answer)

    mark = "✅" if is_correct else "❌"
    safe_user_answer = escape_for_telegram(user_answer_raw) if user_answer_raw else "—"
    answer_line = f"Ответ: {mark} <b>{safe_user_answer}</b>"
    updated_text = _merge_answer_line(base_text, answer_line)

    task_number = task_data.get("task_number") or 6
    task_subtype = task_data.get("subtype") or "common_fractions"

    keyboard = (
        get_task_completed_keyboard(task_number=task_number, task_subtype=task_subtype)
        if is_correct
        else get_after_task_keyboard(
            task_number=task_number,
            task_subtype=task_subtype,
        )
    )

    # Обновляем основное окно задания
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=task_message_id,
            text=updated_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        logger.info(
            "Task 6: обновлено сообщение задания (message_id=%s).",
            task_message_id,
        )
    except Exception as exc:
        logger.error("Task 6: ошибка при обновлении сообщения: %s", exc)
        return

    # --- Если ответ правильный ---
    if is_correct:
        student_name = data.get("student_name")
        gender = data.get("gender")
        feedback_text = get_random_feedback(
            name=student_name,
            gender=gender,
            help_opened=bool(data.get("help_opened")),
        )

        await send_tracked_message(
            bot=message.bot,
            chat_id=message.chat.id,
            state=state,
            text=feedback_text,
            message_tag="task_6_success_feedback",
            category="dialog_messages",
        )

        updated_state = await state.get_data()
        await _finalize_success(state, updated_state)
        return

    # --- Если ответ неправильный ---
    text = random.choice(INCORRECT_FEEDBACK_PHRASES)

    await send_tracked_message(
        bot=message.bot,
        chat_id=message.chat.id,
        state=state,
        text=text,
        message_tag="task_6_incorrect_answer_prompt",
        category="dialog_messages",
    )

    await state.update_data(task_6_last_attempt=user_answer_raw)


# --------- Вспомогательные функции ---------


def _compare_single_answer(user_answer: str, correct: Any) -> bool:
    """Сравнение одиночного ответа с учётом формата (используем общий помощник)."""
    return answers_equal(user_answer, str(correct))


def _merge_answer_line(base_text: str, answer_line: str) -> str:
    """Заменяет строку 'Ответ: ...' в тексте задания или добавляет её в конец."""
    if _ANSWER_LINE_PATTERN.search(base_text):
        return _ANSWER_LINE_PATTERN.sub(answer_line, base_text, count=1)
    return f"{base_text}\n{answer_line}"


def _build_base_text(task_data: dict) -> str:
    """
    Собирает базовый текст задания 6.

    Для дробей основное условие лежит в question_text.
    Если по какой-то причине его нет — пробуем text.
    """
    raw_text = (
        task_data.get("question_text")
        or task_data.get("text")
        or ""
    )

    task_number = task_data.get("task_number") or 6
    return format_task(str(task_number), raw_text)


async def _finalize_success(state: FSMContext, data: dict) -> None:
    """
    Очищает состояние после успешно решённого задания,
    но сохраняет служебные структуры трекинга сообщений.
    """
    tracked_messages = data.get("tracked_messages")
    message_tags_by_category = data.get("message_tags_by_category")

    await state.clear()

    preserved: dict[str, Any] = {}
    if tracked_messages:
        preserved["tracked_messages"] = tracked_messages
    if message_tags_by_category:
        preserved["message_tags_by_category"] = message_tags_by_category

    if preserved:
        await state.update_data(**preserved)

    logger.info(
        "Task 6: состояние очищено, пользователь завершил задачу.",
    )
