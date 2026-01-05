# -*- coding: utf-8 -*-
"""Handlers for Task 15: Geometry."""

from __future__ import annotations

import logging
import os
import random
from pathlib import Path
from typing import Iterable

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    compose_after_task_message_from_state,
    get_after_task_keyboard,
)
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_15.task_15_carousel import (
    generate_task_15_overview_text,
    get_current_theme_name,
    get_task_15_carousel_keyboard,
)
from matunya_bot_final.loader import TASKS_DB
from matunya_bot_final.states.states import TaskState
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
)

router = Router()
logger = logging.getLogger(__name__)

__all__ = ("task_15_router",)
task_15_router = router

# Абсолютный путь к assets (PNG) задания 15:
# .../matunya_bot_final/handlers/callbacks/task_handlers/task_15/task_15_handler.py
# parents[4] == .../matunya_bot_final
PROJECT_ROOT = Path(__file__).resolve().parents[4]
TASK_15_ASSETS_DIR = PROJECT_ROOT / "non_generators" / "task_15" / "assets"

PATTERN_TO_THEME = {
    # Углы
    "triangle_external_angle": "angles",
    "angle_bisector_find_half_angle": "angles",
    # Треугольники общего вида
    "triangle_area_by_sin": "general_triangles",
    "triangle_area_by_dividing_point": "general_triangles",
    "triangle_area_by_parallel_line": "general_triangles",
    "triangle_area_by_midpoints": "general_triangles",
    "cosine_law_find_cos": "general_triangles",
    "triangle_by_two_angles_and_side": "general_triangles",
    "trig_identity_find_trig_func": "general_triangles",
    "triangle_medians_intersection": "general_triangles",
    # Равнобедренные
    "isosceles_triangle_angles": "isosceles_triangles",
    "equilateral_height_to_side": "isosceles_triangles",
    "equilateral_side_to_element": "isosceles_triangles",
    # Прямоугольные
    "right_triangle_angles_sum": "right_triangles",
    "pythagoras_find_leg": "right_triangles",
    "pythagoras_find_hypotenuse": "right_triangles",
    "find_cos_sin_tg_from_sides": "right_triangles",
    "find_side_from_trig_ratio": "right_triangles",
    "right_triangle_median_to_hypotenuse": "right_triangles",
}

THEMES: tuple[str, ...] = (
    "angles",
    "general_triangles",
    "isosceles_triangles",
    "right_triangles",
)


def _pick_task_for_theme(tasks: Iterable[dict], theme_key: str) -> dict | None:
    items = list(tasks)
    if not items:
        return None

    pool = [t for t in items if PATTERN_TO_THEME.get(t.get("pattern")) == theme_key]
    if not pool:
        pool = items

    return random.choice(pool)


@router.callback_query(TaskCallback.filter((F.action == "select_task") & (F.task_type == 15)))
async def handle_task_15(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    # защитный фильтр, если прилетит чужой номер
    if callback_data.question_num and callback_data.question_num != 15:
        return

    await query.answer()
    chat_id = query.message.chat.id

    # чистим меню (на всякий)
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    current_key = THEMES[0]
    overview_text = generate_task_15_overview_text(list(THEMES), current_key)
    keyboard = get_task_15_carousel_keyboard(list(THEMES), current_key)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=overview_text,
        reply_markup=keyboard,
        message_tag="task_15_carousel",
        category="menus",
        parse_mode="HTML",
    )

    await state.update_data(current_theme=current_key)


