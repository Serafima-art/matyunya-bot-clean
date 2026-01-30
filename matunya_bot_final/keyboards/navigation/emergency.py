# matunya_bot_final/keyboards/navigation/emergency.py
# -*- coding: utf-8 -*-

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

__all__ = (
    "emergency_nav_kb",
)

def emergency_nav_kb(
    back_text: str = "🔙 Назад",
) -> InlineKeyboardMarkup:
    """
    Аварийная навигационная клавиатура.

    Используется при сбоях в Help / Solver:
    - 🔙 Назад — восстановить карусель задания
    - 🏠 В главное меню — полный выход из сценария

    ⚠️ Callback'и намеренно строковые и фиксированные.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=back_text,
                callback_data="restore_task_keyboard"
            ),
            InlineKeyboardButton(
                text="🏠 В главное меню",
                callback_data="back_to_main_menu"
            ),
        ]
    ])
