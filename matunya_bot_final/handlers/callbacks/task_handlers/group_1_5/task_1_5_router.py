# handlers/callbacks/task_handlers/task_1_5_router.py

from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
from sqlalchemy.ext.asyncio import async_sessionmaker
import logging
import time

# 🕵️ Настраиваем отдельный логгер для отладки задания 1–5
logger = logging.getLogger("task_1_5_debug")
logger.setLevel(logging.INFO)

# Импорты генераторов задач (ТОЛЬКО для готовых подтипов)
from matunya_bot_final.task_generators.tasks_1_5.generator import generate_task

# Импорты специалистов (ТОЛЬКО для готовых подтипов)
from .subhandlers.tires_handler import send_overview_block_tires, send_focused_task_block_tires

# Клавиатуры и CallbackData
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.task_1_5_carousel import get_task_1_5_carousel_keyboard, generate_task_1_5_overview_text
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import build_overview_keyboard

# Система "Идеальная Чистота"
from matunya_bot_final.utils.message_manager import (
    send_tracked_message,
    send_tracked_photo,
    cleanup_messages_by_category,
    cleanup_all_messages # <-- НАША ГЕНЕРАЛЬНАЯ УБОРКА
)

# Интеграция с базой данных
from matunya_bot_final.utils.db_manager import register_task

from matunya_bot_final.states.states import TaskState

from matunya_bot_final.task_generators.tasks_1_5.tires.render_table import render_tire_sizes_table
from matunya_bot_final.utils.text_formatters import format_task

logger = logging.getLogger(__name__)
router = Router()

# =================================================================
# КОНФИГУРАЦИЯ ПОДТИПОВ
# =================================================================
TASK_1_5_SUBTYPES = ["apartment", "tires", "plot", "bath"]
SUBTYPES_META = {
    "apartment": {"name": "🏠 Квартира", "available": False},
    "tires": {"name": "🚗 Шины", "available": True},
    "plot": {"name": "🌱 Участок", "available": False},
    "bath": {"name": "🔥 Печи", "available": False}
}


def _build_carousel_text(subtype_key: str) -> str:
    """Формирует текст карусели с учётом доступности подтипа."""
    text = generate_task_1_5_overview_text(TASK_1_5_SUBTYPES, subtype_key)

    if not SUBTYPES_META.get(subtype_key, {}).get("available", False):
        text_lines = text.split('\n')
        text = "\n".join(text_lines[:-2]) + "\n\n🚧 Этот подтип находится в разработке.\nПока доступны подтипы: Шины."

    return text


# =================================================================
# СТАРТОВЫЙ ПОКАЗ КАРУСЕЛИ 1-5
# =================================================================
@router.callback_query(TaskCallback.filter(F.action == "show_task_1_5_carousel"))
async def show_task_1_5_carousel(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """Отрисовывает первый экран карусели после выбора диапазона 1-5"""
    logger.info("🕵️ START show_task_1_5_carousel triggered")
    await callback.answer()
    logger.info("🕵️ STEP 2: cleanup_all_messages starting")
    await cleanup_all_messages(bot=bot, state=state, chat_id=callback.from_user.id)
    logger.info("🕵️ STEP 2 ✅ cleanup_all_messages done")
    default_subtype = next((key for key, meta in SUBTYPES_META.items() if meta.get("available")), TASK_1_5_SUBTYPES[0])
    text = _build_carousel_text(default_subtype)
    logger.info(f"🕵️ STEP 3: built carousel text for subtype: {default_subtype}")
    await send_tracked_message(
        bot=bot,
        chat_id=callback.from_user.id,
        state=state,
        text=text,
        reply_markup=get_task_1_5_carousel_keyboard(TASK_1_5_SUBTYPES, default_subtype),
        message_tag="task_1_5_carousel",
        category="menus",
        parse_mode="HTML"
    )

# =================================================================
# ОБРАБОТЧИК НАВИГАЦИИ ПО КАРУСЕЛИ (БЕЗ ИЗМЕНЕНИЙ)
# =================================================================
@router.callback_query(TaskCallback.filter(F.action == "1-5_carousel_nav"))
async def handle_carousel_navigation(callback: types.CallbackQuery, callback_data: TaskCallback, state: FSMContext):
    """
    Обрабатывает навигацию (листание) по карусели, РЕДАКТИРУЯ существующее сообщение.
    Это правильное поведение, т.к. state уже инициализирован.
    """
    await callback.answer()

    subtype_key = callback_data.subtype_key
    subtype_meta = SUBTYPES_META.get(subtype_key, {})

    if not subtype_meta:
        await callback.message.edit_text("❌ Неизвестный подтип задания")
        return

    # Генерируем основной текст через новую функцию
    text = _build_carousel_text(subtype_key)

    # Используем edit_text, так как мы просто меняем "слайд"
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_task_1_5_carousel_keyboard(TASK_1_5_SUBTYPES, subtype_key)
    )

