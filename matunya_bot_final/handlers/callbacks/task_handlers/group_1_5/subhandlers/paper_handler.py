from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from pathlib import Path
import logging

from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import (
    build_focused_keyboard,
    build_overview_keyboard,
)
from matunya_bot_final.utils.text_formatters import format_task
from matunya_bot_final.utils.message_manager import (
    send_tracked_message,
    send_tracked_photo,
)
from matunya_bot_final.non_generators.task_1_5.paper.ui.table_builder import (
    build_paper_table,
)

router = Router()
logger = logging.getLogger(__name__)


# =========================================================
# 📘 ОБЗОРНЫЙ ЭКРАН
# =========================================================

async def send_overview_block_paper(
    bot: Bot,
    state: FSMContext,
    chat_id: int,
    task_1_5_data: dict,
):
    logger.info("📘 ОБЗОРНЫЙ ЭКРАН: Бумага")

    display_scenario = task_1_5_data.get("display_scenario", [])
    if not display_scenario:
        logger.error("❌ Нет display_scenario для paper")
        return

    # 1️⃣ Отправляем intro (картинка + текст)
    for index, element in enumerate(display_scenario, start=1):
        element_type = element.get("type")

        if element_type == "image":
            image_path = Path(element.get("path", ""))
            caption = element.get("caption")

            if image_path.exists():
                await send_tracked_photo(
                    bot=bot,
                    chat_id=chat_id,
                    state=state,
                    photo=FSInputFile(image_path),
                    caption=caption,
                    message_tag=f"overview_image_{index}",
                    category="tasks",
                )

        elif element_type == "text":
            content = element.get("content", "").strip()
            if content:
                await send_tracked_message(
                    bot=bot,
                    chat_id=chat_id,
                    state=state,
                    text=content,
                    message_tag=f"overview_text_{index}",
                    category="tasks",
                    parse_mode="HTML",
                )

    # 2️⃣ Пульт 1–5
    user_data = await state.get_data()
    solved_indices = user_data.get("solved_tasks_indices", [])
    subtype_key = user_data.get("task_subtype", "paper")  # ✅ ВАЖНО: subtype из state

    overview_kb = build_overview_keyboard(
        tasks_count=len(task_1_5_data.get("tasks", [])),
        subtype_key=subtype_key,
        solved_indices=solved_indices,
    )

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text="Выбери номер задания 👇:",
        reply_markup=overview_kb,
        message_tag="overview_keyboard_block",
        category="menus",
    )

    logger.info("✅ ОБЗОРНЫЙ ЭКРАН: Бумага отправлена")


# =========================================================
# 🎯 ФОКУСНЫЙ ЭКРАН
# =========================================================

async def send_focused_task_block_paper(
    bot: Bot,
    state: FSMContext,
    chat_id: int,
    task_1_5_data: dict,
    question_num: int,
):
    logger.info(f"🎯 ФОКУСНЫЙ ЭКРАН (paper): {question_num}")

    tasks = task_1_5_data.get("tasks", [])
    if not (1 <= question_num <= len(tasks)):
        logger.error("❌ Некорректный номер вопроса")
        return

    task = tasks[question_num - 1]

    # =====================================================
    # Q1 → СНАЧАЛА ТАБЛИЦА, ПОТОМ ТЕКСТ
    # ✅ Таблица нужна для Q1, Q3, Q4, для Q2 её нет
    # =====================================================
    if question_num in (1, 3, 4):
        table_context = task_1_5_data.get("table_context")
        if table_context:
            html_table = build_paper_table(table_context)
            await send_tracked_message(
                bot=bot,
                chat_id=chat_id,
                state=state,
                text=html_table,
                message_tag=f"focused_table_q{question_num}",  # ✅ tag под вопрос
                category="focused_assets",
                parse_mode="HTML",
            )

    # =====================================================
    # ТЕКСТ ЗАДАНИЯ
    # =====================================================
    task_text = task.get("question_text", "Текст задания не найден")
    formatted_text = format_task(str(question_num), task_text)

    # =====================================================
    # ВСТРАИВАЕМ ПОРЯДОК ФОРМАТОВ В ТЕКСТ (для match_formats_to_rows)
    # =====================================================
    if (
        task.get("pattern") == "paper_format_match"
        and task.get("narrative") == "match_formats_to_rows"
    ):
        columns_order = task.get("input_data", {}).get("columns_order", [])

        if isinstance(columns_order, list) and columns_order:
            formats_block = (
                "\n\n<b>Форматы для записи ответа:</b>\n"
                "<pre>" + "   ".join(columns_order) + "</pre>"
            )
            formatted_text += formats_block

    user_data = await state.get_data()
    subtype_key = user_data.get("task_subtype", "paper")  # ✅ subtype из state

    focused_keyboard = build_focused_keyboard(
        question_num,
        len(tasks),
        subtype_key,
    )

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=formatted_text,
        reply_markup=focused_keyboard,
        message_tag=f"focused_task_{question_num}",
        category="focused_task_panel",
        parse_mode="HTML",
    )

    logger.info(f"✅ ФОКУСНЫЙ ЭКРАН: Задание {question_num} отправлено")
