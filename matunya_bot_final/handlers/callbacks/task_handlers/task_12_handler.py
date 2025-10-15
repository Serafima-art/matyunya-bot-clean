import random
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from matunya_bot_final.loader import TASKS_DB
from matunya_bot_final.states.states import TaskState
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import get_after_task_keyboard
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_12.task_12_keyboard import (
    task12_intro_text,
    task12_menu,
    task12_cat1_menu,
    task12_cat2_menu,
    task12_cat3_menu
)
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback

router = Router()

# =================================================================
# Маппинг категорий: callback_data -> category в БД
# =================================================================
CATEGORY_MAPPING = {
    "1": "calculations",    # Расчёты по формулам
    "2": "equations",       # Линейные уравнения  
    "3": "misc"            # Разные задачи
}

SUBCATEGORY_MAPPING = {
    "geometry": "geometry",
    "physics": "physics"
}

# =================================================================
# 1. Главное меню Задания 12 (первый вход)
# =================================================================
@router.callback_query(
    TaskCallback.filter((F.action == "select_task") & (F.task_type == 12))
)
async def show_task_12_main_menu(callback: CallbackQuery, state: FSMContext, callback_data: TaskCallback):
    """Показать главное меню выбора категории для Задания 12"""
    await callback.message.edit_text(
        text=task12_intro_text(),
        reply_markup=task12_menu()
    )
    await callback.answer()

# =================================================================
# 2. Выбор категории (кнопки 1, 2, 3)
# =================================================================
@router.callback_query(F.data.startswith("t12:cat:"))
async def handle_category_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории (1, 2, 3)"""
    print(f"ОБРАБАТЫВАЕМ КАТЕГОРИЮ: {callback.data}")
    
    # Парсим callback_data: t12:cat:1 или t12:cat:1:geometry и т.д.
    parts = callback.data.split(":")
    category_num = parts[2]  # "1", "2", "3"
    
    print(f"НОМЕР КАТЕГОРИИ: {category_num}, ВСЕГО ЧАСТЕЙ: {len(parts)}")
    
    # Если есть 4-я часть - это подкатегория или действие
    if len(parts) >= 4:
        action_or_subcat = parts[3]
        print(f"ДЕЙСТВИЕ/ПОДКАТЕГОРИЯ: {action_or_subcat}")
        
        # Обработка подкатегорий для категорий 1 и 2
        if category_num in ["1", "2"] and action_or_subcat in ["geometry", "physics"]:
            await handle_subcategory_selection(callback, state, category_num, action_or_subcat)
            return
        
        # Обработка случайного выбора
        if action_or_subcat == "random":
            await generate_random_task_from_category(callback, state, category_num)
            return
            
        # Обработка категории 3 (разные задачи)
        if category_num == "3" and action_or_subcat == "start":
            await generate_random_task_from_category(callback, state, category_num)
            return
    
    # Показываем меню подкатегорий
    print(f"ПОКАЗЫВАЕМ МЕНЮ ДЛЯ КАТЕГОРИИ: {category_num}")
    if category_num == "1":
        await callback.message.edit_text(
            text="📘 Расчёты по формулам\n\nВыбери область:",
            reply_markup=task12_cat1_menu()
        )
    elif category_num == "2":
        await callback.message.edit_text(
            text="📗 Линейные уравнения\n\nВыбери область:",
            reply_markup=task12_cat2_menu()
        )
    elif category_num == "3":
        await callback.message.edit_text(
            text="📙 Разные задачи\n\nЖизненные задачи на применение формул:",
            reply_markup=task12_cat3_menu()
        )
    
    await callback.answer()

# =================================================================
# 3. Возврат в главное меню задания 12
# =================================================================
@router.callback_query(F.data == "t12:menu")
async def back_to_task_12_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню Задания 12"""
    await callback.message.edit_text(
        text=task12_intro_text(),
        reply_markup=task12_menu()
    )
    await callback.answer()

