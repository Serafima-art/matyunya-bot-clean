from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

__all__ = (
    "main_only_kb",
    "back_and_main_kb",
)

# 🏠 Только «В главное меню»
def main_only_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main_menu")]
    ])

# ⬅️ «Назад» + 🏠 «В главное меню»
def back_and_main_kb(
    back_text: str = "⬅️ Назад",
    back_callback: str = "back_to_parts"   # стандарт: назад к выбору частей
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=back_text, callback_data=back_callback),
            InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main_menu"),
        ]
    ])
