from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

answer_mode_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⏱ На время", callback_data="answer_timer")],
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")]
    ]
)