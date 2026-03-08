from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
import logging
from pathlib import Path

from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import (
    build_focused_keyboard,
)
from matunya_bot_final.utils.text_formatters import format_task

from matunya_bot_final.non_generators.task_1_5.stoves.ui.question_table_builder import (
    build_stoves_question_table,
)
from matunya_bot_final.non_generators.task_1_5.stoves.ui.q4_builder import (
    build_q4_text,
)
from matunya_bot_final.non_generators.task_1_5.stoves.ui.q5_builder import (
    build_q5_text,
)

from matunya_bot_final.utils.message_manager import (
    send_tracked_message,
    send_tracked_photo,
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
    pattern = task.get("pattern")

    # =====================================================
    # ДОП. ТАБЛИЦА ДЛЯ Q1
    # =====================================================
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

    image_file = task.get("image_file")

    if image_file:
        image_path = (
            Path(__file__).resolve().parents[6]
            / "non_generators"
            / "task_1_5"
            / "stoves"
            / "assets"
            / image_file
        )

        if image_path.exists():
            await send_tracked_photo(
                bot=bot,
                chat_id=chat_id,
                state=state,
                 photo=FSInputFile(str(image_path)),
                message_tag=f"focused_task_image_q{question_num}",
                category="focused_assets",
            )
        else:
            logger.warning(f"⚠️ Картинка не найдена: {image_path}")

    # =====================================================
    # ТЕКСТ ЗАДАНИЯ
    # =====================================================
    if pattern == "stoves_discounts":
        task_text = build_q4_text(task)

    elif pattern == "stoves_arc_radius":
        task_text = build_q5_text(task)

    else:
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