# =================================================================
# 4. Обработка случайной задачи из всех категорий
# =================================================================
@router.callback_query(F.data == "t12:random")
async def handle_random_task(callback: CallbackQuery, state: FSMContext):
    """Выдача случайной задачи из всех категорий Задания 12"""
    tasks_12 = TASKS_DB.get("12", [])
    
    if not tasks_12:
        await callback.message.edit_text("Задачи не найдены.")
        await callback.answer()
        return
    
    # Выбираем случайную задачу
    task = random.choice(tasks_12)
    
    # Сохраняем в FSM для полностью случайного выбора
    await state.update_data(
        current_task_id=task["id"],
        current_task_answer=task["answer"], 
        current_task_full_object=task,
        theme_key="random",
        sub_theme_key=None,
        category=task.get("category"),
        subcategory=task.get("subcategory")
    )
    
    # Отправляем задачу
    await callback.message.edit_text(
        text=f"🎲 Случайная задача:\n\n{task['text']}",
        reply_markup=get_after_task_keyboard(
            task_number=12,
            task_subtype=task.get("subcategory") or task.get("category") or "random",
            show_help=False,
        )
    )
    
    # Переводим в состояние ожидания ответа
    await state.set_state(TaskState.waiting_for_answer)
    await callback.answer()

# =================================================================
# 5. Обработка подкатегорий (геометрия/физика)
# =================================================================
async def handle_subcategory_selection(callback: CallbackQuery, state: FSMContext, category_num: str, subcategory: str):
    """Обработка выбора подкатегории (геометрия/физика)"""
    category = CATEGORY_MAPPING[category_num]
    subcategory_mapped = SUBCATEGORY_MAPPING[subcategory]
    
    # Фильтруем задачи
    filtered_tasks = filter_tasks_by_category(category, subcategory_mapped)
    
    if not filtered_tasks:
        await callback.message.edit_text("Задачи для данной категории не найдены.")
        await callback.answer()
        return
    
    # Выбираем случайную задачу
    task = random.choice(filtered_tasks)
    
    # Сохраняем в FSM
    await state.update_data(
        current_task_id=task["id"],
        current_task_answer=task["answer"],
        current_task_full_object=task,
        theme_key=category,
        sub_theme_key=subcategory_mapped,
        category=category,
        subcategory=subcategory_mapped
    )
    
    # Отправляем задачу
    emoji_map = {"geometry": "🧭", "physics": "⚙️"}
    emoji = emoji_map.get(subcategory, "📘")
    
    await callback.message.edit_text(
        text=f"{emoji} {subcategory.title()}:\n\n{task['text']}",
        reply_markup=get_after_task_keyboard(
            task_number=12,
            task_subtype=subcategory_mapped,
            show_help=False,
        )
    )
    
    # Переводим в состояние ожидания ответа
    await state.set_state(TaskState.waiting_for_answer)
    await callback.answer()

# =================================================================
# 6. Генерация случайной задачи из категории
# =================================================================
async def generate_random_task_from_category(callback: CallbackQuery, state: FSMContext, category_num: str):
    """Генерация случайной задачи из указанной категории"""
    category = CATEGORY_MAPPING[category_num]
    
    # Для категории "misc" подкатегорий нет
    if category == "misc":
        filtered_tasks = filter_tasks_by_category(category)
    else:
        # Для categories 1 и 2 берем все подкатегории
        filtered_tasks = filter_tasks_by_category(category)
    
    if not filtered_tasks:
        await callback.message.edit_text("Задачи для данной категории не найдены.")
        await callback.answer()
        return
    
    # Выбираем случайную задачу
    task = random.choice(filtered_tasks)
    
    # Сохраняем в FSM
    await state.update_data(
        current_task_id=task["id"],
        current_task_answer=task["answer"],
        current_task_full_object=task,
        theme_key=category,
        sub_theme_key=None,  # Случайная из всей категории
        category=category,
        subcategory=task.get("subcategory")
    )
    
    # Отправляем задачу
    category_names = {
        "calculations": "📘 Расчёты по формулам",
        "equations": "📗 Линейные уравнения", 
        "misc": "📙 Разные задачи"
    }
    category_name = category_names.get(category, "📘 Задание 12")
    
    await callback.message.edit_text(
        text=f"🎲 {category_name}:\n\n{task['text']}",
        reply_markup=get_after_task_keyboard(
            task_number=12,
            task_subtype=task.get("subcategory") or category,
            show_help=False,
        )
    )
    
    # Переводим в состояние ожидания ответа
    await state.set_state(TaskState.waiting_for_answer)
    await callback.answer()

