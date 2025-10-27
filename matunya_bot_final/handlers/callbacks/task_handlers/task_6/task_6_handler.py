"""Handlers for Task 6: Numbers and Calculations (carousel + delivery)."""

from __future__ import annotations
import re

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
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_6.task_6_carousel import (
    generate_task_6_overview_text,
    get_task_6_carousel_keyboard,
    get_current_theme_name,
)
from matunya_bot_final.loader import TASKS_DB
from matunya_bot_final.utils.message_manager import cleanup_messages_by_category, send_tracked_message
from matunya_bot_final.utils.text_formatters import cleanup_math_for_display

try:
    from matunya_bot_final.utils.text_formatters import format_math_text as _fmt_math
except Exception:  # pragma: no cover - fallback for optional dependency
    _fmt_math = lambda s: s

router = Router()
logger = logging.getLogger(__name__)

__all__ = ("task_6_router",)
task_6_router = router

# --- Темы и связи с subtype ---
THEMES: tuple[str, ...] = (
    "common_fractions",
    "decimal_fractions",
    "mixed_fractions",
    "powers",
)

THEME_TO_SUBTYPES: Dict[str, list[str]] = {
    "common_fractions": ["cf_addition_subtraction", "multiplication_division", "parentheses_operations", "complex_fraction"],
    "decimal_fractions": ["df_addition_subtraction", "linear_operations", "fraction_structure"],
    "mixed_fractions": ["mixed_types_operations"],
    "powers": ["powers_with_fractions", "powers_of_ten"],
}


def _pick_task_for_theme(tasks: Iterable[dict], theme_key: str) -> dict | None:
    """
    Возвращает случайную задачу из выбранной темы для задания №6.
    Основана на связке subtype (основная тема) и pattern (внутренний подтип).
    """
    items = list(tasks)
    if not items:
        return None

    # --- 1. Фильтрация по subtype (основная тема) ---
    pool = [t for t in items if t.get("subtype") == theme_key]

    # --- 2. Если таких нет — фильтрация по связанным паттернам темы ---
    if not pool:
        allowed_patterns = set(THEME_TO_SUBTYPES.get(theme_key, []))
        if allowed_patterns:
            pool = [t for t in items if t.get("pattern") in allowed_patterns]

    # --- 3. Если всё ещё пусто — лог и fallback ---
    if not pool:
        logger.warning(f"[Task6] Нет задач с subtype='{theme_key}' и подходящими паттернами. Беру случайную.")
        pool = items

    return random.choice(pool)


# === ENTRYPOINT ===
@router.callback_query(TaskCallback.filter((F.action == "select_task") & (F.task_type == 6)))
async def handle_task_6(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    """Entry point from the menu: show the theme carousel."""
    if callback_data.question_num and callback_data.question_num != 6:
        return

    await query.answer()
    chat_id = query.message.chat.id

    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    current_key = THEMES[0]
    overview_text = generate_task_6_overview_text(list(THEMES), current_key)
    keyboard = get_task_6_carousel_keyboard(list(THEMES), current_key)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=overview_text,
        reply_markup=keyboard,
        message_tag="task_6_carousel",
        category="menus",
        parse_mode="HTML",
    )
    await state.update_data(current_theme=current_key)


# === NAVIGATION ===
@router.callback_query(TaskCallback.filter(F.action == "6_carousel_nav"))
async def task_6_carousel_nav(
    query: CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    """Switch themes without flicker."""
    current_key = callback_data.subtype_key or THEMES[0]
    overview_text = generate_task_6_overview_text(list(THEMES), current_key)
    keyboard = get_task_6_carousel_keyboard(list(THEMES), current_key)

    try:
        await query.message.edit_text(
            overview_text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    except Exception:
        # fallback if text identical
        await bot.edit_message_reply_markup(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=keyboard,
        )

    await query.answer()


# === OPEN THEME ===
@router.callback_query(TaskCallback.filter(F.action == "6_select_theme"))
async def task_6_open_selected(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    """Pick and show one task from the selected theme."""
    await query.answer()

    theme_key = callback_data.subtype_key or THEMES[0]
    tasks_object = TASKS_DB.get("6", {})
    tasks = tasks_object.get("tasks", []) if isinstance(tasks_object, dict) else tasks_object
    chat_id = query.message.chat.id

    if not tasks:
        await bot.send_message(chat_id, "Пока нет заданий для этой темы.")
        return

    task_data = _pick_task_for_theme(tasks, theme_key)
    if not task_data:
        await bot.send_message(chat_id, "Не удалось подобрать задание для выбранной темы.")
        return

    await state.update_data(current_theme=theme_key)
    await send_task_6(query, bot, state, task_data)


@router.callback_query(F.data == "back_to_carousel_6")
async def back_to_carousel_6(
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
    overview_text = generate_task_6_overview_text(list(THEMES), current_key)
    keyboard = get_task_6_carousel_keyboard(list(THEMES), current_key)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=overview_text,
        reply_markup=keyboard,
        message_tag="task_6_carousel",
        category="menus",
        parse_mode="HTML",
    )
    await state.update_data(current_theme=current_key)

def _task_text(task_data: dict) -> str:
    """Извлекает читаемый текст задания из структуры task_data."""
    return (
        task_data.get("question_text")
        or task_data.get("text")
        or task_data.get("question")
        or ""
    )


# === SEND TASK ===
async def send_task_6(query: CallbackQuery, bot: Bot, state: FSMContext, task_data: dict) -> None:
    """Отправить пользователю задание №6 с аккуратным текстом и клавиатурой."""
    chat_id = query.message.chat.id
    await cleanup_messages_by_category(bot, state, chat_id, "tasks")

    footer_text = await compose_after_task_message_from_state(state)
    question_text = _task_text(task_data)
    question_text = _fmt_math(question_text)
    if "Ответ" not in question_text:
        question_text = question_text.strip() + "\n\nОтвет: ____________"
    if not question_text:
        logger.warning("Task 6 item without text detected: %s", task_data.get("id"))
        question_text = "📄 Текст задания временно недоступен."

    topic_key = task_data.get("topic") or task_data.get("subtype") or "default"
    topic_name = get_current_theme_name(topic_key)

    final_text = (
        f"<b>Задание 6:</b> {topic_name}\n"
        f"\n"
        f"{question_text}\n"
        f"\n\n"
        f"{footer_text}"
    )

    final_text = cleanup_math_for_display(final_text)

    task_subtype = task_data.get("subtype") or task_data.get("topic") or "common_fractions"

    keyboard = get_after_task_keyboard(
        task_number=6,
        task_subtype=task_subtype,
    )

    # --- исправляем отображение знака умножения ---
    final_text = final_text.replace("·", "<code>·</code>")

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=final_text,
        reply_markup=keyboard,
        message_tag="task_6_main_text",
        category="tasks",
        parse_mode="HTML",
    )

    await state.update_data(task_6_data=task_data)
