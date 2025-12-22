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
    send_tracked_message,
    get_message_id_by_tag,
)
from matunya_bot_final.utils.text_formatters import escape_for_telegram, format_task
from matunya_bot_final.gpt.phrases.tasks.correct_answer_feedback import get_random_feedback
from matunya_bot_final.gpt.phrases.tasks.incorrect_answer_feedback import (
    INCORRECT_FEEDBACK_PHRASES,
)
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    get_task_completed_keyboard,
)

# ✨ Рендерим текст задания из expression_tree
from matunya_bot_final.help_core.solvers.task_8.task_8_text_formatter import render_node

logger = logging.getLogger(__name__)
router = Router()

_ANSWER_TAG = "task_8_main_text"
_ANSWER_PATTERN = re.compile(r"^Ответ:.*$", flags=re.MULTILINE)


@router.message(TaskState.waiting_for_answer_8, F.text)
async def handle_task_8_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает текстовый ответ пользователя для задания 8."""
    user_answer_raw = (message.text or "").strip()
    user_id = message.from_user.id
    logger.info("Task 8: получен ответ от пользователя %s: '%s'", user_id, user_answer_raw)

    # Удаляем сообщение ученика
    try:
        await message.delete()
    except Exception:
        pass

    # Чистим старые диалоговые сообщения
    await cleanup_messages_by_category(
        bot=message.bot,
        state=state,
        chat_id=message.chat.id,
        category="dialog_messages",
    )

    data = await state.get_data()
    task_data = data.get("task_8_data")
    if not isinstance(task_data, dict):
        logger.error("Task 8: отсутствует task_8_data")
        return

    # Восстанавливаем текст задания
    base_text = _build_base_text(task_data)

    correct_answer = str(task_data.get("answer", "")).strip()
    if correct_answer == "":
        logger.error("Task 8: нет поля answer")
        return

    task_message_id = await get_message_id_by_tag(state, _ANSWER_TAG)
    if task_message_id is None:
        logger.error("Task 8: не найден message_id по тегу '%s'", _ANSWER_TAG)
        return

    # Проверяем ответ
    is_correct = _compare_single_answer(user_answer_raw, correct_answer)

    mark = "✅" if is_correct else "❌"
    safe_user_answer = escape_for_telegram(user_answer_raw) if user_answer_raw else "—"
    answer_line = f"Ответ: {mark} <b>{safe_user_answer}</b>"
    updated_text = _merge_answer_line(base_text, answer_line)

    task_number = task_data.get("task_number") or 8
    task_subtype = task_data.get("subtype") or "default"

    # 🎯 Клавиатура теперь как в задании 11:
    keyboard = (
        get_task_completed_keyboard(task_number=task_number, task_subtype=task_subtype)
        if is_correct
        else get_after_task_keyboard(task_number=task_number, task_subtype=task_subtype)
    )

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=task_message_id,
            text=updated_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        logger.info("Task 8: обновлено сообщение задания (message_id=%s).", task_message_id)
    except Exception as exc:
        logger.error("Task 8: ошибка при обновлении сообщения: %s", exc)
        return

    # ---------- Правильный ответ ----------
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
            message_tag="task_8_success_feedback",
            category="dialog_messages",
        )

        await _finalize_success(state, data)
        return

    # ---------- Неправильный ответ ----------
    text = random.choice(INCORRECT_FEEDBACK_PHRASES)

    await send_tracked_message(
        bot=message.bot,
        chat_id=message.chat.id,
        state=state,
        text=text,
        message_tag="task_8_incorrect_answer_prompt",
        category="dialog_messages",
    )

    await state.update_data(task_8_last_attempt=user_answer_raw)


# ================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =================


def _compare_single_answer(user_answer: str, correct: str) -> bool:
    return user_answer.strip().lower() == str(correct).strip().lower()


def _merge_answer_line(base_text: str, answer_line: str) -> str:
    if _ANSWER_PATTERN.search(base_text):
        return _ANSWER_PATTERN.sub(answer_line, base_text, count=1)
    return f"{base_text}\n{answer_line}"


def _build_base_text(task_data: dict) -> str:
    """
    Собирает базовый текст задания 8: рендерим expression_tree.
    """
    expression = task_data.get("expression_tree")

    if expression:
        try:
            raw_text = render_node(expression)
        except Exception:
            raw_text = "Ошибка: не удалось построить выражение."
    else:
        raw_text = task_data.get("question_text") or task_data.get("text") or ""

    task_number = task_data.get("task_number") or 8
    return format_task(str(task_number), raw_text)


async def _finalize_success(state: FSMContext, data: dict) -> None:
    tracked = data.get("tracked_messages")
    tags = data.get("message_tags_by_category")

    await state.clear()

    preserved: dict[str, Any] = {}
    if tracked:
        preserved["tracked_messages"] = tracked
    if tags:
        preserved["message_tags_by_category"] = tags

    if preserved:
        await state.update_data(**preserved)
