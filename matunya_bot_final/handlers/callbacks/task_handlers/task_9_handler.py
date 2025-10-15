# handlers/callbacks/task_handlers/task_9_handler.py

import random
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from matunya_bot_final.gpt.phrases.addressing_phrases import get_student_name

# Импортируем нашу "карту тем" для Задания 9
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_9_keyboard import TASK_9_STRUCTURE

# Импортируем наш новый генератор для Задания 9
from matunya_bot_final.py_generators.task_9_generator import generate_task_9_by_subtype

# Импортируем клавиатуру "После задания"
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    compose_help_block_from_state,  # верхний блок (2 строки)
    compose_hint_block,             # нижние подсказки к 📚 и ⏱
)

# Создаем новый роутер специально для этого файла
router = Router(name="task_9_handlers")

@router.callback_query(F.data.startswith("task:9:select_theme:"))
async def handle_theme_selection_9(callback: CallbackQuery, state: FSMContext):
    """
    Этот умный обработчик ловит выбор любой темы для Задания 9.
    Работает по "золотому стандарту".
    """
    await callback.answer("⏳ Подбираю задание...")

    theme_key = callback.data.split(":")[-1]
    
    # --- Блок выбора подтемы ---
    subtypes_to_choose_from = []
    if theme_key == "random":
        subtypes_to_choose_from = [
            subtype for theme in TASK_9_STRUCTURE.values() for subtype in theme['subtypes']
        ]
    elif theme_key in TASK_9_STRUCTURE:
        subtypes_to_choose_from = TASK_9_STRUCTURE[theme_key]['subtypes']
    
    if not subtypes_to_choose_from:
        await callback.message.answer("В этой теме пока нет заданий. Попробуйте другую.")
        return

    final_subtype_key = random.choice(subtypes_to_choose_from)
    # --- Конец блока выбора ---

    task_data = await generate_task_9_by_subtype(final_subtype_key)

    if not task_data:
        await callback.message.answer("Ой, что-то пошло не так при генерации. Попробуй, пожалуйста, еще раз! 🙏")
        return
        
    # --- Этап 1: Получаем данные ---
    task_text = task_data.get("text", "Текст задания не найден")
    task_answer = task_data.get("answer")

    # --- Этап 2: Показываем ученику условие ---
    await callback.message.answer(
        f"📘 <b>Задание 9:</b>\n\n{task_text}",
        parse_mode="HTML"
    )

    # --- Этап 3: Мягкий сброс помощи ---
    await state.update_data(
        help_on=False,
        help_step=1,
        last_hint_level=0,
        last_user_text="",
        dialog_history=[]
    )

    # --- Этап 4: Сохраняем данные нового задания в FSM ---
    await state.update_data(
        task_type="9",
        task_text=task_text,
        correct_answers=[str(task_answer)] if task_answer is not None else []
    )
    
    # 6. Отправляем клавиатуру
    # 1) Верхний блок
    help_block = await compose_help_block_from_state(state)
    await callback.message.answer(f"🎯 Твой ход!\n{help_block}", parse_mode="HTML")

    # 2) Нижний блок + клавиатура
    hint_text = compose_hint_block()
    await callback.message.answer(
        hint_text,
        parse_mode="HTML",
        reply_markup=get_after_task_keyboard(
            task_number=9,
            task_subtype=final_subtype_key,
            show_help=False,
        ),
    )
