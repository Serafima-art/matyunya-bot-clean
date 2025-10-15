from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

gender_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="👧 Девочка", callback_data="gender_female"),
        InlineKeyboardButton(text="👦 Мальчик", callback_data="gender_male")
    ]
])