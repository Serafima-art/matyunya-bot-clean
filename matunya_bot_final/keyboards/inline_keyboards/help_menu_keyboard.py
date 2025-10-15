from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

help_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💡 Как пользоваться ботом",
                callback_data="help_how_to_use"
            ),
            InlineKeyboardButton(
                text="🧭 Как проходит обучение",
                callback_data="help_how_it_works"
            )
        ],
        [
            InlineKeyboardButton(
                text="📲 Связь с живым репетитором",
                callback_data="help_contact_teacher"
            )
        ],
        [
            InlineKeyboardButton(
                text="📤 Загрузить своё задание",
                callback_data="upload_custom_task"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_main"
            )
        ]
    ]
)