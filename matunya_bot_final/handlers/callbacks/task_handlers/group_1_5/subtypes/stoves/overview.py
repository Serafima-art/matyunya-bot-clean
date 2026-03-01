from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from pathlib import Path
import logging

from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import (
    build_focused_keyboard,
    build_overview_keyboard,
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
# 📘 ОБЗОРНЫЙ ЭКРАН (ПЕЧИ)
# =========================================================

async def send_overview_block_stoves(
    bot: Bot,
    state: FSMContext,
    chat_id: int,
    task_1_5_data: dict,
):
    logger.info("📘 ОБЗОРНЫЙ ЭКРАН: Печи")

    # 0️⃣ INTRO (как в Бумаге)
    variant = task_1_5_data.get("variant_data") or task_1_5_data

    print("DEBUG STOVES VARIANT STRUCTURE:")
    print(variant)

    intro_elements = build_stoves_intro(variant)

    for index, element in enumerate(intro_elements, start=1):
        content = element.get("content", "").strip()
        if content:
            await send_tracked_message(
                bot=bot,
                chat_id=chat_id,
                state=state,
                text=content,
                message_tag=f"overview_intro_{index}",
                category="tasks",
                parse_mode="HTML",
            )

    # 1️⃣ Таблица печей
    table_context = task_1_5_data.get("table_context")
    if table_context:
        html_table = build_stoves_table(table_context)

        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=html_table,
            message_tag="overview_table_stoves",
            category="tasks",
            parse_mode="HTML",
        )

    # 2️⃣ Пульт выбора задания
    user_data = await state.get_data()
    solved_indices = user_data.get("solved_tasks_indices", [])
    subtype_key = user_data.get("task_subtype", "stoves")

    overview_kb = build_overview_keyboard(
        tasks_count=len(task_1_5_data.get("tasks", [])),
        subtype_key=subtype_key,
        solved_indices=solved_indices,
    )

    logger.info("✅ ОБЗОРНЫЙ ЭКРАН: Печи отправлен")
