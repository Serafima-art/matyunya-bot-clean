# matunya_bot_final/handlers/callbacks/task_handlers/group_1_5/task_1_5_router.py

from __future__ import annotations

from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
import random
from sqlalchemy.ext.asyncio import async_sessionmaker
from pathlib import Path
import logging
import re
import json

from tqdm import asyncio

from matunya_bot_final.loader import DATA_DIR

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

# Paper-специалист
from matunya_bot_final.handlers.callbacks.task_handlers.group_1_5.subhandlers.paper_handler import (
    send_overview_block_paper,
    send_focused_task_block_paper,
)

from matunya_bot_final.handlers.callbacks.task_handlers.group_1_5.subhandlers.stoves_handler import (
    send_overview_block_stoves,
    send_focused_task_block_stoves,
)

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


# =================================================================
# ГЛАВНЫЙ ХЕНДЛЕР: выбор подтипа -> обзорный экран (Paper)
# =================================================================
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
    subtype_meta = SUBTYPES_META.get(subtype_key)

    if not subtype_meta or not subtype_meta.get("available", False):
        await callback.answer("Этот подтип пока недоступен.", show_alert=True)
        return

    # Генеральная уборка
    await cleanup_all_messages(bot=bot, state=state, chat_id=callback.from_user.id)

    # Базовые данные сессии
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
        session_completed=False,
    )

    # Loading
    await send_tracked_message(
        bot=callback.bot,
        chat_id=callback.from_user.id,
        state=state,
        text=_get_loading_text(subtype_key),
        message_tag="loading_message",
        category="notifications",
    )

    try:
        # ✅ Paper: берём вариант из TASKS_DB (через loader) и собираем task_1_5_data
        task_1_5_data = await _load_task_1_5_data(subtype_key=subtype_key, state=state)

        if not task_1_5_data:
            raise Exception(f"Не удалось получить task_1_5_data для {subtype_key}")

        # Регистрируем 5 вопросов в БД
        task_ids_from_db = []
        async with session_maker() as session:
            tasks = task_1_5_data.get("tasks", [])
            for i, task in enumerate(tasks):
                skill_source_id = task.get("skill_source_id")
                if not skill_source_id:
                    logger.warning(f"Задача {i+1} не содержит skill_source_id, пропускаем")
                    task_ids_from_db.append(None)
                    continue

                question_text = task.get("question_text", "")
                answer_value = task.get("answer", "")
                task_id = await register_task(
                    session,
                    str(skill_source_id),
                    str(question_text),
                    str(answer_value),
                )
                task_ids_from_db.append(task_id)

                if task_id:
                    logger.info(f"✅ Задача {i+1} зарегистрирована с ID={task_id}")
                else:
                    logger.warning(f"⚠️ Не удалось зарегистрировать задачу {i+1}")

        if not any(task_ids_from_db):
            await _remove_loading_message(callback.bot, callback.from_user.id, state)
            await send_tracked_message(
                bot=callback.bot,
                chat_id=callback.from_user.id,
                state=state,
                text="Ошибка: задачи не зарегистрированы в базе данных",
                message_tag="db_error",
                category="notifications",
            )
            return

        # Сохраняем в state
        display_scenario = task_1_5_data.get("display_scenario", [])
        task_text = "".join(
            item.get("content", "")
            for item in display_scenario
            if isinstance(item, dict) and item.get("type") == "text"
        )

        await state.update_data(
            task_1_5_data=task_1_5_data,
            correct_answers=[task.get("answer") for task in task_1_5_data.get("tasks", [])],
            current_task_index=0,
            task_text=task_text,
            task_ids=task_ids_from_db,
        )

        await _remove_loading_message(callback.bot, callback.from_user.id, state)

        # Отрисовка обзорного экрана — через специалиста
        await _send_overview_screen(
            bot=callback.bot,
            chat_id=callback.from_user.id,
            state=state,
            subtype_key=subtype_key,
            task_1_5_data=task_1_5_data,
        )

    except Exception as e:
        logger.error(f"❌ ДИСПЕТЧЕР: Критическая ошибка при подготовке {subtype_key}: {e}", exc_info=True)

        await _remove_loading_message(callback.bot, callback.from_user.id, state)

        await send_tracked_message(
            bot=callback.bot,
            chat_id=callback.from_user.id,
            state=state,
            text="Ой, что-то пошло не так... 🛠️\nПопробуй ещё раз.",
            reply_markup=get_task_1_5_carousel_keyboard(TASK_1_5_SUBTYPES, subtype_key),
            message_tag="error_message",
            category="notifications",
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

    user_data = await state.get_data()
    task_1_5_data = user_data.get("task_1_5_data", {})
    subtype_key = user_data.get("task_subtype", "paper")
    solved_indices = user_data.get("solved_tasks_indices", [])

    tasks_count = len(task_1_5_data.get("tasks", []))

    # 🎮 Формируем клавиатуру
    overview_keyboard = build_overview_keyboard(
        tasks_count=tasks_count,
        subtype_key=subtype_key,
        solved_indices=solved_indices,
    )

    # 🔁 Отправляем ТОЛЬКО пульт
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text="Выбери номер задания 👇:",
        reply_markup=overview_keyboard,
        message_tag="overview_keyboard_block",
        category="menus",
    )

    await state.set_state(None)

