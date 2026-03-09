# matunya_bot_final/handlers/callbacks/task_handlers/group_1_5/task_1_5_router.py

from __future__ import annotations

from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker

import logging

from matunya_bot_final.loader import DATA_DIR

from .registry import TASK_1_5_REGISTRY

# Клавиатуры и CallbackData
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.task_1_5_carousel import (
    get_task_1_5_carousel_keyboard,
    generate_task_1_5_overview_text,
)
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import (
    build_overview_keyboard,
)

# Система "Идеальная Чистота"
from matunya_bot_final.utils.message_manager import (
    send_tracked_message,
    cleanup_messages_by_category,
    cleanup_all_messages,
)

# Интеграция с базой данных (регистрация задач)
from matunya_bot_final.utils.db_manager import register_task

from matunya_bot_final.states.states import TaskState

logger = logging.getLogger(__name__)
router = Router()

# =================================================================
# КОНФИГУРАЦИЯ ПОДТИПОВ (готовы к расширению)
# =================================================================
TASK_1_5_SUBTYPES = ["stoves", "paper", "apartment", "plot"]
SUBTYPES_META = {
    "stoves": {"name": "🔥 Печи", "available": True},
    "paper": {"name": "📄 Бумага (A0–A7)", "available": True},
    "apartment": {"name": "🏠 Квартира", "available": False},
    "plot": {"name": "🌱 Участок", "available": False},
}

# =================================================================
# Пути к ассетам Stoves
# =================================================================
STOVES_ASSETS_DIR = (
    DATA_DIR.parent
    / "non_generators"
    / "task_1_5"
    / "stoves"
    / "assets"
)

# =================================================================
# Пути к ассетам Paper (intro + картинка)
# =================================================================
PAPER_INTRO_PATH = DATA_DIR / "tasks_1_5" / "paper" / "paper_intro.json"

NON_GEN_ASSETS_DIR = (
    DATA_DIR.parent
    / "non_generators"
    / "task_1_5"
    / "paper"
    / "assets"
)

# =================================================================
# ВСПОМОГАТЕЛЬНЫЕ: карусельный текст
# =================================================================
def _build_carousel_text(subtype_key: str) -> str:
    text = generate_task_1_5_overview_text(TASK_1_5_SUBTYPES, subtype_key)

    if not SUBTYPES_META.get(subtype_key, {}).get("available", False):
        text_lines = text.split("\n")
        text = (
            "\n".join(text_lines[:-2])
            + "\n\n🚧 Этот подтип находится в разработке.\n"
            + "Пока доступен подтип: Бумага."
        )
    return text


# =================================================================
# СТАРТОВЫЙ ПОКАЗ КАРУСЕЛИ 1-5
# =================================================================
@router.callback_query(TaskCallback.filter(F.action == "show_task_1_5_carousel"))
async def show_task_1_5_carousel(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()

    await cleanup_all_messages(bot=bot, state=state, chat_id=callback.from_user.id)

    default_subtype = next(
        (key for key, meta in SUBTYPES_META.items() if meta.get("available")),
        TASK_1_5_SUBTYPES[0],
    )
    text = _build_carousel_text(default_subtype)

    await send_tracked_message(
        bot=bot,
        chat_id=callback.from_user.id,
        state=state,
        text=text,
        reply_markup=get_task_1_5_carousel_keyboard(TASK_1_5_SUBTYPES, default_subtype),
        message_tag="task_1_5_carousel",
        category="menus",
        parse_mode="HTML",
    )

# =================================================================
# ОБРАБОТЧИК НАВИГАЦИИ ПО КАРУСЕЛИ (без изменений по поведению)
# =================================================================
@router.callback_query(TaskCallback.filter(F.action == "1-5_carousel_nav"))
async def handle_carousel_navigation(callback: types.CallbackQuery, callback_data: TaskCallback, state: FSMContext):
    await callback.answer()

    subtype_key = callback_data.subtype_key
    subtype_meta = SUBTYPES_META.get(subtype_key, {})

    if not subtype_meta:
        await callback.message.edit_text("❌ Неизвестный подтип задания")
        return

    text = _build_carousel_text(subtype_key)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_task_1_5_carousel_keyboard(TASK_1_5_SUBTYPES, subtype_key),
    )

# =========================================================
# 🔹 dispatch_overview_screen (чистый)
# =========================================================

