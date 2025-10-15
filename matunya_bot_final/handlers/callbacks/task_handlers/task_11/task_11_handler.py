# task_11_handler.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from aiogram.types import CallbackQuery, FSInputFile
import logging
import os
import random

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.loader import TASKS_DB
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_11.task_11_carousel import (
    get_task_11_carousel_keyboard,
    generate_task_11_overview_text,
)
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
)
from matunya_bot_final.states.states import TaskState

from matunya_bot_final.utils.text_formatters import format_task
from matunya_bot_final.task_generators.task_11 import generate_task_11_by_subtype

# Система "Идеальная Чистота"
from matunya_bot_final.utils.message_manager import (
    send_tracked_message,
    send_tracked_photo,
    cleanup_messages_by_category,
    cleanup_all_messages # <-- НАША ГЕНЕРАЛЬНАЯ УБОРКА
)

router = Router()
logger = logging.getLogger(__name__)

# ==============================
# Темы и подтипы
# ==============================
THEMES = ["read_graphs", "transformations"]

THEME_TO_SUBTYPES = {
    "read_graphs": ["match_signs_a_c", "match_signs_k_b"],  # 👈 обе прямые по чтению графиков
    "transformations": ["form_match_mixed"],
}

# Автоматическая обратная карта, чтобы по подтипу узнать тему
SUBTYPE_TO_THEME = {
    subtype: theme
    for theme, lst in THEME_TO_SUBTYPES.items()
    for subtype in lst
}