# =================================================================
# ФОКУСНЫЙ ЭКРАН: конкретный вопрос 1..5
# =================================================================
@router.callback_query(TaskCallback.filter(F.action == "1-5_focus_question"))
async def dispatch_focused_screen(callback: types.CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext):
    await callback.answer()

    question_num = int(callback_data.question_num or 1)
    user_data = await state.get_data()
    subtype_key = user_data.get("task_subtype")
    task_1_5_data = user_data.get("task_1_5_data")

    if not task_1_5_data or not subtype_key:
        await callback.answer("Ошибка: данные задания не найдены", show_alert=True)
        return

    tasks = task_1_5_data.get("tasks", [])
    if question_num < 1 or question_num > len(tasks):
        await callback.answer(f"Ошибка: задание {question_num} не существует", show_alert=True)
        return

    # Удаляем сообщение с обзорной клавиатурой (пульт 1–5)
    try:
        from matunya_bot_final.utils.message_manager import get_message_id_by_tag
        msg_id = await get_message_id_by_tag(state, "overview_keyboard_block")
        if msg_id:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
        else:
            await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning(f"⚠️ Не удалось удалить пульт 1-5: {e}")

    # Небольшое уведомление
    try:
        await send_tracked_message(
            bot=callback.bot,
            chat_id=callback.from_user.id,
            state=state,
            text="Отлично! Готовлю для тебя задание...",
            message_tag="focus_loading",
            category="notifications",
        )

        # 👇 вот это добавить
        await asyncio.sleep(0.4)

    except Exception:
        pass

    # Чистим помощь/диалоги
    await cleanup_messages_by_category(bot, state, callback.message.chat.id, "help_panels")
    await cleanup_messages_by_category(bot, state, callback.message.chat.id, "solution_result")
    await cleanup_messages_by_category(bot, state, callback.message.chat.id, "dialog_messages")

    # Отрисовка фокуса
    await _send_focused_screen(
        bot=callback.bot,
        chat_id=callback.from_user.id,
        state=state,
        subtype_key=subtype_key,
        task_1_5_data=task_1_5_data,
        question_num=question_num,
    )

    await state.update_data(
        current_task_index=question_num - 1,
        current_question_number=question_num,
    )
    await state.set_state(TaskState.waiting_for_answer)


# =================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =================================================================
def _get_loading_text(subtype_key: str) -> str:
    loading_texts = {
        "paper": "Минутку, готовлю для тебя таблицу форматов бумаги... 📄",
        "apartment": "Минутку, подбираю для тебя квартиру... 🏠",
        "plot": "Минутку, готовлю садовый участок... 🌱",
        "stoves": "Минутку, разжигаю печь... 🔥",
    }
    return loading_texts.get(subtype_key, "Минутку, готовлю задание... ⏳")


async def _remove_loading_message(bot: Bot, chat_id: int, state: FSMContext):
    await cleanup_messages_by_category(bot, state, chat_id, "notifications")


async def _send_overview_screen(bot: Bot, chat_id: int, state: FSMContext, subtype_key: str, task_1_5_data: dict):
    if subtype_key == "paper":
        await send_overview_block_paper(bot, state, chat_id, task_1_5_data)
        return

    if subtype_key == "stoves":
        await send_overview_block_stoves(bot, state, chat_id, task_1_5_data)
        return

    fallback_text = f"Задания 1-5: {SUBTYPES_META.get(subtype_key, {}).get('name', subtype_key)}\n\n🚧 В разработке..."
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=fallback_text,
        message_tag="overview_fallback",
        category="tasks",
        parse_mode="HTML",
    )


