from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

# Импорт карты навигации из отдельного файла
from .TASK_12_MAP import TASK_12_MAP

# =================================================================
# Префикс для callback_data
# =================================================================
T12_PREFIX = "t12"

# =================================================================
# Текст приветствия
# =================================================================
def task12_intro_text() -> str:
    return (
        "Задание 12: Расчёты по формулам\n\n"
        "Выбери тему, которую хочешь потренировать:\n\n"
        "1. 📘 Вычисление по формуле\n"
        "2. 📗 Линейные уравнения\n"
        "3. 📙 Разные задачи"
    )

# =================================================================
# Главное меню (первый уровень)
# =================================================================
def task12_menu() -> InlineKeyboardMarkup:
    """Главное меню выбора категории задач"""
    kb = InlineKeyboardBuilder()
    kb.button(text="1", callback_data=f"{T12_PREFIX}:cat:1")
    kb.button(text="2", callback_data=f"{T12_PREFIX}:cat:2")
    kb.button(text="3", callback_data=f"{T12_PREFIX}:cat:3")
    kb.button(text="🎲 Случайная тема", callback_data=f"{T12_PREFIX}:random")
    kb.button(text="🔝 В главное меню", callback_data="back_to_main")
    kb.adjust(3, 2)
    return kb.as_markup()

# =================================================================
# Меню категории 1: Вычисление по формуле
# =================================================================
def task12_cat1_menu() -> InlineKeyboardMarkup:
    """
    12.1 «Вычисление по формуле».
    Выбор между геометрией и физикой.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🧭 Геометрия", callback_data=f"{T12_PREFIX}:cat:1:geometry")
    kb.button(text="⚙️ Физика", callback_data=f"{T12_PREFIX}:cat:1:physics")
    kb.button(text="🎲 Случайная тема", callback_data=f"{T12_PREFIX}:cat:1:random")
    kb.button(text="🔙 Назад", callback_data=f"{T12_PREFIX}:menu")
    kb.button(text="🔝 В главное меню", callback_data="back_to_main")
    kb.adjust(2, 1, 2)
    return kb.as_markup()

# =================================================================
# Меню категории 2: Линейные уравнения
# =================================================================
def task12_cat2_menu() -> InlineKeyboardMarkup:
    """
    12.2 «Линейные уравнения».
    Выбор между геометрией и физикой.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🧭 Геометрия", callback_data=f"{T12_PREFIX}:cat:2:geometry")
    kb.button(text="⚙️ Физика", callback_data=f"{T12_PREFIX}:cat:2:physics")
    kb.button(text="🎲 Случайная тема", callback_data=f"{T12_PREFIX}:cat:2:random")
    kb.button(text="🔙 Назад", callback_data=f"{T12_PREFIX}:menu")
    kb.button(text="🔝 В главное меню", callback_data="back_to_main")
    kb.adjust(2, 1, 2)
    return kb.as_markup()

# =================================================================
# Меню категории 3: Разные задачи
# =================================================================
def task12_cat3_menu() -> InlineKeyboardMarkup:
    """
    12.3 «Разные задачи».
    У этой категории нет подкategorий, сразу генерируем задачу.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🎯 Начать решать", callback_data=f"{T12_PREFIX}:cat:3:start")
    kb.button(text="🔙 Назад", callback_data=f"{T12_PREFIX}:menu")
    kb.button(text="🔝 В главное меню", callback_data="back_to_main")
    kb.adjust(1, 2)
    return kb.as_markup()

# =================================================================
# Вспомогательные функции для работы с картой
# =================================================================
def get_random_subtype_from_category(category: str, subcategory: str = None) -> str:
    """
    Возвращает случайный subtype_key из указанной категории.
    
    Args:
        category: "calculations", "equations", или "misc"
        subcategory: "geometry" или "physics" (только для calculations/equations)
    
    Returns:
        Случайный subtype_key
    """
    import random
    
    if category == "misc":
        return random.choice(TASK_12_MAP["misc"])
    
    if subcategory and subcategory in TASK_12_MAP[category]:
        return random.choice(TASK_12_MAP[category][subcategory])
    
    # Если subcategory не указан, берем из всех подкategorий
    all_subtypes = []
    for subcat_list in TASK_12_MAP[category].values():
        all_subtypes.extend(subcat_list)
    return random.choice(all_subtypes)

def get_all_subtypes() -> list:
    """Возвращает список всех доступных subtype_key"""
    all_subtypes = []
    
    # Добавляем из calculations
    for subcat_list in TASK_12_MAP["calculations"].values():
        all_subtypes.extend(subcat_list)
    
    # Добавляем из equations  
    for subcat_list in TASK_12_MAP["equations"].values():
        all_subtypes.extend(subcat_list)
    
    # Добавляем из misc
    all_subtypes.extend(TASK_12_MAP["misc"])
    
    return all_subtypes