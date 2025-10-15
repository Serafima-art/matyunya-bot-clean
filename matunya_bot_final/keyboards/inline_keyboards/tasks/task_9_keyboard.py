from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

"""
Этот модуль отвечает за создание клавиатуры для выбора подтем в Задании 9.
"""

# =================================================================
# Карта тем для Задания 9
# Связывает официальные темы ОГЭ с ключами подтипов из task_9_generator.py
# =================================================================
TASK_9_STRUCTURE = {
    "linear": {
        "title": "Линейные уравнения",
        "subtypes": [
            "linear_equation_integer",
            "linear_equation_fractional",
            "square_equals_square",
            "expressions_equal",
        ]
    },
    "quadratic": {
        "title": "Квадратные уравнения",
        "subtypes": [
            "quadratic_equation_all_roots",
            "quadratic_equation_bigger_root_integer",
            "quadratic_equation_bigger_root_fractional",
            "quadratic_equation_smaller_root_integer",
            "quadratic_equation_smaller_root_fractional",
            "product_of_factors_all_roots",
            "product_of_factors_bigger_root",
            "product_of_factors_smaller_root",
            "difference_of_squares",
            "quadratic_both_sides_smaller_root_integer",
            "given_roots_find",
            "factorized_quadratic",
        ]
    },
    "rational": {
        "title": "Рациональные уравнения",
        "subtypes": [
            "linear_equation_rational",
        ]
    },
    "systems": {
        "title": "Системы уравнений",
        "subtypes": [
            "system_sum",
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
def get_task_9_themes_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками-номерами для выбора темы Задания 9.
    """
    theme_buttons = []
    for i, theme_key in enumerate(TASK_9_STRUCTURE.keys(), 1):
        emoji = THEME_EMOJIS[i-1]
        button = InlineKeyboardButton(
            text=f"{emoji} {i}",
            callback_data=f"task:9:select_theme:{theme_key}"
        )
        theme_buttons.append(button)

    service_buttons = [
        InlineKeyboardButton(
            text="🎲 Случайная тема",
            callback_data="task:9:select_theme:random"
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