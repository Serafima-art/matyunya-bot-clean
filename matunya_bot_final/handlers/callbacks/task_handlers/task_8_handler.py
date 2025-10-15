import random
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from matunya_bot_final.gpt.phrases.addressing_phrases import get_student_name
from matunya_bot_final.utils.help_reset import reset_help_state

# Импортируем клавиатуру "После задания"
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    compose_help_block_from_state,  # верхний блок (2 строки)
    compose_hint_block,             # нижние подсказки к 📚 и ⏱
)

# Импортируем нашу "карту тем" для Задания 8
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_8_keyboard import TASK_8_STRUCTURE

# Импортируем наш новый генератор
from matunya_bot_final.py_generators.task_8_generator import generate_task_8_by_subtype

# Импортируем наш универсальный "отправлятор" заданий
from matunya_bot_final.handlers._legacy.task_utils import handle_task

# Создаем новый роутер специально для этого файла
router = Router(name="task_8_handlers")

#
# СЮДА МЫ СКОРО ДОБАВИМ НАШ НОВЫЙ, УМНЫЙ ОБРАБОТЧИК
#
@router.callback_query(F.data.startswith("task:8:select_theme:"))
async def handle_theme_selection(callback: CallbackQuery, state: FSMContext):
    """
    Этот умный обработчик ловит выбор любой темы для Задания 8.
    """
    # 1. "Откусываем" ключ темы от callback_data
    # callback_data будет, например, "task:8:select_theme:integer_expressions"
    theme_key = callback.data.split(":")[-1]

    final_subtype_key = ""

    # 2. Определяем, какую детальную подтему генерировать
    if theme_key == "random":
        # Если нажата кнопка "Случайная тема", выбираем случайную подтему из ВСЕХ
        all_subtypes = [subtype for theme in TASK_8_STRUCTURE.values() for subtype in theme['subtypes']]
        final_subtype_key = random.choice(all_subtypes)
    elif theme_key in TASK_8_STRUCTURE:
        # Если выбрана конкретная тема, выбираем случайную подтему ИЗ НЕЕ
        subtypes_for_theme = TASK_8_STRUCTURE[theme_key]['subtypes']
        final_subtype_key = random.choice(subtypes_for_theme)
    
    if not final_subtype_key:
        # На всякий случай, если что-то пошло не так
        await callback.answer("Не удалось определить тему, попробуйте еще раз.", show_alert=True)
        return

    # 3. Генерируем задание с помощью нашего "дирижера"
    # Показываем сообщение-ожидание
    await callback.message.edit_text("⏳ Минуточку, подбираю для тебя идеальное задание...")

    
    # Вызываем наш новый генератор
    task_data = await generate_task_8_by_subtype(final_subtype_key)


    if not task_data:
        await callback.message.edit_text("Ой, что-то пошло не так при генерации. Попробуй, пожалуйста, еще раз! 🙏")
        return
        
    # 4. Красиво отправляем задание ученику
    # (здесь мы пока напишем простую отправку, а handle_task подключим позже, если понадобится)
    task_text = task_data.get("text", "Текст задания не найден")
    task_answer = task_data.get("answer", "Ответ не найден")

    await callback.message.edit_text(
        f"📘 <b>Задание 8:</b>\n\n{task_text}",
        parse_mode="HTML"
    )

    # 5. Сохраняем состояние (мягкий reset помощи + новые данные задания)
    await reset_help_state(state)  # <<-- МЯГКИЙ СБРОС ПОМОЩИ

    await state.update_data(
    task_type="8",
    # единый ключ для help_flow:
    task_text=task_text,
    correct_answers=[str(task_answer)] if task_answer is not None else []
)

    # 6. Отправляем клавиатуру после задания
    # 1) Верхний блок
    help_block = await compose_help_block_from_state(state)
    await callback.message.answer(f"🎯 Твой ход!\n{help_block}", parse_mode="HTML")

    # 2) Нижний блок + клавиатура
    hint_text = compose_hint_block()
    await callback.message.answer(
        hint_text,
        parse_mode="HTML",
        reply_markup=get_after_task_keyboard(
            task_number=8,
            task_subtype=final_subtype_key,
            show_help=False,
        ),
    )
    
    # Не забываем ответить на callback, чтобы убрать "часики"
    await callback.answer()
