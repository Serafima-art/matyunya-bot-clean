from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from pathlib import Path
import logging

from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import (
    build_focused_keyboard,
)
from matunya_bot_final.utils.text_formatters import format_task
from matunya_bot_final.utils.message_manager import (
    send_tracked_message,
)

from matunya_bot_final.non_generators.task_1_5.stoves.ui.table_builder import (
    build_stoves_table,
)
from matunya_bot_final.non_generators.task_1_5.stoves.ui.question_table_builder import (
    build_stoves_question_table,
)

from matunya_bot_final.non_generators.task_1_5.stoves.ui.intro_builder import (
    build_stoves_intro,
)

router = Router()
logger = logging.getLogger(__name__)


# =========================================================
# 🎯 ФОКУСНЫЙ ЭКРАН (ПЕЧИ)
# =========================================================

async def send_focused_task_block_stoves(
    bot: Bot,
    state: FSMContext,
    chat_id: int,
    task_1_5_data: dict,
    question_num: int,
):
    logger.info(f"🎯 ФОКУСНЫЙ ЭКРАН (stoves): {question_num}")

    tasks = task_1_5_data.get("tasks", [])
    if not (1 <= question_num <= len(tasks)):
        logger.error("❌ Некорректный номер вопроса")
        return

    task = tasks[question_num - 1]

    # Таблица значений (54 | 120 | 135 и т.п.)
    pattern = task.get("pattern")

    if pattern == "stove_match_table":
        question_table_html = build_stoves_question_table(task)

        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=question_table_html,
            message_tag=f"focused_question_table_q{question_num}",
            category="focused_assets",
            parse_mode="HTML",
        )

    # =====================================================
    # ТЕКСТ ЗАДАНИЯ
    # =====================================================
    task_text = task.get("question_text", "Текст задания не найден")
    formatted_text = format_task(str(question_num), task_text)

    user_data = await state.get_data()
    subtype_key = user_data.get("task_subtype", "stoves")

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

