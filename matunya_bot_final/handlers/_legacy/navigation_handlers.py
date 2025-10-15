import asyncio
import random
import re
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

# Конфиги и утилиты
from matunya_bot_final.config import USE_GPT_FOR_TASK6
from matunya_bot_final.handlers._legacy.task_loader import get_random_task_6
from matunya_bot_final.handlers._legacy.bot_messages import build_instruction
from matunya_bot_final.task_generators.task_7.image_generator import create_number_line_image
from matunya_bot_final.handlers._legacy.task_utils import handle_task, safe_gen
from matunya_bot_final.utils.help_reset import reset_help_state  # импортируем наш ресет
from matunya_bot_final.handlers.callbacks.navigators.task_12_navigator import run_subtype, pick_random_any
from matunya_bot_final.gpt.instructions.tasks.task_12 import build_instruction_12

# Состояния
from matunya_bot_final.states.states import TaskState

# Клавиатуры
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import get_after_task_keyboard
from matunya_bot_final.keyboards.navigation.navigation import back_to_main_menu
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_6_keyboard import TASK_6_STRUCTURE as TASK_6_STRUCTURE, get_task_6_themes_keyboard, THEME_EMOJIS as THEME_EMOJIS_6
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_7_keyboard import TASK_7_STRUCTURE as TASK_7_STRUCTURE, get_task_7_themes_keyboard, THEME_EMOJIS as THEME_EMOJIS_7
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_8_keyboard import TASK_8_STRUCTURE as TASK_8_STRUCTURE, get_task_8_themes_keyboard, THEME_EMOJIS as THEME_EMOJIS_8
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_9_keyboard import TASK_9_STRUCTURE as TASK_9_STRUCTURE, get_task_9_themes_keyboard, THEME_EMOJIS as THEME_EMOJIS_9
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_10_keyboard import TASK_10_STRUCTURE as TASK_10_STRUCTURE, get_task_10_themes_keyboard, THEME_EMOJIS as THEME_EMOJIS_10
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_12.task_12_keyboard import TASK_12_STRUCTURE, get_task_12_main_themes_keyboard, THEME_EMOJIS as THEME_EMOJIS_12

# единый роутер (как в handlers/__init__.py)
gpt_task_router = Router(name="gpt_task_handlers")
router = gpt_task_router


# ──────────────────────────────────────────────────────────────────────────────
# Кнопки
# ──────────────────────────────────────────────────────────────────────────────

@gpt_task_router.callback_query(F.data == "gpt:task:6")
async def on_task_6(callback: CallbackQuery, state: FSMContext):
    
    """
    Обрабатывает нажатие на кнопку "Задание 6".
    Формирует и отправляет сообщение с выбором подтем.
    """
    await callback.answer()

    message_text = "<b>Задание 6: Числа и вычисления</b>\n\n"
    message_text += "Выбери тему, которую хочешь потренировать:\n"

    for i, (theme_key, theme_data) in enumerate(TASK_6_STRUCTURE.items(), 1):
        emoji = THEME_EMOJIS_6[i-1]
        theme_title = theme_data['title']
        message_text += f"\n{emoji} {i}. {theme_title}"

    keyboard = get_task_6_themes_keyboard()
    await callback.message.edit_text(message_text, reply_markup=keyboard)


