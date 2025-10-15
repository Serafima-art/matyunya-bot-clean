# keyboards/inline_keyboards/tasks/task_12_keyboard.py
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

T12_PREFIX = "t12"

def task12_intro_text() -> str:
    return (
        "Задание 12: Расчёты по формулам\n\n"
        "Выбери тему, которую хочешь потренировать:\n\n"
        "1. 📘 Вычисление по формуле\n"
        "2. 📗 Линейные уравнения\n"
        "3. 📙 Разные задачи"
    )

def task12_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="1", callback_data=f"{T12_PREFIX}:cat:1")
    kb.button(text="2", callback_data=f"{T12_PREFIX}:cat:2")
    kb.button(text="3", callback_data=f"{T12_PREFIX}:cat:3")
    kb.button(text="🎲 Случайная тема", callback_data=f"{T12_PREFIX}:random")
    kb.button(text="🔝 В главное меню", callback_data="back_to_main")
    kb.adjust(3, 2)
    return kb.as_markup()

def task12_cat1_menu() -> InlineKeyboardMarkup:
    """
    12.1 «Вычисление по формуле».
    Кнопки без длинных списков: обе области ведут к рандому внутри 12.1.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🧭 Геометрия", callback_data=f"{T12_PREFIX}:cat:1:random")
    kb.button(text="⚙️ Физика",   callback_data=f"{T12_PREFIX}:cat:1:random")
    kb.button(text="🎲 Случайная тема", callback_data=f"{T12_PREFIX}:cat:1:random")
    kb.button(text="🔝 В главное меню", callback_data="back_to_main")
    kb.adjust(2, 2)
    return kb.as_markup()

def task12_cat2_menu() -> InlineKeyboardMarkup:
    """
    12.2 «Линейные уравнения».
    Кнопки без длинных списков: области ведут к рандому внутри 12.2.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🧭 Геометрия", callback_data=f"{T12_PREFIX}:cat:2:random")
    kb.button(text="⚙️ Физика",   callback_data=f"{T12_PREFIX}:cat:2:random")
    kb.button(text="🎲 Случайная тема", callback_data=f"{T12_PREFIX}:cat:2:random")
    kb.button(text="🔝 В главное меню", callback_data="back_to_main")
    kb.adjust(2, 2)
    return kb.as_markup()