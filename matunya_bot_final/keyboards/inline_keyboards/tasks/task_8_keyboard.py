from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

"""
Этот модуль отвечает за создание клавиатуры для выбора подтем в Задании 8.
Главный элемент - словарь TASK_8_STRUCTURE, который является "картой",
связывающей официальные темы ОГЭ с ключами подтипов из generator.py.
"""

# =================================================================
# Карта тем для Задания 8 (СИНХРОНИЗИРОВАННАЯ ВЕРСИЯ)
# =================================================================
TASK_8_STRUCTURE = {
    "integer_expressions": {
        "title": "Целые алгебраические выражения",
        "subtypes": [
            "difference_of_squares_with_roots"  
        ]
    },
    "rational_expressions": {
        "title": "Рациональные алгебраические выражения",
        "subtypes": [
            "fraction_with_powers",  
            "fraction_with_powers_and_substitution",
            "root_of_fraction_with_powers",
            "powered_fraction_with_root_denominator"
        ]
    },
    "powers_and_roots": {
        "title": "Степени и корни",
        "subtypes": [
            "same_base",
            "root_fraction_variable_power",
            "expression_with_radicals_and_powers",
            "expressions_with_powers",  
            "multiplication_of_roots",
            "powers_with_variables_and_substitution",
            "product_and_division_of_roots_with_variables",
            "power_of_product_and_division",  
            "powers_in_fraction_with_products",  
            "product_of_roots_divided_by_root",
            "negative_exponents",
            "multiplication_of_roots_and_numbers"
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
def get_task_8_themes_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками-номерами для выбора темы Задания 8,
    а также кнопки "Случайная тема" и "В главное меню".
    """
    # --- Ряд 1: Кнопки с номерами тем ---
    theme_buttons = []
    # enumerate(..., 1) начнет нумерацию с 1
    for i, theme_key in enumerate(TASK_8_STRUCTURE.keys(), 1):
        # Берем эмодзи по порядку. Если тем будет больше, чем эмодзи,
        # программа выдаст ошибку, что хорошо - это напомнит нам добавить новые.
        emoji = THEME_EMOJIS[i-1]
        
        button = InlineKeyboardButton(
            text=f"{emoji} {i}",
            callback_data=f"task:8:select_theme:{theme_key}"
        )
        theme_buttons.append(button)

    # --- Ряд 2: Служебные кнопки ---
    service_buttons = [
        InlineKeyboardButton(
            text="🎲 Случайная тема",
            callback_data="task:8:select_theme:random"
        ),
        InlineKeyboardButton(
            text="🔝 В главное меню",
            callback_data="to_main_menu"
        )
    ]

    # --- Собираем клавиатуру ---
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        theme_buttons,
        service_buttons
    ])
    
    return keyboard