@router.callback_query(TaskCallback.filter(F.action == "1-5_select_subtype"))
async def dispatch_overview_screen(
    callback: types.CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
    state: FSMContext,
    session_maker: async_sessionmaker,
):
    await callback.answer()

    subtype_key = callback_data.subtype_key

    handler = TASK_1_5_REGISTRY.get(subtype_key)
    if not handler:
        await callback.answer("Этот подтип пока недоступен.", show_alert=True)
        return

    # Генеральная уборка
    await cleanup_all_messages(bot=bot, state=state, chat_id=callback.from_user.id)

    # Базовые данные
    await state.update_data(
        solved_tasks_indices=[],
        current_task_index=0,
        session_completed=False,
        last_help_task_id=None,
        task_1_5_solution_core=None,
        help_image=None,  # ← очищаем картинку предыдущего задания
        tracked_messages={},
        message_tags_by_category={},
        task_type="1-5",
        task_subtype=subtype_key,
    )

    # Loading
    await send_tracked_message(
        bot=bot,
        chat_id=callback.from_user.id,
        state=state,
        text="Минутку, готовлю задание... ⏳",
        message_tag="loading_message",
        category="notifications",
    )

    try:
        # 👉 loader из registry
        task_1_5_data = await handler["loader"]()
        if not task_1_5_data:
            raise Exception("Не удалось получить task_1_5_data")

        # 👉 регистрация задач в БД
        task_ids_from_db = []
        async with session_maker() as session:
            tasks = task_1_5_data.get("tasks", [])
            for task in tasks:
                skill_source_id = task.get("skill_source_id")
                question_text = task.get("question_text", "")
                answer_value = task.get("answer", "")

                solution_data = task.get("solution_data")

                task_id = await register_task(
                    session,
                    str(skill_source_id),
                    str(question_text),
                    str(answer_value),
                    theme=subtype_key,
                    solution_data=solution_data,
                )
                task_ids_from_db.append(task_id)

        await state.update_data(
            task_1_5_data=task_1_5_data,
            correct_answers=[t.get("answer") for t in task_1_5_data.get("tasks", [])],
            current_task_index=0,
            task_ids=task_ids_from_db,
        )

        await cleanup_messages_by_category(bot, state, callback.from_user.id, "notifications")

        # 👉 overview из registry
        await handler["overview"](
            bot=bot,
            state=state,
            chat_id=callback.from_user.id,
            task_1_5_data=task_1_5_data,
        )

        await show_task_1_5_overview(
            bot=bot,
            state=state,
            chat_id=callback.from_user.id,
        )

    except Exception as e:
        logger.error(f"Ошибка подготовки подтипа {subtype_key}: {e}", exc_info=True)
        await send_tracked_message(
            bot=bot,
            chat_id=callback.from_user.id,
            state=state,
            text="Ой, что-то пошло не так... 🛠️",
            category="notifications",
        )

# =================================================================
# 🔁 Пульт
# =================================================================

async def show_task_1_5_overview(bot: Bot, state: FSMContext, chat_id: int):
    user_data = await state.get_data()
    task_1_5_data = user_data.get("task_1_5_data", {})
    subtype_key = user_data.get("task_subtype")
    solved_indices = user_data.get("solved_tasks_indices", [])

    tasks_count = len(task_1_5_data.get("tasks", []))

    # 🧹 Чистим старые пульты
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    overview_keyboard = build_overview_keyboard(
        tasks_count=tasks_count,
        subtype_key=subtype_key,
        solved_indices=solved_indices,
    )

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text="Выбери номер задания 👇:",
        reply_markup=overview_keyboard,
        message_tag="overview_keyboard_block",
        category="menus",
    )

# =================================================================
# ВОЗВРАТ К ОБЗОРУ
# =================================================================
@router.callback_query(TaskCallback.filter(F.action == "1-5_back_to_overview"))
async def back_to_overview_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    bot = callback.bot
    chat_id = callback.message.chat.id

    # 🧹 Чистим всё, что относится к фокусному заданию
    await cleanup_messages_by_category(bot, state, chat_id, "focused_task_panel")
    await cleanup_messages_by_category(bot, state, chat_id, "focused_assets")
    await cleanup_messages_by_category(bot, state, chat_id, "help_panels")
    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")
    await cleanup_messages_by_category(bot, state, chat_id, "notifications")

    await show_task_1_5_overview(bot, state, chat_id)

    await state.set_state(None)


# =========================================================
# 🔹 dispatch_focused_screen (чистый)
# =========================================================
@router.callback_query(TaskCallback.filter(F.action == "1-5_focus_question"))
async def dispatch_focused_screen(
    callback: types.CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
    state: FSMContext,
):
    await callback.answer()

    question_num = int(callback_data.question_num or 1)

    user_data = await state.get_data()
    subtype_key = user_data.get("task_subtype")
    task_1_5_data = user_data.get("task_1_5_data")

    handler = TASK_1_5_REGISTRY.get(subtype_key)
    if not handler or not task_1_5_data:
        await callback.answer("Ошибка загрузки задания", show_alert=True)
        return

    await cleanup_messages_by_category(bot, state, callback.message.chat.id, "help_panels")
    await cleanup_messages_by_category(bot, state, callback.message.chat.id, "dialog_messages")

    await handler["focused"](
        bot=bot,
        state=state,
        chat_id=callback.from_user.id,
        task_1_5_data=task_1_5_data,
        question_num=question_num,
    )

    await state.update_data(
        current_task_index=question_num - 1,
        current_question_number=question_num,
    )

    await state.set_state(TaskState.waiting_for_answer)
