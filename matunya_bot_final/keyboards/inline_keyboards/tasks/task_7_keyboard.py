# keyboards/inline_keyboards/task_7_keyboard.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

"""
Этот модуль отвечает за создание клавиатуры для выбора подтем в Задании 7.
"""

# =================================================================
# Карта тем для Задания 7
# Связывает официальные темы ОГЭ с ключами подтипов из task_7_prompts.py
# =================================================================
TASK_7_STRUCTURE = {
    "inequalities": {
        "title": "Неравенства",
        "subtypes": [
            "root_in_integer_interval",
            "fraction_in_decimal_interval",
            "number_in_set",
        ]
    },
    "number_comparison": {
        "title": "Сравнение чисел",
        "subtypes": [
            "decimal_between_fractions",
            "integer_between_roots",
        ]
    },
    "numbers_on_line": {
        "title": "Числа на прямой",
        "subtypes": [
            "point_to_root",
            "point_to_fraction_decimal",
            "root_to_point",
            "point_to_fraction",
            "decimal_to_point",
        ]
    },
    "statement_choice": {
        "title": "Выбор верного или неверного утверждения",
        "subtypes": [
            "variable_on_line",
            "expression_analysis_on_line",
            "difference_analysis_on_line",
        ]
    }
}

# =================================================================
# Эмодзи для тем
# =================================================================
THEME_EMOJIS = ['📘', '📗', '📙', '📒', '📕', '📔']

# =================================================================
# Функция для создания клавиатуры выбора тем
# =================================================================
def get_task_7_themes_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками-номерами для выбора темы Задания 7.
    """
    theme_buttons = []
    for i, theme_key in enumerate(TASK_7_STRUCTURE.keys(), 1):
        emoji = THEME_EMOJIS[i-1]
        button = InlineKeyboardButton(
            text=f"{emoji} {i}",
            callback_data=f"task:7:select_theme:{theme_key}"
        )
        theme_buttons.append(button)

    service_buttons = [
        InlineKeyboardButton(
            text="🎲 Случайная тема",
            callback_data="task:7:select_theme:random"
        ),
        InlineKeyboardButton(
            text="🔝 В главное меню",
            callback_data="to_main_menu"
        )
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        theme_buttons,
        service_buttons
    ])
    
    return keyboard