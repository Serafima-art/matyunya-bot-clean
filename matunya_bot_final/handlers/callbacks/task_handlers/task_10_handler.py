from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

# Импортируем наши обновленные клавиатуры и тексты
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_10_keyboard import (
    get_task_10_carousel_keyboard,
    get_task_10_subtype_carousel_keyboard # Наша новая клавиатура!
)
# Импортируем клавиатуру "После задания"
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    compose_help_block_from_state,  # верхний блок (2 строки)
    compose_hint_block,             # нижние подсказки к 📚 и ⏱
)

# Импортируем наш "мозг" - Навигатор
from matunya_bot_final.handlers.callbacks.navigators.task_10_navigator import pick_random_by_theme, title_for

# Импортируем нашу "Фабрику"
from matunya_bot_final.gpt.task_generators.task_10.task_10_generator import generate_task_10, TaskGenerationError

router = Router()

# =================================================================
# УРОВЕНЬ 1: Пользователь выбрал тему (classic/stats/random)
# =================================================================
@router.callback_query(F.data.startswith("task:10:theme:"))
async def show_theme_overview_and_start_carousel(callback: types.CallbackQuery, state: FSMContext):
    """
    Ловит выбор темы и СРАЗУ запускает первый показ "карусели".
    """
    await callback.answer()
    theme_key = callback.data.split(":")[-1]

    # Сохраняем выбранную тему в "память" (FSM)
    await state.update_data(t10_theme=theme_key)

    # Запускаем "карусель"
    await start_carousel(callback, state, theme_key)

# =================================================================
# УРОВЕНЬ 2: Логика "Карусели"
# =================================================================
async def start_carousel(callback: types.CallbackQuery, state: FSMContext, theme_key: str):
    """
    Показывает один "слайд" карусели.
    Версия 4.0: с именем, полом и подсказками.
    """
    # 1. Выбираем случайный подтип
    subtype_key = pick_random_by_theme(theme_key)
    if not subtype_key:
        await callback.answer("В этой категории пока нет заданий.", show_alert=True)
        return

    # 2. Получаем данные ученика из FSM
    user_data = await state.get_data()
    gender = user_data.get("gender")
    student_name = user_data.get("student_name", "Чемпион") # Если имени нет, зовем "Чемпион"

    # 3. Определяем правильное обращение по полу
    readiness_word = "Готов(а)"
    if gender == "девочка":
        readiness_word = "Готова"
    elif gender == "мальчик":
        readiness_word = "Готов"

    # 4. Формируем новый, подробный текст "слайда"
    text = (f"🎲 Случайная тема для тебя:\n"
            f"<b>{title_for(subtype_key)}</b>\n\n"
            f"{student_name}, {readiness_word.lower()} к этой теме?\n"
            f"▶️ <b>Открыть задание</b> — чтобы начать решать.\n"
            f"🎲 <b>Ещё вариант</b> — чтобы я подобрал другую тему.")
    
    # 5. Получаем клавиатуру
    keyboard = get_task_10_subtype_carousel_keyboard(subtype_key)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "task:10:reroll")
async def reroll_carousel(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик для кнопки "🎲 Ещё вариант"."""
    user_data = await state.get_data()
    theme_key = user_data.get("t10_theme")
    
    if not theme_key:
        await callback.answer("Что-то пошло не так, попробуйте заново.", show_alert=True)
        return
        
    # Просто запускаем карусель заново с сохраненной темой
    await start_carousel(callback, state, theme_key)

# =================================================================
# УРОВЕНЬ 3: Финальный запуск генерации задания
# =================================================================
@router.callback_query(F.data.startswith("task:10:run:"))
async def run_task_10_generation(callback: types.CallbackQuery, state: FSMContext):
    """
    Ловит нажатие на "▶️ Открыть задание" и работает по "Эталонному скелету".
    """
    await callback.answer() # Пункт 6. Убираем часики
    subtype_id = callback.data.split(":")[-1]

    loading_message = await callback.message.edit_text("Минутку, генерирую для тебя уникальную задачку... 🧠")
    
    try:
        # Пункт 1. Получаем данные
        generated_task = await generate_task_10(subtype_id)
        task_text = generated_task['text']
        task_answer = generated_task['answer']
        task_type = "10"

        # Пункт 2. Показываем условие
        await loading_message.delete()
        await callback.message.answer(f"📘 <b>Задание {task_type}:</b>\n\n{task_text}", parse_mode="HTML")

        # Пункт 3. Мягкий сброс помощи
        await state.update_data(
            help_on=False, help_step=1, last_hint_level=0, 
            last_user_text="", dialog_history=[] # Добавлен last_user_text=""
        )

        # Пункт 4. Сохраняем данные в FSM
        await state.update_data(
            task_type=task_type,
            task_text=task_text,
            correct_answers=[str(task_answer)] if task_answer is not None else [],
            subtype_key=subtype_id,
        )

        # Пункт 5. Отправляем клавиатуру после задания
        # 1) Верхний блок
        help_block = await compose_help_block_from_state(state)
        await callback.message.answer(f"🎯 Твой ход!\n{help_block}", parse_mode="HTML")

        # 2) Нижний блок + клавиатура
        hint_text = compose_hint_block()
        await callback.message.answer(
            hint_text,
            parse_mode="HTML",
            reply_markup=get_after_task_keyboard(
                task_number=10,
                task_subtype=subtype_id,
                show_help=False,
            ),
        )

        # Не забываем ответить на callback, чтобы убрать "часики"
        await callback.answer()

    except (TaskGenerationError, Exception) as e:
        print(f"Ошибка при генерации Задания 10 ({subtype_id}): {e}")
        await loading_message.edit_text("Ой, что-то пошло не так... 🛠️ Попробуй, пожалуйста, еще раз.",
                                        reply_markup=get_task_10_carousel_keyboard())