# ==============================
# Обработчик кнопки «11» → показываем карусель
# ==============================
@router.callback_query(TaskCallback.filter((F.action == "select_task") & (F.task_type == 11)))
async def handle_task_11(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    if callback_data.question_num != 11:
        return

    await query.answer()

    # --- Убираем меню выбора заданий ---
    await cleanup_messages_by_category(bot, state, query.message.chat.id, "menus")

    # --- Формируем карусель ---
    current_key = THEMES[0]
    text = generate_task_11_overview_text(THEMES, current_key)
    kb = get_task_11_carousel_keyboard(THEMES, current_key)

    # --- Отправляем через "волшебную палочку" ---
    await send_tracked_message(
        bot=bot,
        chat_id=query.message.chat.id,
        state=state,
        text=text,
        reply_markup=kb,
        message_tag="task_11_carousel",
        category="menus",
        parse_mode="HTML"
    )

    await query.answer()


# ==============================
# Навигация по карусели
# ==============================
@router.callback_query(TaskCallback.filter(F.action == "11_carousel_nav"))
async def task_11_carousel_nav(
    query: CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    current_key = callback_data.subtype_key or THEMES[0]
    text = generate_task_11_overview_text(THEMES, current_key)
    kb = get_task_11_carousel_keyboard(THEMES, current_key)

    try:
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await bot.send_message(
            chat_id=query.message.chat.id,
            text=text,
            parse_mode="HTML",
            reply_markup=kb,
        )
    await query.answer()


# ==============================
# Кнопка «✅ Открыть задание»
# ==============================
@router.callback_query(TaskCallback.filter(F.action == "select_subtype"))
async def task_11_open_selected(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    raw_key = callback_data.subtype_key or THEMES[0]
    theme_key = raw_key if raw_key in THEMES else SUBTYPE_TO_THEME.get(raw_key, THEMES[0])
    tasks_db = TASKS_DB.get("11", [])

    await query.answer()

    chat_id = query.message.chat.id
    # 💡 Убираем карусель и возможные временные уведомления
    await cleanup_messages_by_category(bot, state, chat_id, "menus")
    await cleanup_messages_by_category(bot, state, chat_id, "notifications")

    if not tasks_db:
        await query.answer("❌ База заданий пуста")
        await bot.send_message(
            chat_id=query.message.chat.id,
            text="😔 База заданий 11 типа пуста. Обратитесь к администратору.",
        )
        return

    allowed = set(THEME_TO_SUBTYPES.get(theme_key, []))
    pool = [t for t in tasks_db if t.get("subtype") in allowed] or tasks_db

    task_data = random.choice(pool)
    await send_task_11(query, bot, state, task_data)
    await query.answer("✅ Задание загружено")

# ==============================
# Кнопка «🎯 Другое задание»
# ==============================

@router.callback_query(TaskCallback.filter(F.action == "11_select_theme"))
async def task_11_another_task_handler(
    query: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    callback_data: TaskCallback,  # <-- ★★★ ДОБАВИТЬ ЭТОТ АРГУМЕНТ
) -> None:
    """
    ОБРАБОТЧИК ДЛЯ КНОПКИ "ДРУГОЕ ЗАДАНИЕ".
    Берет тему из callback_data и выдает другую задачу из той же темы из БД.
    """
    await query.answer("Подбираю другое задание...")

    # ★★★ ИЗМЕНЕНИЕ №1: Берем тему из callback_data, а не из state
    raw_key = callback_data.subtype_key
    if raw_key in THEMES:
        theme_key = raw_key
    else:
        theme_key = SUBTYPE_TO_THEME.get(raw_key)

    data = await state.get_data()
    last_task_id = data.get("task_11_data", {}).get("id")

    if not theme_key:
        await query.message.answer("Не удалось определить тему. Пожалуйста, вернитесь в меню выбора заданий.")
        return

    # ★★★ ИЗМЕНЕНИЕ №2: Сохраняем тему в state для будущих нажатий (на всякий случай)
    await state.update_data(current_task_11_theme=theme_key)

    tasks_db = TASKS_DB.get("11", [])

    pool = [
        t for t in tasks_db
        if t.get("topic") == theme_key and t.get("id") != last_task_id
    ]

    if not pool:
        pool = [t for t in tasks_db if t.get("topic") == theme_key]

    if not pool:
        await query.message.answer("Не удалось подобрать другое задание для этой темы.")
        return

    task_data = random.choice(pool)
    await send_task_11(query, bot, state, task_data)

# ==============================
# Кнопка «💫 Назад» → вернуться к карусели тем 11
# ==============================
@router.callback_query(F.data == "back_to_carousel_11")
async def back_to_carousel_11(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Возврат к карусели задания 11 с чистой сценой."""
    await callback.answer()

    # 1) Пытаемся убрать текущее сообщение (обычно «после задания»)
    try:
        await callback.message.delete()
    except Exception:
        pass

    # 2) Чистим все «следы задания» и вспомогательные панели
    await cleanup_messages_by_category(bot, state, callback.from_user.id, "tasks")
    await cleanup_messages_by_category(bot, state, callback.from_user.id, "help_panels")
    await cleanup_messages_by_category(bot, state, callback.from_user.id, "dialog_messages")
    await cleanup_messages_by_category(bot, state, callback.from_user.id, "menus")  # на всякий случай, чтобы не было дублей

    # 3) Показываем карусель тем 11 заново
    current_key = THEMES[0]
    text = generate_task_11_overview_text(THEMES, current_key)
    kb = get_task_11_carousel_keyboard(THEMES, current_key)

    await send_tracked_message(
        bot=bot,
        chat_id=callback.message.chat.id,
        state=state,
        text=text,
        reply_markup=kb,
        message_tag="task_11_carousel",
        category="menus",
        parse_mode="HTML"
    )

# ==============================
# Helper: отправка задания
# ==============================
async def send_task_11(query: CallbackQuery, bot: Bot, state: FSMContext, task_data: dict) -> None:
    """
    НОВАЯ ВЕРСЯ 3.0: Отправляет Задание 11 в правильном, полном и красивом формате.
    Сначала картинки (по одной), затем - единое сообщение с текстом, вариантами и клавиатурой.
    """
    await cleanup_messages_by_category(bot, state, query.message.chat.id, "tasks")

    # --- 1. Отправляем КАРТИНКИ по одной с подписями ---
    source_plot = task_data.get("source_plot", {})
    params = source_plot.get("params", {})
    image_paths = params.get("graphs", [])
    labels = params.get("labels", ["А", "Б", "В"])

    if not image_paths:
        logger.error("Task 11: Отсутствуют пути к изображениям в БД")
        await bot.send_message(chat_id=query.message.chat.id, text="⚠️ Ошибка: Изображения для этого задания не найдены.")
        return # Прерываем выполнение, если нет картинок

    for index, image_path in enumerate(image_paths):
        try:
            final_path = os.path.abspath(image_path.replace("\\", "/"))
            caption = f"<b>График {labels[index]}</b>" if index < len(labels) else f"График {index+1}"

            if not os.path.exists(final_path):
                logger.error(f"Task 11: Файл не найден по пути: {final_path}")
                continue

            await send_tracked_photo(
                bot=bot,
                chat_id=query.message.chat.id,
                state=state,
                photo=FSInputFile(final_path),
                caption=caption,
                parse_mode="HTML",
                message_tag=f"task_11_image_{index}",
                category="tasks"
            )
        except Exception as e:
            logger.error(f"Task 11: Ошибка отправки изображения {image_path}: {e}")

    # --- 2. Собираем ПОЛНЫЙ текст задания ДЛЯ ФИНАЛЬНОГО СООБЩЕНИЯ ---
    main_text = task_data.get("text")
    options = params.get("options", {})

    if not main_text:
        logger.error("Task 11: Отсутствует ключ 'text' в task_data.")
        await bot.send_message(chat_id=query.message.chat.id, text="❌ Ошибка: текст задания не найден.")
        return

    # Гарантируем, что final_text будет создан в любом случае
    final_text = main_text

    if options:
        # Форматируем варианты ответов в красивую строку
        variants_text = "\n".join([f"<b>{num})</b> {formula}" for num, formula in options.items()])
        # Собираем итоговый текст
        final_text = f"{main_text}\n\n<b>ВАРИАНТЫ:</b>\n{variants_text}"

    # --- 3. В КОНЦЕ отправляем текст и клавиатуру ОДНИМ сообщением ---
    logger.info(f"=== TASK 11 FINAL TEXT ===\n{final_text}")

    formatted_text = format_task(
        str(task_data.get("task_type")),
        final_text
    )

    await send_tracked_message(
        bot=bot,
        chat_id=query.message.chat.id,
        state=state,
        text=formatted_text,
        parse_mode="HTML",
        reply_markup=get_after_task_keyboard(
            task_number=task_data.get("task_type") or 11,
            task_subtype=task_data.get("subtype") or "default",
        ),
        message_tag="task_11_main_text", # Даем уникальную бирку
        category="tasks"                 # Кладем в контейнер с остальными частями задания
    )
    await state.update_data(
        task_11_data=task_data,
        task_11_formatted_text=formatted_text,
    )
    await state.set_state(TaskState.waiting_for_answer_11)
    logger.info("Task 11: данные задания сохранены, состояние ожидания ответа активировано.")