async def _send_focused_screen(bot: Bot, chat_id: int, state: FSMContext, subtype_key: str, task_1_5_data: dict, question_num: int):
    if subtype_key == "paper":
        await send_focused_task_block_paper(bot, state, chat_id, task_1_5_data, question_num)
        return
    if subtype_key == "stoves":
        await send_focused_task_block_stoves(
            bot, state, chat_id, task_1_5_data, question_num
        )
        return

    fallback_text = f"Задание {question_num}:\n🚧 В разработке..."
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=fallback_text,
        message_tag=f"focused_fallback_{question_num}",
        category="tasks",
        parse_mode="HTML",
    )


# -------------------------
# Paper: загрузка варианта + intro
# -------------------------
def _sort_key_paper_id(item: dict) -> int:
    # paper_2026_var_15 -> 15
    m = re.search(r"_var_(\d+)$", str(item.get("id", "")))
    return int(m.group(1)) if m else 10**9


def _load_paper_intro() -> list[dict]:
    if not PAPER_INTRO_PATH.exists():
        return []

    raw = json.loads(PAPER_INTRO_PATH.read_text(encoding="utf-8"))

    # ✅ Новый формат: {"paper_intro": {...}}
    if isinstance(raw, dict) and "paper_intro" in raw:
        intro_block = raw["paper_intro"]

        title = intro_block.get("title", "").strip()
        text = intro_block.get("text", "").strip()

        content = ""
        if title:
            content += f"<b>{title}</b>\n\n"
        if text:
            content += text

        return [
            {
                "type": "image",
                "path": str(NON_GEN_ASSETS_DIR / "task_paper_formats.png"),
                "caption": None,
            },
            {
                "type": "text",
                "content": content,
            },
        ]

    # Старые форматы (если будут)
    if isinstance(raw, list):
        return raw

    return []


def _attach_intro_assets(display_scenario: list[dict]) -> list[dict]:
    """
    Нормализуем пути к картинке:
    если элемент type=image и path относительный — превращаем в абсолютный к assets.
    """
    out = []
    for el in display_scenario:
        if not isinstance(el, dict):
            continue
        if el.get("type") == "image":
            p = el.get("path", "")
            path_obj = Path(p)
            if not path_obj.is_absolute():
                # default: берем из non_generators assets
                path_obj = NON_GEN_ASSETS_DIR / path_obj.name
            el = {**el, "path": str(path_obj)}
        out.append(el)
    return out


async def _load_task_1_5_data(subtype_key: str, state: FSMContext) -> dict | None:
    """
    Загружает один вариант подтипа 1–5 из TASKS_DB и приводит его к формату task_1_5_data,
    который ожидают subhandlers (paper_handler / stoves_handler).

    Поддерживаем сейчас:
    - paper
    - stoves
    """

    # ⚠️ Здесь мы полагаемся, что loader.py уже загрузил TASKS_DB.
    from matunya_bot_final.loader import TASKS_DB

    # -------------------------------------------------------------
    # PAPER
    # -------------------------------------------------------------
    if subtype_key == "paper":
        variants = TASKS_DB.get("1_5_paper") or []
        if not variants:
            logger.error("❌ TASKS_DB['1_5_paper'] пуст")
            return None

        variants_sorted = sorted(variants, key=_sort_key_paper_id)
        chosen = random.choice(variants_sorted)

        questions = chosen.get("questions", [])
        table_context = chosen.get("table_context")
        image_file = chosen.get("image_file")

        # display_scenario: берём из отдельного файла и нормализуем пути
        intro = _attach_intro_assets(_load_paper_intro())

        # Если intro вообще без картинки — можно автоматически добавить стандартную
        if intro and not any(el.get("type") == "image" for el in intro):
            if image_file:
                intro = [{"type": "image", "path": str(NON_GEN_ASSETS_DIR / image_file), "caption": None}] + intro

        return {
            "id": chosen.get("id"),
            "image_file": image_file,
            "table_context": table_context,
            "display_scenario": intro,
            "tasks": questions,  # ✅ важно: handler ждёт key "tasks"
            "metadata": {"subtype": "paper"},
        }

    # -------------------------------------------------------------
    # STOVES
    # -------------------------------------------------------------
    if subtype_key == "stoves":
        variants = TASKS_DB.get("1_5_stoves") or []
        if not variants:
            logger.error("❌ TASKS_DB['1_5_stoves'] пуст")
            return None

        chosen = random.choice(variants)

        questions = chosen.get("questions", [])
        table_context = chosen.get("table_context")

        # У печей пока нет intro / image_file на уровне варианта (картинка будет у Q5 позже)
        return {
            "id": chosen.get("id"),
            "table_context": table_context,
            "display_scenario": [],
            "tasks": questions,
            "metadata": {"subtype": "stoves"},
        }

    # -------------------------------------------------------------
    # OTHER SUBTYPES — пока не реализованы
    # -------------------------------------------------------------
    return None
