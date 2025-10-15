from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем клавиатуру с одной кнопкой для пропуска знакомства
skip_onboarding_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Можно без имени ➡️",
            callback_data="skip_onboarding"
        )
    ]
])