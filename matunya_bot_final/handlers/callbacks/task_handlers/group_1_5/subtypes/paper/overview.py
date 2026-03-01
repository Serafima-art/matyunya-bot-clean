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

    logger.info("✅ ОБЗОРНЫЙ ЭКРАН: Бумага отправлена")
