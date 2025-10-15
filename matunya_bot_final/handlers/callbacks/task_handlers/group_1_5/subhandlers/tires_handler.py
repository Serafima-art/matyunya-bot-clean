from aiogram import Bot, Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pathlib import Path
import logging
import random

from matunya_bot_final.gpt.phrases.addressing_phrases import get_student_name
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback



from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import build_focused_keyboard, build_overview_keyboard
from matunya_bot_final.utils.text_formatters import format_task
# Система "Идеальная Чистота" - Архитектура "Именных Бирок"
from matunya_bot_final.utils.message_manager import (
    send_tracked_message,
    send_tracked_photo,
    cleanup_messages_by_category,
    get_message_id_by_tag,   # 👈 добавили
)
from matunya_bot_final.task_generators.tasks_1_5.tires.render_table import (
    render_tire_sizes_table,
    render_service_costs_table
)

router = Router()
logger = logging.getLogger(__name__)

# Метаданные для шин (оставляем для совместимости)
TIRES_META = {
    "name": "🚗 Шины",
    "success_emoji": "🚗✨",
    "success_text": "Ты отлично разобрался с каталогом шин!",
    "retry_text": "автомобильные расчёты требуют точности!",
    "suggestion": "Хочешь разобрать еще один каталог шин?",
}


async def send_overview_block_tires(bot: Bot, state: FSMContext, chat_id: int, task_package: dict):
    """
    📘 Обзорный экран для подтипа «Шины»
    Отправляет тексты, изображения, таблицы и единый пульт выбора задания (1–5).
    """
    logger.info("📋 ОБЗОРНЫЙ ЭКРАН: Начинаем отправку общей информации про шины")

    # --- 1. Получаем сценарий отображения ---
    display_scenario = task_package.get('display_scenario', [])
    if not display_scenario:
        logger.error("❌ ОБЗОРНЫЙ ЭКРАН: Отсутствует display_scenario в task_package")
        return

    data = await state.get_data()
    student_name = data.get("student_name")
    gender = data.get("gender")

    # --- 2. Отправляем все элементы display_scenario ---
    for i, element in enumerate(display_scenario, start=1):
        element_type = element.get('type')

        if element_type == 'image':
            await _send_overview_image(bot, chat_id, state, element, i)
        elif element_type == 'text':
            await _send_overview_text(bot, chat_id, state, element, i)

    # --- 3. Таблица размеров шин (VIP-бирка) ---
    plot_data = task_package.get("plot_data", {})
    allowed_tire_sizes = plot_data.get("allowed_tire_sizes", {})
    if allowed_tire_sizes:
        tire_table_html = render_tire_sizes_table(allowed_tire_sizes)
        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=tire_table_html,
            message_tag="overview_table",
            category="task_assets"   # 💎 не очищается кнопкой Назад
        )

    # --- 4. Единый пульт выбора задания ---
    overview_kb = build_overview_keyboard(
        tasks_count=len(task_package.get("tasks", [])),
        subtype_key=task_package.get("subtype"),
        solved_indices=data.get("solved_tasks_indices", [])
    )

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text="Выбери номер задания 👇:",
        reply_markup=overview_kb,
        message_tag="overview_keyboard_block",   # 🔗 находит роутер при возврате
        category="menus"                         # 🧹 очищается при смене подтипа
    )

    logger.info("✅ ОБЗОРНЫЙ ЭКРАН: Общая информация про шины и клавиатура отправлены")


async def _send_overview_image(bot: Bot, chat_id: int, state: FSMContext, element: dict, index: int):
    """Отправляет изображение из display_scenario"""
    image_path = Path(element.get('path', ''))
    caption = element.get('caption', '')

    if image_path.exists():
        logger.info(f"📤 ОБЗОРНЫЙ ЭКРАН: Отправляем изображение {index}: {image_path.name}")
        try:
            await send_tracked_photo(
                bot=bot,
                chat_id=chat_id,
                state=state,
                photo=FSInputFile(image_path),
                caption=caption if caption else None,
                message_tag=f"overview_image_{index}",
                category="tasks"
            )
        except Exception as e:
            logger.error(f"❌ ОБЗОРНЫЙ ЭКРАН: Ошибка отправки изображения {index}: {e}")
    else:
        logger.warning(f"⚠️ ОБЗОРНЫЙ ЭКРАН: Изображение не найдено: {image_path}")


