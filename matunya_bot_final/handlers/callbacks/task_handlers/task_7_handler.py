# handlers/callbacks/task_handlers/task_7_handler.py

import random
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from matunya_bot_final.gpt.phrases.addressing_phrases import get_student_name

# Импортируем нашу "карту тем" для Задания 7
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_7_keyboard import TASK_7_STRUCTURE

# ВАЖНО: Импортируем наш СТАРЫЙ, GPT-шный генератор для Задания 7
from matunya_bot_final.gpt.task_templates.task_7.task_7_generator import generate_task_7

# Импортируем клавиатуру "После задания"
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    compose_help_block_from_state,  # верхний блок (2 строки)
    compose_hint_block,             # нижние подсказки к 📚 и ⏱
)
from matunya_bot_final.task_generators.task_7.image_generator import create_number_line_image # Для отрисовки координатной прямой
from aiogram.types import BufferedInputFile
import re


# Создаем новый роутер специально для этого файла
router = Router(name="task_7_handlers")

@router.callback_query(F.data.startswith("task:7:select_theme:"))
async def handle_theme_selection_7(callback: CallbackQuery, state: FSMContext):
    """
    Этот умный обработчик ловит выбор любой темы для Задания 7.
    Работает по "золотому стандарту".
    """
    await callback.answer("⏳ Подбираю задание...")

    theme_key = callback.data.split(":")[-1]
    
    # --- Блок выбора подтемы (улучшенная версия) ---
    subtypes_to_choose_from = []
    if theme_key == "random":
        # Если "Случайная тема" - собираем ВСЕ подтемы из всех категорий
        subtypes_to_choose_from = [
            subtype for theme in TASK_7_STRUCTURE.values() for subtype in theme['subtypes']
        ]
    elif theme_key in TASK_7_STRUCTURE:
        # Если выбрана конкретная тема - берем подтемы только из нее
        subtypes_to_choose_from = TASK_7_STRUCTURE[theme_key]['subtypes']
    
    if not subtypes_to_choose_from:
        # Если по какой-то причине список подтем пуст
        await callback.message.answer("В этой теме пока нет заданий. Попробуй другую.")
        return

    # Выбираем финальную подтему из подготовленного списка
    final_subtype_key = random.choice(subtypes_to_choose_from)
    # --- Конец блока выбора ---

    task_data = await generate_task_7(final_subtype_key)

    if not task_data:
        await callback.message.answer("Ой, что-то пошло не так при генерации. Попробуй, пожалуйста, еще раз! 🙏")
        return
        
    # --- Этап 1: Получаем данные ---
    task_text = task_data.get("text", "")
    options = task_data.get("options", [])
    task_answer = task_data.get("answer", "")
    image_params = task_data.get("image_params")

    # Форматируем текст для ученика
    clean_text = re.split(r'\n\s*1\)', task_text)[0].strip()
    options_text = "\n".join(f"{i+1}) {opt}" for i, opt in enumerate(options))
    full_task_text_for_user = f"{clean_text}\n\n{options_text}"

    # --- Этап 2: Показываем ученику условие ---
    if image_params:
        image_bytes = create_number_line_image(image_params)
        photo_to_send = BufferedInputFile(image_bytes.getvalue(), filename="task_7.png")
        await callback.message.answer_photo(
            photo=photo_to_send, 
            caption=f"📘 <b>Задание 7:</b>\n\n{full_task_text_for_user}",
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            f"📘 <b>Задание 7:</b>\n\n{full_task_text_for_user}",
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
        task_type="7",
        task_text=task_text, # Сохраняем полный текст, а не "очищенный"
        correct_answers=[str(task_answer)] if task_answer is not None else []
    )
    
    # --- Этап 5: Отправляем клавиатуру после задания ---
    # 1) Верхний блок
    help_block = await compose_help_block_from_state(state)
    await callback.message.answer(f"🎯 Твой ход!\n{help_block}", parse_mode="HTML")

    # 2) Нижний блок + клавиатура
    hint_text = compose_hint_block()
    await callback.message.answer(
        hint_text,
        parse_mode="HTML",
        reply_markup=get_after_task_keyboard(
            task_number=7,
            task_subtype=final_subtype_key,
            show_help=False,
        ),
    )

    # --- Этап 6: Убираем «часики» с кнопки ---
    # Мы уже сделали это в самом начале через await callback.answer("..."),
    # поэтому второй раз вызывать не нужно.
