# keyboards/inline_keyboards/after_task_1_5_keyboard.py
from __future__ import annotations

import random
from typing import Optional

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback

from matunya_bot_final.keyboards.navigation.navigation import main_only_kb

# Пулы фраз
from matunya_bot_final.gpt.phrases.help_block_phrases import (
    MALE_PHRASES, FEMALE_PHRASES, NEUTRAL_PHRASES, HELP_PHRASES
)
from matunya_bot_final.gpt.phrases.after_task_phrases import (
    THEORY_PHRASES, COMBINED_PHRASES
)

# ──────────────────────────────────────────────────────────────────────────────
# ТЕКСТОВЫЕ ПОДСКАЗКИ (с рандомом)
# ──────────────────────────────────────────────────────────────────────────────

def _normalize_gender(value: Optional[str]) -> Optional[str]:
    """Приводит значение пола к 'male' | 'female' | None."""
    if not value:
        return None
    v = str(value).strip().lower()

    male_set = {"m", "male", "boy", "юноша", "парень", "мальчик", "м"}
    female_set = {"f", "female", "girl", "девушка", "девочка", "ж"}

    if v in male_set:
        return "male"
    if v in female_set:
        return "female"
    return None


def _build_help_block_text(gender: Optional[str] = None) -> str:
    """Формирует верхний мотивационный блок под выбранный пол ученика."""
    if gender == "male":
        first = random.choice(MALE_PHRASES)
    elif gender == "female":
        first = random.choice(FEMALE_PHRASES)
    else:
        first = random.choice(NEUTRAL_PHRASES)

    second = random.choice(HELP_PHRASES)
    return f"{first}\n{second}"


def _build_after_task_hint(use_combined_prob: float = 0.55) -> str:
    """Возвращает подсказки для кнопок «📚 Теория» и «⏱ На время»."""
    if COMBINED_PHRASES and random.random() < use_combined_prob:
        return random.choice(COMBINED_PHRASES)

    parts = []
    if THEORY_PHRASES:
        parts.append(random.choice(THEORY_PHRASES))

    random.shuffle(parts)
    return "  ".join(parts)


async def compose_help_block_from_state(state: FSMContext) -> str:
    """Возвращает верхний мотивационный блок с учётом пола из FSM."""
    data = await state.get_data()
    gender_raw = (
        data.get("gender")
        or data.get("student_gender")
        or data.get("user_gender")
        or data.get("sex")
        or data.get("pol")
    )
    gender = _normalize_gender(gender_raw)
    return _build_help_block_text(gender)


def compose_hint_block(use_combined_prob: float = 0.55) -> str:
    """Возвращает подсказки для блока с дополнительными кнопками."""
    return _build_after_task_hint(use_combined_prob)


# ──────────────────────────────────────────────────────────────────────────────
# НОВАЯ АРХИТЕКТУРА: Клавиатуры для Заданий 1-5
# ──────────────────────────────────────────────────────────────────────────────

def build_overview_keyboard(tasks_count: int, subtype_key: str, solved_indices: list | None = None) -> InlineKeyboardMarkup:
    """Обзорная клавиатура с отображением решённых заданий."""

    if solved_indices is None:
        solved_indices = []

    kb = InlineKeyboardBuilder()

    # Кнопки номеров заданий
    for i in range(tasks_count):
        button_text = f"✅ {i + 1}" if i in solved_indices else str(i + 1)
        kb.button(
            text=button_text,
            callback_data=TaskCallback(
                action="1-5_focus_question",
                subtype_key=subtype_key,
                question_num=i + 1,
            ).pack(),
        )

    # Дополнительные инструменты
    kb.button(
        text="🔄 Другое задание",
        callback_data=TaskCallback(
            action="1-5_select_subtype",
            subtype_key=subtype_key,
        ).pack(),
    )
    kb.button(
        text="↩️ Другой подтип",
        callback_data=TaskCallback(action="show_task_1_5_carousel").pack(),
    )

    # Главное меню
    for row in main_only_kb().inline_keyboard:
        kb.row(*row)

    kb.adjust(tasks_count, 2, 1)
    return kb.as_markup()


def build_focused_keyboard(current_question: int, total_questions: int, subtype_key: str) -> InlineKeyboardMarkup:
    """Клавиатура для конкретного задания в серии 1–5."""

    specific_subtype_key = f"{subtype_key}_q{current_question}"
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🆘 Помощь",
        callback_data=TaskCallback(
            action="request_help",
            subtype_key=specific_subtype_key,
            question_num=current_question,
            task_type=current_question,
        ).pack(),
    )
    builder.button(
        text="📚 Теория",
        callback_data=TaskCallback(
            action="1-5_get_theory",
            subtype_key=subtype_key,
            question_num=current_question,
        ).pack(),
    )

    builder.button(
        text="💫 Назад",
        callback_data=TaskCallback(
            action="1-5_tires_back_to_overview",
            subtype_key=subtype_key,
        ).pack(),
    )

    for row in main_only_kb().inline_keyboard:
        builder.row(*row)

    builder.adjust(2, 2)
    return builder.as_markup()


# ──────────────────────────────────────────────────────────────────────────────
# ЭКСПОРТЫ
# ──────────────────────────────────────────────────────────────────────────────

__all__ = [
    "compose_help_block_from_state",
    "compose_hint_block",
    "build_overview_keyboard",
    "build_focused_keyboard",
]
