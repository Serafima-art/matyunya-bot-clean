# -*- coding: utf-8 -*-
"""
Обработчик ответа для Задания 16.
Полностью повторяет UX и архитектуру задания 15 / 8:
— редактируем сообщение задания
— встраиваем ответ в строку «Ответ:»
— показываем ✅ / ❌
— FSM ведёт себя идентично заданию 15
"""

from __future__ import annotations

import logging
import re
import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from matunya_bot_final.states.states import TaskState
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
    get_message_id_by_tag,
)
from matunya_bot_final.utils.text_formatters import (
    escape_for_telegram,
    cleanup_math_for_display,
)
from matunya_bot_final.gpt.phrases.tasks.correct_answer_feedback import (
    get_random_feedback,
)
from matunya_bot_final.gpt.phrases.tasks.incorrect_answer_feedback import (
    INCORRECT_FEEDBACK_PHRASES,
)
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    compose_after_task_message_from_state,
)
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_16.task_16_carousel import (
    get_task_16_theme_name,
)

logger = logging.getLogger(__name__)
router = Router()

__all__ = ("router",)

# Тег сообщения с заданием
_ANSWER_TAG = "task_16_main_text"

# Для замены строки "Ответ: ..."
_ANSWER_PATTERN = re.compile(r"^Ответ:.*$", flags=re.MULTILINE)


# ──────────────────────────────────────────────
# ОСНОВНОЙ HANDLER
# ──────────────────────────────────────────────

@router.message(TaskState.waiting_for_answer_16, F.text)
async def handle_task_16_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает текстовый ответ ученика для задания 16."""
    user_answer_raw = (message.text or "").strip()
    logger.info("Task 16: получен ответ: '%s'", user_answer_raw)

    # 1️⃣ Удаляем сообщение ученика
    try:
        await message.delete()
    except Exception:
        pass

    # 2️⃣ Чистим диалоговые сообщения (реплики, help)
    await cleanup_messages_by_category(
        bot=message.bot,
        state=state,
        chat_id=message.chat.id,
        category="dialog_messages",
    )

    data = await state.get_data()
    task_data = data.get("task_16_data")

    if not isinstance(task_data, dict):
        logger.error("Task 16: отсутствует task_16_data")
        return

    # 3️⃣ Восстанавливаем базовый текст задания
    base_text = await _build_base_text_16(task_data, state)

    # 4️⃣ Правильный ответ
    correct_answer = str(task_data.get("answer", "")).strip()
    if not correct_answer:
        logger.error("Task 16: отсутствует поле answer")
        return

    # 5️⃣ Находим message_id исходного задания
    task_message_id = await get_message_id_by_tag(state, _ANSWER_TAG)
    if task_message_id is None:
        logger.error("Task 16: не найден message_id по тегу %s", _ANSWER_TAG)
        return

    # 6️⃣ Сравнение ответа (нормализация как в задании 15)
    ua = cleanup_math_for_display(user_answer_raw).replace(" ", "").lower()
    ca = cleanup_math_for_display(correct_answer).replace(" ", "").lower()

    is_correct = ua == ca

    mark = "✅" if is_correct else "❌"
    safe_user_answer = escape_for_telegram(
        cleanup_math_for_display(user_answer_raw)
    )
    answer_line = f"Ответ: {mark} <b>{safe_user_answer}</b>"

    updated_text = _merge_answer_line(base_text, answer_line)

    task_number = 16
    task_subtype = task_data.get("pattern") or "default"

    keyboard = get_after_task_keyboard(
        task_number=task_number,
        task_subtype=task_subtype,
    )

    # 7️⃣ Обновляем сообщение с заданием
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=task_message_id,
            text=updated_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.error("Task 16: ошибка при обновлении сообщения: %s", exc)
        return

    # 8️⃣ Реплика Матюни
    if is_correct:
        feedback = get_random_feedback(
            name=data.get("student_name"),
            gender=data.get("gender"),
            help_opened=bool(data.get("help_opened")),
        )
        await send_tracked_message(
            bot=message.bot,
            chat_id=message.chat.id,
            state=state,
            text=feedback,
            message_tag="task_16_success_feedback",
            category="dialog_messages",
        )
    else:
        text = random.choice(INCORRECT_FEEDBACK_PHRASES)
        await send_tracked_message(
            bot=message.bot,
            chat_id=message.chat.id,
            state=state,
            text=text,
            message_tag="task_16_incorrect_feedback",
            category="dialog_messages",
        )

    # 9️⃣ FSM
    if is_correct:
        preserved = {
            k: v
            for k, v in data.items()
            if k in {
                "current_theme",
                "gender",
                "student_name",
                "tracked_messages",
                "message_tags_by_category",
            }
        }

        await state.clear()

        if preserved:
            await state.update_data(**preserved)
    else:
        # FSM остаётся, ждём следующий ответ
        await state.update_data(task_16_last_attempt=user_answer_raw)


# ──────────────────────────────────────────────
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ──────────────────────────────────────────────

def _merge_answer_line(base_text: str, answer_line: str) -> str:
    """Заменяет строку 'Ответ: ...' на новую с галочкой / крестиком."""
    if _ANSWER_PATTERN.search(base_text):
        return _ANSWER_PATTERN.sub(answer_line, base_text, count=1)
    return f"{base_text}\n{answer_line}"


async def _build_base_text_16(task_data: dict, state: FSMContext) -> str:
    footer_text = await compose_after_task_message_from_state(state)

    question_text = task_data.get("question_text", "")
    if "Ответ" not in question_text:
        question_text = question_text.rstrip() + "\n\nОтвет: ____________"

    theme_key = task_data.get("theme_key", "central_and_inscribed_angles")
    theme_name = get_task_16_theme_name(theme_key)

    return (
        f"<b>Задание 16:</b> {theme_name}\n\n"
        f"{question_text}\n\n\n"
        f"{footer_text}"
    )
