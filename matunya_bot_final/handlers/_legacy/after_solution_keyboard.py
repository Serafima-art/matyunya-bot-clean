from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def _build_after_solution_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    # 1-й ряд
    kb.row(
        InlineKeyboardButton(text="🧩 Похожее задание", callback_data="similar_task"),
        InlineKeyboardButton(text="📚 Теория",            callback_data="open_theory"),
    )

    # 2-й ряд
    kb.row(
        InlineKeyboardButton(text="🔙 Назад к темам",     callback_data="back_to_topics"),
        InlineKeyboardButton(text="🏠 В главное меню",    callback_data="back_to_main"),
    )

    return kb.as_markup()

after_solution_keyboard: InlineKeyboardMarkup = _build_after_solution_keyboard()