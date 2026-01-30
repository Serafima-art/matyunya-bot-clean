from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_inline_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📘 Задания от GPT", callback_data="menu_gpt_tasks")],
    [InlineKeyboardButton(text="📤 Загрузить своё задание", callback_data="menu_upload_task")],
    [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="menu_progress")],
    [InlineKeyboardButton(text="📖 Как пользоваться", callback_data="menu_help")],
])