# =================================================================
# ГЛАВНЫЙ ХЕНДЛЕР: ГЕНЕРАЦИЯ + ОБЗОРНЫЙ ЭКРАН (НОВАЯ АРХИТЕКТУРА)
# =================================================================
@router.callback_query(TaskCallback.filter(F.action == "1-5_select_subtype"))
async def dispatch_overview_screen(callback: types.CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext, session_maker: async_sessionmaker):
    """
    НОВАЯ АРХИТЕКТУРА: Главный хендлер для генерации задания и отправки "Обзорного экрана"

    Логика:
    1. Инициализирует state с архитектурой "Именных Бирок"
    2. Вызывает соответствующий Генератор для получения task_1_5_data
    3. Регистрирует задачи в базе данных
    4. Сохраняет task_1_5_data и task_ids в state
    5. Вызывает Специалиста для отправки "Обзорного экрана"
    6. Отправляет "Обзорную клавиатуру" с кнопками-номерами
    """
    print("🚩🚩🚩 ВЫПОЛНЯЕТСЯ dispatch_overview_screen ВЕРСИЯ 4.0 (ПОСЛЕ РЕФАКТОРИНГА) 🚩🚩🚩")
    await callback.answer()


    subtype_key = callback_data.subtype_key
    subtype_meta = SUBTYPES_META.get(subtype_key)

    if not subtype_meta or not subtype_meta.get("available", False):
        await callback.answer("Этот подтип пока недоступен.", show_alert=True)
        return

    await cleanup_all_messages(bot=bot, state=state, chat_id=callback.from_user.id)

    await state.update_data(
        solved_tasks_indices=[],
        current_task_index=0,
        session_completed=False,
        last_help_task_id=None,
        task_1_5_solution_core=None,
    )

    await state.update_data(
        tracked_messages={},
        message_tags_by_category={},
        task_type="1-5",
        task_subtype=subtype_key,
        session_completed=False
    )

    loading_text = _get_loading_text(subtype_key)
    await send_tracked_message(
        bot=callback.bot,
        chat_id=callback.from_user.id,
        state=state,
        text=loading_text,
        message_tag="loading_message",
        category="notifications"
    )

    try:
        task_1_5_data = await _generate_task_1_5_data(subtype_key, state, session_maker)
        if not task_1_5_data:
            raise Exception(f"Не удалось сгенерировать task_1_5_data для {subtype_key}")

        task_ids_from_db = []
        async with session_maker() as session:
            tasks = task_1_5_data.get('tasks', [])
            for i, task in enumerate(tasks):
                skill_source_id = task.get('skill_source_id')
                if not skill_source_id:
                    logger.warning(f"Задача {i+1} не содержит skill_source_id, пропускаем")
                    task_ids_from_db.append(None)
                    continue
                task_id = await register_task(session, str(skill_source_id), task.get('text', ''), str(task.get('answer', '')))
                task_ids_from_db.append(task_id)
                if task_id:
                    logger.info(f"✅ Задача {i+1} зарегистрирована с ID={task_id}")
                else:
                    logger.warning(f"⚠️ Не удалось зарегистрировать задачу {i+1}")

        if not any(task_ids_from_db):
            await send_tracked_message(
                bot=callback.bot,
                chat_id=callback.from_user.id,
                state=state,
                text="Ошибка: задачи не зарегистрированы в базе данных",
                message_tag="db_error",
                category="notifications"
            )
            return

        display_scenario = task_1_5_data.get('display_scenario', [])
        task_text = ''.join(item['content'] for item in display_scenario if item['type'] == 'text')
        await state.update_data(
            task_1_5_data=task_1_5_data,
            correct_answers=[task["answer"] for task in task_1_5_data["tasks"]],
            current_task_index=0,
            task_text=task_text,
            task_ids=task_ids_from_db
        )


        await _remove_loading_message(callback.bot, callback.from_user.id, state)
        # Вся отрисовка делегируется специалисту:
        await _send_overview_screen(
            bot=callback.bot,
            chat_id=callback.from_user.id,
            state=state,
            subtype_key=subtype_key,
            task_1_5_data=task_1_5_data
        )

    except Exception as e:
        logger.error(f"❌ ДИСПЕТЧЕР: Критическая ошибка при генерации {subtype_key}: {e}")
        import traceback
        traceback.print_exc()

        await _remove_loading_message(callback.bot, callback.from_user.id, state)

        await send_tracked_message(
            bot=callback.bot,
            chat_id=callback.from_user.id,
            state=state,
            text=(
                f"Ой, что-то пошло не так с генерацией... 🛠️\n"
                f"Попробуй, пожалуйста, еще раз."
            ),
            reply_markup=get_task_1_5_carousel_keyboard(TASK_1_5_SUBTYPES, subtype_key),
            message_tag="error_message",
            category="notifications"
        )

