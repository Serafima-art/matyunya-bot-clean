# handlers/callbacks/task_handlers/task_6_handler.py

import random
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from matunya_bot_final.gpt.phrases.addressing_phrases import get_student_name

# Импортируем нашу "карту тем" для Задания 6
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_6_keyboard import TASK_6_STRUCTURE

# Импортируем наш новый генератор для Задания 6
from matunya_bot_final.py_generators.task_6_generator import generate_task_6_by_subtype

# Импортируем клавиатуру "После задания" и генераторы текста
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    compose_help_block_from_state,  # верхний блок (2 строки)
    compose_hint_block,             # нижние подсказки к 📚/⏱
)

# Создаем новый роутер специально для этого файла
router = Router(name="task_6_handlers")

@router.callback_query(F.data.startswith("task:6:select_theme:"))
async def handle_theme_selection_6(callback: CallbackQuery, state: FSMContext):
    """
    Этот умный обработчик ловит выбор любой темы для Задания 6.
    """
    await callback.answer("⏳ Подбираю задание...")

    theme_key = callback.data.split(":")[-1]
    
    # --- Блок выбора подтемы (улучшенная версия) ---
    subtypes_to_choose_from = []
    if theme_key == "random":
        # Если "Случайная тема" - собираем ВСЕ подтемы из всех категорий
        subtypes_to_choose_from = [
            subtype for theme in TASK_6_STRUCTURE.values() for subtype in theme['subtypes']
        ]
    elif theme_key in TASK_6_STRUCTURE:
        # Если выбрана конкретная тема - берем подтемы только из нее
        subtypes_to_choose_from = TASK_6_STRUCTURE[theme_key]['subtypes']
    
    if not subtypes_to_choose_from:
        # Если по какой-то причине список подтем пуст
        await callback.message.answer("В этой теме пока нет заданий. Попробуйте другую.")
        return

    # Выбираем финальную подтему из подготовленного списка
    final_subtype_key = random.choice(subtypes_to_choose_from)
    # --- Конец блока выбора ---

    task_data = await generate_task_6_by_subtype(final_subtype_key)

    if not task_data:
        await callback.message.answer("Ой, что-то пошло не так при генерации. Попробуй, пожалуйста, еще раз! 🙏")
        return
        
    task_text = task_data.get("text")
    task_answer = task_data.get("answer")

    # Отправляем задание НОВЫМ сообщением
    await callback.message.answer(f"📘 <b>Задание 6:</b>\n\n{task_text}", parse_mode="HTML")

    # ⛳ Мягкий сброс помощи + чистая история для нового задания
    await state.update_data(
        help_on=False,
        help_step=1,
        last_hint_level=0,
        last_user_text="",
        dialog_history=[]
    )

    # Сохраняем данные в FSM
    await state.update_data(
        task_type="6",
        task_text=task_text,
        correct_answers=[str(task_answer)] if task_answer is not None else []
)
    
    # Отправляем инструкции и клавиатуру ВТОРЫМ сообщением
    # 1) Верхний блок (без слова «Готово») — +пол из FSM
    help_block = await compose_help_block_from_state(state)
    await callback.message.answer(f"🎯 Твой ход!\n{help_block}", parse_mode="HTML")

    # 2) Нижний блок (рандомные подсказки к 📚 и ⏱) + клавиатура
    hint_text = compose_hint_block()
    await callback.message.answer(
        hint_text,
        parse_mode="HTML",
        reply_markup=get_after_task_keyboard(
            task_number=6,
            task_subtype=final_subtype_key,
            show_help=False,
        ),
    )

    # снимаем "часики" у кнопки
    await callback.answer()
