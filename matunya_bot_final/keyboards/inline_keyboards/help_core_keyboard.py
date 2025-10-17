"""
help_core_keyboard.py
=====================

Универсальная клавиатура для окна "Помощь" 🆘

Отображается после вывода полного решения задачи:
кнопки ❌ «Закрыть помощь» и ❓ «Задать вопрос».

Используется всеми help_handler_X.py (для заданий 1–25).
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback


def create_solution_keyboard(task_subtype: str, task_type: int) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для окна помощи.

    Кнопки:
    - ❌ Закрыть помощь
    - ❓ Задать вопрос
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="❌ Закрыть помощь",
            callback_data=TaskCallback(
                action="hide_help",
                subtype_key=task_subtype,
                question_num=task_type
            ).pack()
        ),
        InlineKeyboardButton(
            text="❓ Задать вопрос",
            callback_data=TaskCallback(
                action="ask_question",
                subtype_key=task_subtype,
                question_num=task_type
            ).pack()
        )
    )

    return builder.as_markup()


__all__ = ["create_solution_keyboard"]
