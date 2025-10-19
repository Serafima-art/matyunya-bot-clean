from __future__ import annotations

from typing import Optional, Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback


TaskIdentifier = Union[int, str]


def _prepare_task_identifier(value: TaskIdentifier) -> str:
    if isinstance(value, (int, float)):
        return str(int(value))
    return str(value)


def get_help_panel_keyboard(
    task_num: TaskIdentifier,
    subtype: Optional[str] = None,
    *,
    question_num: Optional[int] = None,
) -> InlineKeyboardMarkup:
    """Build keyboard with "hide" and "ask GPT" buttons for the help panel."""
    identifier = _prepare_task_identifier(task_num)
    builder = InlineKeyboardBuilder()

    builder.button(
        text="❌ Закрыть помощь",
        callback_data=TaskCallback(
            action="dismiss_help_panel",
            question_num=question_num if question_num is not None else (int(identifier) if identifier.isdigit() else None),
            subtype_key=subtype,
        ).pack(),
    )
    builder.button(
        text="❓ Задать вопрос",
        callback_data=TaskCallback(
            action=f"{identifier}_ask_gpt",
            question_num=question_num if question_num is not None else (int(identifier) if identifier.isdigit() else None),
            subtype_key=subtype,
        ).pack(),
    )

    builder.adjust(2)
    return builder.as_markup()


def get_gpt_dialog_keyboard() -> InlineKeyboardMarkup:
    """Keyboard that controls the GPT dialogue flow."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Всё понятно, спасибо!",
            callback_data=TaskCallback(action="end_gpt_dialog").pack(),
        ),
        InlineKeyboardButton(
            text="❓ Ещё вопрос",
            callback_data=TaskCallback(action="continue_gpt_dialog").pack(),
        ),
    )
    return builder.as_markup()
