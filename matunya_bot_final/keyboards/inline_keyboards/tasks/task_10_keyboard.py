from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Импортируем наш новый "мозг" - Навигатор
from matunya_bot_final.handlers.callbacks.navigators.task_10_navigator import get_subtypes_by_theme

# =================================================================
# "Мозг" и "Лицо" для Задания 10 (Версия "Карусель")
# =================================================================

# "Мозг": Карта ОСНОВНЫХ тем. Подтипы теперь живут в Навигаторе.
TASK_10_STRUCTURE = {
    "classic": {"name": "Классические вероятности", "emoji": "📘"},
    "stats": {"name": "Статистика и теоремы", "emoji": "📗"}
}
THEME_EMOJIS = ['📘', '📗']

# Лицо №1: Клавиатура для выбора ГЛАВНОЙ темы (остается почти без изменений)
def get_task_10_themes_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора основной темы в Задании 10."""
    builder = InlineKeyboardBuilder()
    for i, (theme_key, theme_data) in enumerate(TASK_10_STRUCTURE.items(), 1):
        builder.button(text=f"{theme_data['emoji']} {i}", callback_data=f"task:10:theme:{theme_key}")
    
    builder.button(text="🎲 Случайная тема", callback_data="task:10:theme:random")
    builder.button(text="🔝 В главное меню", callback_data="to_main_menu")
    builder.adjust(2, 2)
    return builder.as_markup()

# Лицо №2: НОВАЯ клавиатура для "Карусели"
def get_task_10_carousel_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для "карусели":
    [ Вариант темы ] [ Назад к темам ]
    [      В главное меню      ]
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="✨ Вариант темы", callback_data="task:10:reroll")
    builder.button(text="🔙 Назад к темам", callback_data="gpt:task:10") # Возврат в navigation_handler
    builder.button(text="🔝 В главное меню", callback_data="to_main_menu")
    builder.adjust(2, 1)
    return builder.as_markup()

# =================================================================
# Лицо №3: НОВАЯ клавиатура для ЭКРАНА "КАРУСЕЛИ"
# =================================================================
def get_task_10_subtype_carousel_keyboard(subtype_key: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для экрана "карусели подтипов":
    [ Открыть задание ] [ Ещё вариант ]
    [ Назад к темам ]   [ В главное меню ]
    """
    builder = InlineKeyboardBuilder()
    
    # Ряд 1
    builder.button(text="▶️ Открыть задание", callback_data=f"task:10:run:{subtype_key}")
    builder.button(text="🎲 Ещё вариант", callback_data="task:10:reroll")
    
    # Ряд 2
    builder.button(text="🔙 Назад к темам", callback_data="gpt:task:10")
    builder.button(text="🔝 В главное меню", callback_data="to_main_menu")
    
    builder.adjust(2, 2) # Расставляем: 2 кнопки в первом ряду, 2 во втором
    return builder.as_markup()

# Текстовая "Карта" №1: Для выбора темы (без изменений)
def get_task_10_themes_text() -> str:
    """Возвращает форматированный текст со списком основных тем."""
    text = "<b>Задание 10: Теория вероятностей</b>\n\n"
    text += "Выбери тему, которую хочешь потренировать:\n\n"
    for i, (theme_key, theme_data) in enumerate(TASK_10_STRUCTURE.items(), 1):
        text += f"{theme_data['emoji']} {i}. {theme_data['name']}\n"
    return text