@router.callback_query(TaskCallback.filter(F.action == "1-5_back_to_overview"))
async def back_to_overview_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    💫 Возврат к Обзорному экрану (пульт 1–5).
    Удаляет панели фокусного задания и восстанавливает клавиатуру под сообщением
    'Выбери номер задания 👇:' без пересоздания дублей.
    """
    await callback.answer()
    bot = callback.bot
    chat_id = callback.message.chat.id

    logger.info("💫 НАВИГАЦИЯ: Возврат к Обзорному экрану")

    # 🧹 1. Чистим всё, что относится к фокусному заданию
    await cleanup_messages_by_category(bot, state, chat_id, "focused_task_panel")
    await cleanup_messages_by_category(bot, state, chat_id, "focused_assets")     # таблицы Q6 и подобные
    await cleanup_messages_by_category(bot, state, chat_id, "help_panels")
    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")
    await cleanup_messages_by_category(bot, state, chat_id, "notifications")

    # 📦 2. Достаём данные из state
    user_data = await state.get_data()
    task_1_5_data = user_data.get("task_1_5_data", {})
    subtype_key = user_data.get("task_subtype", "tires")
    tasks_count = len(task_1_5_data.get("tasks", []))
    solved_indices = user_data.get("solved_tasks_indices", [])

    # 🎮 3. Формируем клавиатуру
    overview_keyboard = build_overview_keyboard(tasks_count, subtype_key, solved_indices=solved_indices)

    # 🕹 4. Пробуем найти старое сообщение с обзорной клавиатурой по тегу
    from matunya_bot_final.utils.message_manager import get_message_id_by_tag
    try:
        msg_id = await get_message_id_by_tag(state, "overview_keyboard_block")

        if msg_id:
            # 🔁 просто восстанавливаем клавиатуру у старого сообщения
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=overview_keyboard
            )
            logger.info("🔁 Обзорная клавиатура восстановлена (без дублей текста)")
        else:
            # 🔧 если не нашли (редкий случай) — ничего не создаём, только логируем
            logger.warning("⚠️ Сообщение 'overview_keyboard_block' не найдено, пропуск восстановления.")

    except Exception as e:
        logger.error(f"❌ Ошибка при восстановлении обзорной клавиатуры: {e}")

    # 🔄 5. Сбрасываем состояние
    await state.set_state(None)
    logger.info("🧭 Состояние сброшено, пользователь вернулся к обзору.")

# =================================================================
# ХЕНДЛЕР ДЕТАЛИЗАЦИИ: ФОКУСНЫЙ ЭКРАН (НОВАЯ АРХИТЕКТУРА)
# =================================================================
@router.callback_query(TaskCallback.filter(F.action == "1-5_focus_question"))
async def dispatch_focused_screen(callback: types.CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext):

    """
    НОВАЯ АРХИТЕКТУРА: Хендлер для отправки "Фокусного экрана" конкретного вопроса

    Логика:
    1. Извлекает номер вопроса из callback_data
    2. Получает task_1_5_data из state
    3. Редактирует сообщение с "Обзорной клавиатурой", убирая ее
    4. Условно очищает фокусные панели только при смене задания
    5. Всегда очищает панели помощи и диалогов
    6. Вызывает Специалиста для отправки "Фокусного экрана"
    """
    await callback.answer()

    # Извлекаем данные
    question_num = int(callback_data.question_num or 1)
    user_data = await state.get_data()
    subtype_key = user_data.get("task_subtype")
    task_1_5_data = user_data.get("task_1_5_data")

    if not task_1_5_data:
        logger.error("❌ ФОКУСНЫЙ ЭКРАН: task_1_5_data не найден в state")
        await callback.answer("Ошибка: данные задания не найдены", show_alert=True)
        return

    if not subtype_key:
        logger.error("❌ ФОКУСНЫЙ ЭКРАН: task_subtype не найден в state")
        await callback.answer("Ошибка: тип задания не определен", show_alert=True)
        return

    # Проверяем корректность номера вопроса
    tasks = task_1_5_data.get('tasks', [])
    if question_num < 1 or question_num > len(tasks):
        await callback.answer(f"Ошибка: задание {question_num} не существует", show_alert=True)
        return

    logger.info(f"🎯 ФОКУСНЫЙ ЭКРАН: Переключаемся на задание {question_num} для {subtype_key}")

    # 🧹 Скрываем или удаляем старую обзорную клавиатуру (1 2 3 4 5)
    try:
        from matunya_bot_final.utils.message_manager import get_message_id_by_tag
        msg_id = await get_message_id_by_tag(state, "overview_keyboard_block")
        if msg_id:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
            logger.info(f"🧹 Удалено сообщение 'overview_keyboard_block' (ID={msg_id}) вместе с клавиатурой.")
        else:
            await callback.message.edit_reply_markup(reply_markup=None)
            logger.info("Клавиатура 1-5 скрыта (сообщение не было найдено по тегу).")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось удалить пульт 1-5: {e}")

    logger.info(f"🎯 ФОКУСНЫЙ ЭКРАН: Переключаемся на задание {question_num} для {subtype_key}")

    try:
        # 1. Временное уведомление о загрузке задания (замена edit_text)
        try:
            await send_tracked_message(
                bot=callback.bot,
                chat_id=callback.from_user.id,
                state=state,
                text="Отлично! Готовлю для тебя задание...",
                message_tag="focus_loading",
                category="notifications"
            )
            logger.info("Показано уведомление о загрузке (с категорией notifications).")
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление о загрузке: {e}")

        # === НОВАЯ ЛОГИКА ОЧИСТКИ V3.0: Накопительный эффект ===

        # Мы НЕ чистим всю категорию focused_task_panel, чтобы сохранить решенные задания.

        # Но мы ВСЕГДА очищаем временные сообщения (подсказки, ошибки).
        logger.info("🧹 Очищаем панели помощи и диалоговые сообщения.")
        await cleanup_messages_by_category(bot, state, callback.message.chat.id, "help_panels")
        await cleanup_messages_by_category(bot, state, callback.message.chat.id, "dialog_messages")
        # ===============================================

        # 2. ОТПРАВЛЯЕМ ФОКУСНЫЙ ЭКРАН через соответствующего Специалиста
        await _send_focused_screen(bot, callback.from_user.id, state, subtype_key, task_1_5_data, question_num)

        # 3. Обновляем текущий индекс задания
        await state.update_data(current_task_index=question_num - 1)

        logger.info(f"✅ ФОКУСНЫЙ ЭКРАН: Задание {question_num} для {subtype_key} отправлено")

        # 4. Переводим пользователя в состояние ожидания ответа
        await state.set_state(TaskState.waiting_for_answer)
        logger.info(f"Установлено состояние TaskState.waiting_for_answer для пользователя {callback.from_user.id}")

    except Exception as e:
        logger.error(f"❌ ФОКУСНЫЙ ЭКРАН: Ошибка при отправке задания {question_num}: {e}")
        import traceback
        traceback.print_exc()

        await send_tracked_message(
            bot=callback.bot,
            chat_id=callback.from_user.id,
            state=state,
            text=f"❌ Ошибка при загрузке задания {question_num}",
            message_tag=f"focused_error_{question_num}",
            category="notifications"
        )

# =================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =================================================================

async def _generate_task_1_5_data(subtype_key: str, state: FSMContext, session_maker: async_sessionmaker) -> dict:
    logger.info(f"🚗 ДИСПЕТЧЕР: Вызываем универсальный генератор для подтипа '{subtype_key}'")
    try:
        task_1_5_data = await generate_task(subtype=subtype_key, session_maker=session_maker)
        return task_1_5_data
    except Exception as e:
        logger.error(f"Критическая ошибка в универсальном генераторе для '{subtype_key}': {e}")
        return None

async def _send_overview_screen(bot: Bot, chat_id: int, state: FSMContext, subtype_key: str, task_1_5_data: dict):
    """Отправляет обзорный экран через соответствующего Специалиста"""

    if subtype_key == "tires":
        await send_overview_block_tires(bot, state, chat_id, task_1_5_data)

    else:
        logger.warning(f"⚠️ ДИСПЕТЧЕР: Специалист для {subtype_key} не найден")
        fallback_text = f"Задания 1-5: {SUBTYPES_META.get(subtype_key, {}).get('name', subtype_key)}\n\n🚧 В разработке..."
        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=format_task("1-5", fallback_text),
            message_tag="overview_fallback",
            category="tasks",
            parse_mode="HTML"
        )

async def _send_focused_screen(bot: Bot, chat_id: int, state: FSMContext, subtype_key: str, task_1_5_data: dict, question_num: int):
    """Отправляет фокусный экран через соответствующего Специалиста"""

    if subtype_key == "tires":
        await send_focused_task_block_tires(bot, state, chat_id, task_1_5_data, question_num)

    else:
        logger.warning(f"⚠️ ДИСПЕТЧЕР: Специалист для {subtype_key} не найден")
        fallback_text = f"Задание {question_num}:\n🚧 В разработке..."
        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=format_task("1-5", fallback_text),
            message_tag=f"focused_fallback_{question_num}",
            category="tasks",
            parse_mode="HTML"
        )
async def _remove_loading_message(bot: Bot, chat_id: int, state: FSMContext):
    """Удаляет все служебные уведомления, используя новую систему."""
    await cleanup_messages_by_category(bot, state, chat_id, "notifications")

def _get_loading_text(subtype_key: str) -> str:
    """Возвращает loading текст для конкретного подтипа"""

    loading_texts = {
        "tires": "Минутку, генерирую для тебя уникальный каталог шин... 🚗",
        "apartment": "Минутку, подбираю для тебя квартиру... 🏠",
        "plot": "Минутку, готовлю садовый участок... 🌱",
        "bath": "Минутку, разжигаю печь... 🔥"
    }

    return loading_texts.get(subtype_key, "Минутку, генерирую задание... ⏳")

def _create_fallback_task_1_5_data(subtype_key: str) -> dict:
    """Создает заглушку task_1_5_data для неготовых подтипов"""

    return {
        "main_condition": f"Задание типа {subtype_key} находится в разработке.",
        "tasks": [
            {"text": "Заглушка задания 1", "answer": 42, "params": {}},
            {"text": "Заглушка задания 2", "answer": 24, "params": {}},
        ],
        "images": [],
        "metadata": {"subtype": subtype_key, "status": "fallback"}
    }


# ==========================================================
# 🔗 Подключаем подроутеры конкретных подтипов (например, Шины)
# ==========================================================
from matunya_bot_final.handlers.callbacks.task_handlers.group_1_5.subhandlers.tires_handler import router as tires_router
router.include_router(tires_router)
