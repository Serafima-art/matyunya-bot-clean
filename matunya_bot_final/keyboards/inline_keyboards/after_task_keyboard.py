from __future__ import annotations

import random
from typing import Optional

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.gpt.phrases.after_task_phrases import (
    COMBINED_PHRASES,
    THEORY_PHRASES,
)
from matunya_bot_final.gpt.phrases.help_block_phrases import (
    FEMALE_PHRASES,
    HELP_PHRASES,
    MALE_PHRASES,
    NEUTRAL_PHRASES,
)
from matunya_bot_final.keyboards.navigation.navigation import main_only_kb


# ──────────────────────────────────────────────────────────────────────────────
# ТЕКСТОВЫЕ ПОДСКАЗКИ
# ──────────────────────────────────────────────────────────────────────────────

def _normalize_gender(value: Optional[str]) -> Optional[str]:
    """
    Приводит значение пола к 'male' | 'female' | None.
    Поддерживает разные варианты хранения.
    """
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
    """
    Верхний блок под пол ученика:
    1) приглашение к самостоятельному решению (без слова «Готово»)
    2) мягкая подсказка про кнопку «Помощь»
    """
    if gender == "male":
        first = random.choice(MALE_PHRASES)
    elif gender == "female":
        first = random.choice(FEMALE_PHRASES)
    else:
        first = random.choice(NEUTRAL_PHRASES)

    second = random.choice(HELP_PHRASES)
    return f"{first}\n{second}"


def _build_after_task_hint(use_combined_prob: float = 0.55) -> str:
    """
    Подсказки к кнопкам 📚 Теория и ⏱ На время:
    — либо одна готовая связка,
    — либо склейка из двух независимых фраз (порядок случайный).
    """
    if COMBINED_PHRASES and random.random() < use_combined_prob:
        return random.choice(COMBINED_PHRASES)

    parts = []
    if THEORY_PHRASES:
        parts.append(random.choice(THEORY_PHRASES))

    random.shuffle(parts)
    return "  ".join(parts)


def compose_after_task_message(gender: Optional[str] = None) -> str:
    """
    Финальный верхний текст перед клавиатурой.
    ВАЖНО: не содержит слова «Готово».
    """
    header = "🚀 Твой ход!"
    help_block = _build_help_block_text(gender)
    hints = _build_after_task_hint()
    return f"{header}\n{help_block}\n\n{hints}"


async def compose_after_task_message_from_state(state: FSMContext) -> str:
    """
    То же, но пол берём из FSM: gender | student_gender | user_gender | sex | pol.
    """
    data = await state.get_data()
    gender_raw = (
        data.get("gender")
        or data.get("student_gender")
        or data.get("user_gender")
        or data.get("sex")
        or data.get("pol")
    )
    gender = _normalize_gender(gender_raw)
    return compose_after_task_message(gender)


async def compose_help_block_from_state(state: FSMContext) -> str:
    """
    Возвращает ТОЛЬКО верхний блок (2 строки) с учётом пола из FSM:
    — приглашение к самостоятельному решению (без слова «Готово»),
    — мягкая подсказка про кнопку «Помощь».
    """
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
    """
    Возвращает НИЖНИЕ рандомные подсказки к кнопкам:
    — либо готовую связку,
    — либо склейку из фраз для «📚 Теория».
    """
    return _build_after_task_hint(use_combined_prob)


# ──────────────────────────────────────────────────────────────────────────────
# КЛАВИАТУРЫ ДЛЯ ЗАДАНИЙ
# ──────────────────────────────────────────────────────────────────────────────

def get_after_task_keyboard(
    task_number: int,
    task_subtype: str,
    show_help: bool = True,
) -> InlineKeyboardMarkup:
    """
    Универсальная клавиатура для задания после выдачи условия.

    Args:
        task_number: Номер задания (для обратного перехода и неймспейса колбэков).
        task_subtype: Текущий подтип задания.
        show_help: Добавлять ли кнопку «🆘 Помощь».
    """
    builder = InlineKeyboardBuilder()

    first_row: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text="💫 Назад",
            callback_data=f"back_to_carousel_{task_number}",
        )
    ]

    if show_help:
        first_row.append(
            InlineKeyboardButton(
                text="🆘 Помощь",
                callback_data=TaskCallback(
                    action="request_help",
                    subtype_key=task_subtype,
                    task_type=task_number,
                    question_num=task_number,
                ).pack(),
            )
        )

    first_row.append(
        InlineKeyboardButton(
            text="📚 Теория",
            callback_data=f"task{task_number}_theory",
        )
    )

    builder.row(*first_row)

    row_buttons = [
        InlineKeyboardButton(
            text="🎯 Другое задание",
            callback_data=TaskCallback(
                action=f"{task_number}_select_theme",
                task_type=task_number,
                subtype_key=task_subtype
            ).pack(),
        )
    ]

    for row in main_only_kb().inline_keyboard:
        row_buttons.extend(row)

    builder.row(*row_buttons)

    return builder.as_markup()


def get_task_completed_keyboard(
    task_number: int,
    task_subtype: str,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🎯 Другое задание",
            callback_data=TaskCallback(
                action=f"{task_number}_select_theme",
                task_type=task_number,
                subtype_key=task_subtype
            ).pack(),
        )
    )
    for row in main_only_kb().inline_keyboard:
        builder.row(*row)
    return builder.as_markup()


# ──────────────────────────────────────────────────────────────────────────────
# СОВМЕСТИМОСТЬ СО СТАРОЙ ЛОГИКОЙ (ДО ПОЛНОЙ МИГРАЦИИ)
# ──────────────────────────────────────────────────────────────────────────────

def get_task_11_completed_keyboard(
    task_subtype: str = "match_signs_a_c",
) -> InlineKeyboardMarkup:
    """
    Обёртка для обратной совместимости с кодом задания 11.
    """
    return get_task_completed_keyboard(task_number=11, task_subtype=task_subtype)


def _build_legacy_after_task_keyboard() -> InlineKeyboardMarkup:
    """
    Исторический вариант клавиатуры (до миграции на параметризованный интерфейс).
    Используется до тех пор, пока все задания не перейдут на новую функцию.
    """
    builder = InlineKeyboardBuilder()

    builder.button(text="🤝 Помощь", callback_data="ask_help")
    builder.button(text="📚 Теория", callback_data="show_theory")
    builder.button(text="⏱ На время", callback_data="answer_timer")
    builder.button(text="🧩 Похожее", callback_data="similar_task")
    builder.button(text="🔄 Новое задание", callback_data="back_to_task_type")
    builder.button(text="🏠 В главное меню", callback_data="back_to_main")

    builder.adjust(3, 2, 1)
    return builder.as_markup()


# Временный экспорт для старого кода.
after_task_keyboard: InlineKeyboardMarkup = _build_legacy_after_task_keyboard()


__all__ = [
    "compose_after_task_message",
    "compose_after_task_message_from_state",
    "compose_help_block_from_state",
    "compose_hint_block",
    "after_task_keyboard",
    "get_after_task_keyboard",
    "get_task_completed_keyboard",
    "get_task_11_completed_keyboard",
]
