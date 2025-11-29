"""Handlers for Task 20: theme carousel and statement delivery."""

from __future__ import annotations

import logging
import random
from typing import Dict, Iterable

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    compose_after_task_message_from_state,
    get_after_task_keyboard,
)
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_20.task_20_carousel import (
    generate_task_20_overview_text,
    get_task_20_carousel_keyboard,
)
from matunya_bot_final.loader import TASKS_DB
from matunya_bot_final.utils.message_manager import cleanup_messages_by_category, send_tracked_message

router = Router()
logger = logging.getLogger(__name__)

__all__ = ("task_20_router",)
task_20_router = router

THEMES: tuple[str, ...] = (
    "algebraic_expressions",
    "equations",
    "inequalities",
    "systems_equations",
    "systems_inequalities",
)

THEME_TO_SUBTYPES: Dict[str, list[str]] = {
    "algebraic_expressions": ["polynomial_factorization"],
    "equations": ["rational_equations", "radical_equations"],
    "inequalities": ["rational_inequalities"],
    "systems_equations": ["system_two_equations"],
    "systems_inequalities": ["system_two_inequalities"],
}

TOPIC_DISPLAY_NAMES: Dict[str, str] = {
    "algebraic_expressions": "Алгебраические выражения",
    "equations": "Уравнения (рациональные и иррациональные)",
    "inequalities": "Рациональные неравенства",
    "systems_equations": "Системы уравнений",
    "systems_inequalities": "Системы неравенств",
}


def _pick_task_for_theme(tasks: Iterable[dict], theme_key: str) -> dict | None:
    """Return a random task for the given theme or None if nothing fits."""
    tasks = list(tasks)
    if not tasks:
        return None

    allowed_subtypes = set(THEME_TO_SUBTYPES.get(theme_key, []))
    pool = [task for task in tasks if task.get("subtype") in allowed_subtypes] or tasks
    if not pool:
        return None
    return random.choice(pool)


def _task_text(task_data: dict) -> str:
    """Extract human readable text from task storage record."""
    return (
        task_data.get("question_text")
        or task_data.get("text")
        or task_data.get("question")
        or ""
    )

@router.callback_query(TaskCallback.filter((F.action == "select_task") & (F.task_type == 20)))
async def handle_task_20(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    """Entry point from the menu: show the theme carousel."""
    if callback_data.question_num and callback_data.question_num != 20:
        return

    await query.answer()

    chat_id = query.message.chat.id
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    current_key = THEMES[0]
    overview_text = generate_task_20_overview_text(list(THEMES), current_key)
    keyboard = get_task_20_carousel_keyboard(list(THEMES), current_key)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=overview_text,
        reply_markup=keyboard,
        message_tag="task_20_carousel",
        category="menus",
        parse_mode="HTML",
    )
    await state.update_data(current_theme=current_key)


@router.callback_query(TaskCallback.filter(F.action == "20_carousel_nav"))
async def task_20_carousel_nav(
    query: CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    current_key = callback_data.subtype_key or THEMES[0]
    overview_text = generate_task_20_overview_text(list(THEMES), current_key)
    keyboard = get_task_20_carousel_keyboard(list(THEMES), current_key)

    try:
        await query.message.edit_text(
            overview_text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    except Exception:
        await bot.send_message(
            chat_id=query.message.chat.id,
            text=overview_text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    await query.answer()


@router.callback_query(TaskCallback.filter(F.action == "20_select_theme"))
async def task_20_open_selected(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    """Pick and show one task from the selected theme."""
    await query.answer()

    theme_key = callback_data.subtype_key or THEMES[0]
    tasks = TASKS_DB.get("20", [])
    chat_id = query.message.chat.id

    if not tasks:
        await bot.send_message(chat_id, "Пока нет заданий для выдачи.")
        return

    task_data = _pick_task_for_theme(tasks, theme_key)
    if not task_data:
        await bot.send_message(chat_id, "Не удалось подобрать задание для выбранной темы.")
        return

    await state.update_data(current_theme=theme_key)
    await send_task_20(query, bot, state, task_data)


#@router.callback_query(F.data == "task20_other")
#async def task_20_other_task(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
   # """Send another task using the current theme stored in state."""
    #await query.answer("Подбираю другое задание...")

    #data = await state.get_data()
    #theme_key = data.get("current_theme") or THEMES[0]
    #tasks = TASKS_DB.get("20", [])
    #chat_id = query.message.chat.id

    #if not tasks:
        #await bot.send_message(chat_id, "Пока нет заданий для выдачи.")
        #return

    #task_data = _pick_task_for_theme(tasks, theme_key)
    #if not task_data:
        #await bot.send_message(chat_id, "Не удалось подобрать задание для выбранной темы.")
        #return

    #await send_task_20(query, bot, state, task_data)


@router.callback_query(F.data == "back_to_carousel_20")
async def back_to_carousel_20(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
) -> None:
    """Return user to the theme carousel."""
    await callback.answer()

    chat_id = callback.message.chat.id
    await cleanup_messages_by_category(bot, state, chat_id, "tasks")
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    current_key = THEMES[0]
    overview_text = generate_task_20_overview_text(list(THEMES), current_key)
    keyboard = get_task_20_carousel_keyboard(list(THEMES), current_key)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=overview_text,
        reply_markup=keyboard,
        message_tag="task_20_carousel",
        category="menus",
        parse_mode="HTML",
    )
    await state.update_data(current_theme=current_key)


async def send_task_20(query: CallbackQuery, bot: Bot, state: FSMContext, task_data: dict) -> None:
    """Отправить пользователю задание 20 с оживляющим текстом и стандартной клавиатурой."""
    chat_id = query.message.chat.id

    await cleanup_messages_by_category(bot, state, chat_id, "tasks")

    # 🔥 Критично: сообщаем системе, что это задание №20
    await state.update_data(task_type=20)

    footer_text = await compose_after_task_message_from_state(state)
    question_text = _task_text(task_data)
    if not question_text:
        logger.warning("Task 20 item without text detected: %s", task_data.get("id"))
        question_text = "📄 Текст задания временно недоступен. Запроси другое задание или попробуй позже."

    topic_key = task_data.get("topic") or task_data.get("subtype") or "default"
    topic_name = TOPIC_DISPLAY_NAMES.get(topic_key, "Общая тема")

    final_text = (
        f"<b>Задание 20:</b> {topic_name}\n"
        f"---\n"
        f"{question_text}\n"
        f"---\n\n"
        f"{footer_text}"
    )

    task_subtype = task_data.get("subtype") or task_data.get("topic") or "polynomial_factorization"

    keyboard = get_after_task_keyboard(
        task_number=20,
        task_subtype=task_subtype,
    )

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=final_text,
        reply_markup=keyboard,
        message_tag="task_20_main_text",
        category="tasks",
        parse_mode="HTML",
    )

    await state.update_data(task_20_data=task_data)