@gpt_task_router.callback_query(F.data == "gpt:task:7")
async def on_task_7(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Задание 7".
    Формирует и отправляет сообщение с выбором подтем.
    """
    await callback.answer()

    message_text = "<b>Задание 7: Числовые неравенства, координатная прямая</b>\n\n"
    message_text += "Выбери тему, которую хочешь потренировать:\n"

    for i, (theme_key, theme_data) in enumerate(TASK_7_STRUCTURE.items(), 1):
        emoji = THEME_EMOJIS_7[i-1]
        theme_title = theme_data['title']
        message_text += f"\n{emoji} {i}. {theme_title}"

    keyboard = get_task_7_themes_keyboard()
    await callback.message.edit_text(message_text, reply_markup=keyboard)

@gpt_task_router.callback_query(F.data == "gpt:task:8")
async def on_task_8(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Задание 8" в главном меню.
    Формирует и отправляет сообщение с выбором подтем.
    """
    await callback.answer()

    # --- 1. Формируем красивое сообщение со списком тем ---
    # Заголовок
    message_text = "<b>Задание 8: Числа, вычисления и алгебраические выражения</b>\n\n"
    message_text += "Выбери тему, которую хочешь потренировать:\n"

    # Добавляем пронумерованный список тем с эмодзи
    # enumerate(..., 1) начинает нумерацию с 1
    for i, (theme_key, theme_data) in enumerate(TASK_8_STRUCTURE.items(), 1):
        emoji = THEME_EMOJIS_8[i-1]
        
        # ИСПРАВЛЕНИЕ: Универсальная обработка theme_data
        try:
            # Пытаемся получить как словарь
            theme_title = theme_data['title'].lstrip('0123456789. ')
        except (TypeError, KeyError):
            # Если theme_data - tuple или другая структура
            if isinstance(theme_data, tuple) and len(theme_data) > 0:
                # Берем первый элемент tuple (предполагая, что это title)
                theme_title = str(theme_data[0]).lstrip('0123456789. ')
            elif isinstance(theme_data, dict) and 'name' in theme_data:
                # Альтернативный ключ для названия
                theme_title = theme_data['name'].lstrip('0123456789. ')
            else:
                # Конвертируем в строку как fallback
                theme_title = str(theme_data).lstrip('0123456789. ')
        
        message_text += f"\n{emoji} {i}. {theme_title}"

    # --- 2. Получаем готовую клавиатуру ---
    keyboard = get_task_8_themes_keyboard()

    # --- 3. Отправляем сообщение с клавиатурой ученику ---
    # Используем edit_text, чтобы заменить сообщение "Подбираю задание..."
    await callback.message.edit_text(message_text, reply_markup=keyboard)

@gpt_task_router.callback_query(F.data == "gpt:task:9")
async def on_task_9(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Задание 9".
    Формирует и отправляет сообщение с выбором подтем.
    """
    await callback.answer()

    message_text = "<b>Задание 9: Уравнения, системы уравнений</b>\n\n"
    message_text += "Выбери тему, которую хочешь потренировать:\n"

    for i, (theme_key, theme_data) in enumerate(TASK_9_STRUCTURE.items(), 1):
        emoji = THEME_EMOJIS_9[i-1]
        theme_title = theme_data['title']
        message_text += f"\n{emoji} {i}. {theme_title}"

    keyboard = get_task_9_themes_keyboard()
    await callback.message.edit_text(message_text, reply_markup=keyboard)

@gpt_task_router.callback_query(F.data == "gpt:task:10")
async def on_task_10(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Задание 10".
    Версия 3.0: с правильным форматированием.
    """
    await callback.answer()

    message_text = "<b>Задание 10: Статистика, вероятности</b>\n\n" # <-- Это HTML
    message_text += "Выбери тему, которую хочешь потренировать:\n"

    for i, (theme_key, theme_data) in enumerate(TASK_10_STRUCTURE.items(), 1):
        emoji = THEME_EMOJIS_10[i-1]
        theme_title = theme_data['name']
        message_text += f"\n{emoji} {i}. {theme_title}"

    user_data = await state.get_data()
    gender = user_data.get("gender")

    if gender == "девочка":
        readiness_word = "Готова"
    elif gender == "мальчик":
        readiness_word = "Готов"
    else:
        readiness_word = "Готов(а)"

    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Переписываем фразу в стиле HTML (тег <i> для курсива)
    message_text += f"\n\n<i>{readiness_word} ворваться в любую из них? Погнали решать!</i> 🚀"

    keyboard = get_task_10_themes_keyboard()
    
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")

    # И возвращаем правильный parse_mode
    await callback.message.answer(message_text, reply_markup=keyboard, parse_mode="HTML")

@gpt_task_router.callback_query(F.data == "gpt:task:12")
async def on_task_12(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Задание 12".
    Формирует и отправляет сообщение с ПЕРВЫМ уровнем выбора тем.
    """
    await callback.answer()

    # Формируем красивое сообщение со списком
    message_text = "<b>Задание 12: Расчёты по формулам</b>\n\n"
    message_text += "Выбери общую тему, которую хочешь потренировать:\n"

    for i, (theme_key, theme_data) in enumerate(TASK_12_STRUCTURE.items(), 1):
        emoji = THEME_EMOJIS_12[i-1]
        theme_title = theme_data['title']
        message_text += f"\n{emoji} {i}. {theme_title}"

    # Получаем и отправляем клавиатуру ПЕРВОГО уровня
    keyboard = get_task_12_main_themes_keyboard()
    await callback.message.edit_text(message_text, reply_markup=keyboard)

# ── Диспетчер экранов подтем по типу задания ──
TASK_TOPICS_ROUTER = {
  "6": on_task_6,
  "7": on_task_7,
  "8": on_task_8,
  "9": on_task_9,
  "10": on_task_10,
  "12": on_task_12,
}

@gpt_task_router.callback_query(F.data == "back_to_topics")
async def back_to_topics(callback: CallbackQuery, state: FSMContext):
    """Возврат к экрану выбора подтем текущего задания."""
    await callback.answer()

    data = await state.get_data()
    task_type = str(data.get("task_type") or "")

    # Мягкий сброс состояния помощи
    try:
        await reset_help_state(state)
    except Exception:
        await state.update_data(
            help_on=False,
            help_step=0,
            help_finished=False,
            after_solution_mode=False,
        )

    handler = TASK_TOPICS_ROUTER.get(task_type)
    if handler:
        return await handler(callback, state)

    # Фолбэк — если task_type пустой/неподдерживаемый
    await callback.message.answer(
        "Не удалось определить текущее задание. Вернёмся в главное меню.",
        reply_markup=back_to_main_menu
    )

@gpt_task_router.callback_query(F.data == "similar_task")
async def handle_similar_task(callback: CallbackQuery, state: FSMContext):
    """Сгенерировать похожее задание того же типа."""
    await callback.answer()

    data = await state.get_data()
    task_type = data.get("task_type")

    # --- №12: генерируем ещё одно задание того же подтипа ---
    if task_type == "12":
        try:
            await reset_help_state(state)  # мягкий сброс
        except Exception:
            pass

        subtype_key = data.get("subtype_key") or pick_random_any()
        await callback.message.answer("✨ Генерирую похожее задание для №12...")

        try:
            _subtype, text, answer = run_subtype(subtype_key)
        except Exception as e:
            await callback.message.answer(
                "Упс! Не получилось собрать похожее задание №12.\n"
                f"Тех. детали: {e}\nПопробуй ещё раз или выбери другую тему."
            )
            return

        await callback.message.answer(
            f"📘 <b>Задание 12:</b>\n\n{text}",
            parse_mode="HTML"
        )

        await state.update_data(
            task_type="12",
            task_text=text,
            correct_answers=[str(answer)] if answer is not None else [],
            subtype_key=subtype_key,
            dialog_history=[{"role": "system", "content": f"Вот текущее задание:\n\n{text}"}]
        )

        gender = data.get("gender", "неизвестно")
        await callback.message.answer(
            build_instruction_12(gender),
            reply_markup=get_after_task_keyboard(
                task_number=12,
                task_subtype=subtype_key or "generic",
                show_help=False,
            ),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    if not task_type:
        await callback.message.answer("Не удалось определить тип задания. Попробуй выбрать его заново. 🙈")
        return

    # чистим историю — новый круг помощи
    await state.update_data(dialog_history=[])
    await callback.message.answer("✨ Генерирую похожее задание...")

    # генерим новое
    new_task, correct_answers = await safe_gen(task_type, state, timeout=20)
    data_after_gen = await state.get_data()
    task_source_value = data_after_gen.get("task_source", "gpt")
    source_human = "от GPT" if task_source_value == "gpt" else "из базы"

    # печать нового задания
    await callback.message.answer(f"📘 <b>Похожее задание ({source_human})</b>:\n\n{new_task}")

    # сохраняем в FSM для «Помощи» и проверки
    await state.update_data(
        task_text=new_task,
        correct_answers=correct_answers,
        source=task_source_value,
        dialog_history=[{"role": "system", "content": f"Вот текущее задание:\n\n{new_task}"}]
    )

    await state.update_data(task_text=new_task)

    # инструкция + клавиатура
    gender = data_after_gen.get("gender", "неизвестно")
    try:
        await callback.message.answer(
            build_instruction(gender, task_type),
            reply_markup=after_task_keyboard
        )
    except Exception as e:
        await callback.message.answer(build_instruction(gender, task_type))
        print(f"[WARN] after_task_keyboard не отправилась: {e}")

    # режим ожидания ответа — только для №6
    if task_type == "6":
        await state.set_state(TaskState.waiting_for_answer)

@gpt_task_router.callback_query(F.data == "open_theory")
async def open_theory_handler(callback: CallbackQuery, state: FSMContext):
    """Заглушка для теории: краткое сообщение и мягкий CTA к практике."""
    await callback.answer()
    await callback.message.answer(
        "📚 Теория по этой теме скоро появится.\n"
        "Пока давай закрепим на практике — жми <b>🧩 Похожее задание</b>.",
        parse_mode="HTML"
    )