async def _send_overview_text(bot: Bot, chat_id: int, state: FSMContext, element: dict, index: int):
    """Отправляет текст из display_scenario, вешая разные "бирочки" на тексты и таблицы."""

    content = element.get('content', '')

    if content.strip():
        logger.info(f"📝 ОБЗОРНЫЙ ЭКРАН: Отправляем текст {index}")

        # --- НАША НОВАЯ, УМНАЯ ЛОГИКА ---
        # Определяем, что за контент мы отправляем
        if "<b><u>Таблица" in content:
            category = "task_assets" # <-- VIP-БИРОЧКА для таблицы
            message_tag = f"overview_table_{index}"
        else:
            category = "tasks" # <-- Обычная бирочка для текстов
            message_tag = f"overview_text_{index}"
        # ------------------------------------

        # Добавляем заголовок к первому тексту
        if index == 3:
            content = f"📘 <b>Задания 1-5: Практико-ориентированная задача. Шины.</b>\n\n{content}"

        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=content,
            message_tag=message_tag, # <-- Подставляем правильный тег
            category=category      # <-- Подставляем правильную категорию
        )
    else:
        logger.warning(f"⚠️ ОБЗОРНЫЙ ЭКРАН: Пустой текст {index}")



async def send_focused_task_block_tires(bot: Bot, state: FSMContext, chat_id: int, task_package: dict, question_num: int):
    """
    Фокусный экран: отправляет только текст задания и клавиатуру.
    """
    logger.info(f"🎯 ФОКУСНЫЙ ЭКРАН: Начинаем отправку Задания {question_num}")

    tasks = task_package.get('tasks', [])
    if not (1 <= question_num <= len(tasks)):
        logger.error(f"❌ ФОКУСНЫЙ ЭКРАН: Некорректный номер вопроса {question_num}")
        return

    task = tasks[question_num - 1]
    user_data = await state.get_data()
    subtype_key = user_data.get("task_subtype", "tires")
    focused_keyboard = build_focused_keyboard(question_num, len(tasks), subtype_key)

    # Получаем только текст задания
    task_text = task.get('text', 'Текст задания не найден')

    # --- НАШЕ УЛУЧШШЕНИЕ: Используем стандартный форматер ---
    formatted_text = format_task(str(question_num), task_text)
    # ---------------------------------------------------------

    logger.info(f"📝 ФОКУСНЫЙ ЭКРАН: Отправляем блок для Задания {question_num}")
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=formatted_text, # <-- ИСПОЛЬЗУЕМ ОТФОРМАТИРОВАННЫЙ ТЕКСТ
        reply_markup=focused_keyboard,
        message_tag=f"focused_task_{question_num}",
        category="focused_task_panel",
        parse_mode="HTML"
    )

    html_table = None
    plot_data = task_package.get("plot_data", {})

    # Проверяем, нужна ли таблица для этого конкретного вопроса.
    # Сейчас таблица нужна ТОЛЬКО для задач типа Q6.
    q_type_info = task.get("skill_source_id", "")
    if "q6" in q_type_info:
        # Для Q6 нужна таблица сервисов
        task_specific_data = plot_data.get("task_specific_data", {})
        # Ищем данные в task_6_data, с фолбэком на task_5_data для совместимости
        task_data = task_specific_data.get("task_6_data", task_specific_data.get("task_5_data", {}))
        service_data_raw = task_data.get("service_choice_data", {})

        if service_data_raw:
            # ГОТОВИМ ДАННЫЕ ДЛЯ РЕНДЕРЕРА
            services_formatted = [
                {
                    "id": s.get("name", ""),
                    "title": f"Автосервис {s.get('name', '')}",
                    "road_cost": s.get("road_cost", 0),
                    "ops": {
                        "remove": s.get("operations", {}).get("removal", 0),
                        "mount": s.get("operations", {}).get("tire_change", 0),
                        "balance": s.get("operations", {}).get("balancing", 0),
                        "install": s.get("operations", {}).get("installation", 0)
                    }
                } for s in service_data_raw.get("services", [])
            ]

            data_for_renderer = {
                "services": services_formatted,
                "currency": "руб.",
                "wheels_count": service_data_raw.get("wheels_count", 4)
            }
            html_table = render_service_costs_table(data_for_renderer)

    # Если таблица была создана, отправляем ее
    if html_table:
        logger.info(f"📦 Отправляем HTML-таблицу для Задания {question_num}...")
        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=html_table,
            message_tag=f"focused_table_{question_num}",
            category="focused_assets" # VIP-бирочка, чтобы не исчезала
        )

    logger.info(f"✅ ФОКУСНЫЙ ЭКРАН: Задание {question_num} отправлено")

