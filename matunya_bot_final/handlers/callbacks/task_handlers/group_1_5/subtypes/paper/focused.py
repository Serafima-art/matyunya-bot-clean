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
    if question_num == 1:
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