@router.callback_query(TaskCallback.filter(F.action == "15_carousel_nav"))
async def task_15_carousel_nav(
    query: CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    current_key = callback_data.subtype_key or THEMES[0]

    overview_text = generate_task_15_overview_text(list(THEMES), current_key)
    keyboard = get_task_15_carousel_keyboard(list(THEMES), current_key)

    try:
        await query.message.edit_text(
            overview_text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    except Exception:
        await bot.edit_message_reply_markup(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=keyboard,
        )

    await query.answer()


@router.callback_query(TaskCallback.filter(F.action == "15_select_theme"))
async def task_15_open_selected(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    await query.answer()
    chat_id = query.message.chat.id
    state_data = await state.get_data()

    # 1) Определяем тему
    if callback_data.subtype_key == "__USE_STATE_THEME__":
        theme_key = state_data.get("current_theme") or THEMES[0]
    else:
        theme_key = callback_data.subtype_key or THEMES[0]

    # 2) Загружаем задания
    tasks_object = TASKS_DB.get("15", {})
    tasks = tasks_object.get("tasks", []) if isinstance(tasks_object, dict) else tasks_object

    if not tasks:
        await bot.send_message(chat_id, "Пока нет заданий для этой темы.")
        return

    # 3) Берём задание только из темы
    task_data = _pick_task_for_theme(tasks, theme_key)
    if not task_data:
        await bot.send_message(chat_id, "Не удалось подобрать задание.")
        return

    # 4) Обновляем state и отправляем
    await state.update_data(current_theme=theme_key)
    await send_task_15(query, bot, state, task_data)


@router.callback_query(F.data == "back_to_carousel_15")
async def back_to_carousel_15(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
) -> None:
    await callback.answer()
    chat_id = callback.message.chat.id

    await cleanup_messages_by_category(bot, state, chat_id, "tasks")
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    current_key = THEMES[0]
    overview_text = generate_task_15_overview_text(list(THEMES), current_key)
    keyboard = get_task_15_carousel_keyboard(list(THEMES), current_key)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=overview_text,
        reply_markup=keyboard,
        message_tag="task_15_carousel",
        category="menus",
        parse_mode="HTML",
    )

    await state.update_data(current_theme=current_key)


async def send_task_15(
    query: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    task_data: dict,
) -> None:
    chat_id = query.message.chat.id

    # 1) Чистим меню
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    # 2) Чистим прошлые задания
    await cleanup_messages_by_category(bot, state, chat_id, "tasks")

    # 3️⃣ Картинка (PNG) — если есть
    image_file = task_data.get("image_file")

    if image_file:
        image_path = TASK_15_ASSETS_DIR / image_file

        if image_path.exists():
            photo = BufferedInputFile.from_file(image_path)

            msg = await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
            )

            # регистрация для cleanup
            state_data = await state.get_data()

            tracked = dict(state_data.get("tracked_messages", {}))
            tracked["task_15_image"] = msg.message_id

            tags = dict(state_data.get("message_tags_by_category", {}))
            tags.setdefault("tasks", []).append("task_15_image")

            await state.update_data(
                tracked_messages=tracked,
                message_tags_by_category=tags,
            )
        else:
            logger.warning("[Task15] PNG не найден: %s", image_path)

    # 4) Текст задания
    footer_text = await compose_after_task_message_from_state(state)

    question_text = task_data.get("text", "🔴 Ошибка: текст задания отсутствует!")
    if "Ответ" not in question_text and "🔴" not in question_text:
        question_text = question_text.strip() + "\n\nОтвет: ____________"

    topic_key = task_data.get("pattern") or "default"
    theme_key = PATTERN_TO_THEME.get(topic_key, "default")
    topic_name = get_current_theme_name(theme_key)

    final_text = (
        f"<b>Задание 15:</b> {topic_name}\n\n"
        f"{question_text}\n\n\n"
        f"{footer_text}"
    )

    keyboard = get_after_task_keyboard(task_number=15, task_subtype=topic_key)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=final_text,
        reply_markup=keyboard,
        message_tag="task_15_main_text",
        category="tasks",
        parse_mode="HTML",
    )

    topic_key = task_data.get("pattern") or "default"
    theme_key = PATTERN_TO_THEME.get(topic_key, "default")

    # 5) FSM
    await state.update_data(
        task_type=15,
        task_15_data={
            **task_data,
            "pattern": topic_key,
            "theme_key": theme_key,
        },
    )
    await state.set_state(TaskState.waiting_for_answer_15)