@router.callback_query(TaskCallback.filter(F.action == "1-5_tires_back_to_overview"))
async def handle_tires_back_to_overview(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """
    💫 Обработчик локальной кнопки «Назад» внутри подтипа Шины.
    Возвращает к обзорной клавиатуре (1 2 3 4 5), но не удаляет таблицы и общий контент.
    """
    await callback.answer()

    chat_id = callback.message.chat.id
    logger.info("💫 НАВИГАЦИЯ: Возврат к обзору (Шины)")

    # 1. Чистим только панели, относящиеся к фокусному заданию
    await cleanup_messages_by_category(bot, state, chat_id, "focused_task_panel")
    await cleanup_messages_by_category(bot, state, chat_id, "help_panels")
    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")
    await cleanup_messages_by_category(bot, state, chat_id, "focused_assets")
    await cleanup_messages_by_category(bot, state, chat_id, "notifications")

    # 2. Восстанавливаем обзорную клавиатуру
    user_data = await state.get_data()
    task_package = user_data.get("task_package", {})
    subtype_key = user_data.get("task_subtype", "tires")
    tasks_count = len(task_package.get("tasks", []))
    solved_indices = user_data.get("solved_tasks_indices", [])

    overview_keyboard = build_overview_keyboard(tasks_count, subtype_key, solved_indices=solved_indices)

    # 1) пытаемся найти исходный “пульт”
    msg_id = await get_message_id_by_tag(state, "overview_keyboard_block")

    if msg_id:
        # 2) просто вернём клавиатуру на исходное сообщение
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=overview_keyboard
            )
        except Exception:
            # на всякий случай — если сообщение нельзя редактировать
            await send_tracked_message(
                bot=bot,
                chat_id=chat_id,
                state=state,
                text="Выбери номер задания 👇:",
                reply_markup=overview_keyboard,
                message_tag="overview_keyboard_block",
                category="menus"
            )
    else:
        # если по какой-то причине тега нет — создадим пульт заново
        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text="Выбери номер задания 👇:",
            reply_markup=overview_keyboard,
            message_tag="overview_keyboard_block",
            category="menus"
        )

    logger.info("✅ НАВИГАЦИЯ: Обзорная клавиатура восстановлена (Шины)")


# ===== УДАЛЕННЫЕ ФУНКЦИИ =====
# Следующие функции удалены в рамках рефакторинга:
# - generate_tires_task() - монолитная функция генерации и отправки
# - _send_tires_content_in_correct_order() - старая логика отправки
# - _send_tire_html_table_if_needed() - заменена на новую логику
# - _send_service_html_table_if_needed() - заменена на новую логику
# - _cleanup_tires_temp_files() - логика очистки файлов перенесена в другие модули
# - _split_intro_and_condition() - больше не нужна, так как тексты уже разделены в генераторе