# =================================================================
# 7. Кнопка "Еще вариант" (reroll)
# =================================================================
@router.callback_query(F.data == "task_reroll", TaskState.waiting_for_answer)
async def handle_task_reroll(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Еще вариант' - новая задача из той же категории"""
    data = await state.get_data()
    
    # Получаем текущие параметры выбора
    theme_key = data.get("theme_key")
    sub_theme_key = data.get("sub_theme_key")
    current_task_id = data.get("current_task_id")
    
    if not theme_key:
        await callback.answer("Ошибка: не удалось определить категорию задачи")
        return
    
    # Фильтруем задачи согласно сохраненным параметрам
    if theme_key == "random":
        # Полностью случайный выбор из всех задач
        tasks_12 = TASKS_DB.get("12", [])
        filtered_tasks = tasks_12
    elif sub_theme_key:
        # Конкретная подкатегория
        filtered_tasks = filter_tasks_by_category(theme_key, sub_theme_key)
    else:
        # Вся категория
        filtered_tasks = filter_tasks_by_category(theme_key)
    
    if not filtered_tasks:
        await callback.answer("Больше задач в этой категории нет")
        return
    
    # Исключаем текущую задачу, если есть другие варианты
    if len(filtered_tasks) > 1:
        filtered_tasks = [t for t in filtered_tasks if t["id"] != current_task_id]
    
    # Выбираем новую задачу
    new_task = random.choice(filtered_tasks)
    
    # Обновляем FSM
    await state.update_data(
        current_task_id=new_task["id"],
        current_task_answer=new_task["answer"],
        current_task_full_object=new_task
    )
    
    # Формируем заголовок в зависимости от типа выбора
    if theme_key == "random":
        header = "🎲 Случайная задача:"
    elif sub_theme_key:
        emoji_map = {"geometry": "🧭", "physics": "⚙️"}
        emoji = emoji_map.get(sub_theme_key, "📘")
        header = f"{emoji} {sub_theme_key.title()}:"
    else:
        category_names = {
            "calculations": "📘 Расчёты по формулам",
            "equations": "📗 Линейные уравнения",
            "misc": "📙 Разные задачи"
        }
        header = f"🎲 {category_names.get(theme_key, 'Задание 12')}:"
    
    # Отправляем новую задачу
    await callback.message.edit_text(
        text=f"{header}\n\n{new_task['text']}",
        reply_markup=get_after_task_keyboard(
            task_number=12,
            task_subtype=sub_theme_key or theme_key or "random",
            show_help=False,
        )
    )
    
    await callback.answer("Новая задача!")

# =================================================================
# Вспомогательные функции
# =================================================================
def filter_tasks_by_category(category: str, subcategory: str = None) -> list:
    """
    Фильтрует задачи по категории и подкатегории
    
    Args:
        category: "calculations", "equations", "misc"
        subcategory: "geometry", "physics" (опционально)
    
    Returns:
        Список отфильтрованных задач
    """
    tasks_12 = TASKS_DB.get("12", [])
    
    if not tasks_12:
        return []
    
    # Фильтруем по категории
    filtered = [task for task in tasks_12 if task.get("category") == category]
    
    # Если указана подкатегория, дополнительно фильтруем
    if subcategory:
        filtered = [task for task in filtered if task.get("subcategory") == subcategory]
    
    return filtered
