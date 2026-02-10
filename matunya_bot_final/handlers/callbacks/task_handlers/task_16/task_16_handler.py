# -*- coding: utf-8 -*-
"""Handlers for Task 16: Geometry (Circle)."""

from __future__ import annotations

import logging
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
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_16.task_16_carousel import (
    generate_task_16_overview_text,
    get_task_16_carousel_keyboard,
)
from matunya_bot_final.loader import TASKS_DB
from matunya_bot_final.states.states import TaskState
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
)

router = Router()
logger = logging.getLogger(__name__)

__all__ = ("task_16_router",)
task_16_router = router

# -----------------------------------------------------------------------------
# Пути
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[4]
TASK_16_ASSETS_DIR = PROJECT_ROOT / "non_generators" / "task_16" / "assets"

# -----------------------------------------------------------------------------
# Темы и паттерны задания 16
# -----------------------------------------------------------------------------
THEMES_16: dict[str, dict] = {
    "central_and_inscribed_angles": {
        "title": "Центральные и вписанные углы",
        "patterns": (
            "cyclic_quad_angles",
            "central_inscribed",
            "radius_chord_angles",
            "arc_length_ratio",
            "diameter_right_triangle",
            "two_diameters_angles",
        ),
    },
    "circle_elements_relations": {
        "title": "Касательная, хорда, секущая, радиус",
        "patterns": (
            "secant_similarity",
            "tangent_trapezoid_properties",
            "tangent_quad_sum",
            "tangent_arc_angle",
            "angle_tangency_center",
            "sector_area",
            "power_point",
        ),
    },
    "circle_around_polygon": {
        "title": "Окружность вокруг многоугольника",
        "patterns": (
            "square_incircle_circumcircle",
            "eq_triangle_circles",
            "square_radius_midpoint",
            "right_triangle_circumradius",
        ),
    },
}

THEMES_ORDER: tuple[str, ...] = tuple(THEMES_16.keys())


# -----------------------------------------------------------------------------
# Утилита выбора задания (Task 16)
# -----------------------------------------------------------------------------
def _pick_task_for_theme_16(
    tasks: Iterable[dict],
    theme_key: str,
    exclude_pattern: str | None = None,
) -> dict | None:
    """
    Выбирает задание из указанной темы Task 16.

    Правила:
    1. Берём только задания из паттернов выбранной темы.
    2. При наличии exclude_pattern — стараемся выбрать задание
       с ДРУГИМ паттерном (чтобы «Другое задание» было реально другим).
    3. Если после исключения паттерна вариантов не осталось —
       разрешаем повтор текущего паттерна (fallback).
    """

    items = list(tasks)
    if not items:
        return None

    # Разрешённые паттерны темы
    allowed_patterns = set(THEMES_16[theme_key]["patterns"])

    # 1) Базовый пул по теме
    themed_pool = [
        t for t in items
        if t.get("pattern") in allowed_patterns
    ]

    if not themed_pool:
        return None

    # 2) Пул без текущего паттерна (если он передан)
    if exclude_pattern:
        filtered_pool = [
            t for t in themed_pool
            if t.get("pattern") != exclude_pattern
        ]

        # Если удалось исключить текущий паттерн — используем этот пул
        if filtered_pool:
            return random.choice(filtered_pool)

    # 3) Fallback: если паттерн один или исключать нечего
    return random.choice(themed_pool)


# -----------------------------------------------------------------------------
# Вход в задание 16 (карусель тем)
# -----------------------------------------------------------------------------
@router.callback_query(TaskCallback.filter((F.action == "select_task") & (F.task_type == 16)))
async def handle_task_16(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    await query.answer()
    chat_id = query.message.chat.id

    # чистим меню
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    current_theme = THEMES_ORDER[0]

    overview_text = generate_task_16_overview_text(THEMES_16, current_theme)
    keyboard = get_task_16_carousel_keyboard(THEMES_16, current_theme)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=overview_text,
        reply_markup=keyboard,
        message_tag="task_16_carousel",
        category="menus",
        parse_mode="HTML",
    )

    await state.update_data(current_theme=current_theme)


# -----------------------------------------------------------------------------
# Навигация по карусели
# -----------------------------------------------------------------------------
@router.callback_query(TaskCallback.filter(F.action == "16_carousel_nav"))
async def task_16_carousel_nav(
    query: CallbackQuery,
    callback_data: TaskCallback,
    bot: Bot,
) -> None:
    current_theme = callback_data.subtype_key or THEMES_ORDER[0]

    overview_text = generate_task_16_overview_text(THEMES_16, current_theme)
    keyboard = get_task_16_carousel_keyboard(THEMES_16, current_theme)

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


# -----------------------------------------------------------------------------
# Открытие выбранной темы
# -----------------------------------------------------------------------------
@router.callback_query(TaskCallback.filter(F.action == "16_select_theme"))
async def task_16_open_selected(
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
        theme_key = state_data.get("current_theme") or THEMES_ORDER[0]
    else:
        theme_key = callback_data.subtype_key or THEMES_ORDER[0]

    # 2) Загружаем задания
    tasks_object = TASKS_DB.get("16", {})
    tasks = tasks_object.get("tasks", []) if isinstance(tasks_object, dict) else tasks_object

    if not tasks:
        await bot.send_message(chat_id, "Пока нет заданий для этой темы.")
        return

    # 3) Выбираем задание
    state_data = await state.get_data()
    current_task = state_data.get("task_16_data", {})
    current_pattern = current_task.get("pattern")

    task_data = _pick_task_for_theme_16(
        tasks,
        theme_key,
        exclude_pattern=current_pattern,
    )
    if not task_data:
        await bot.send_message(chat_id, "Не удалось подобрать задание.")
        return

    # 4) Обновляем state и отправляем
    await state.update_data(current_theme=theme_key)
    await send_task_16(query, bot, state, task_data)


# -----------------------------------------------------------------------------
# Назад к карусели
# -----------------------------------------------------------------------------
@router.callback_query(F.data == "back_to_carousel_16")
async def back_to_carousel_16(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
) -> None:
    await callback.answer()
    chat_id = callback.message.chat.id

    await cleanup_messages_by_category(bot, state, chat_id, "tasks")
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    current_theme = THEMES_ORDER[0]
    overview_text = generate_task_16_overview_text(THEMES_16, current_theme)
    keyboard = get_task_16_carousel_keyboard(THEMES_16, current_theme)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=overview_text,
        reply_markup=keyboard,
        message_tag="task_16_carousel",
        category="menus",
        parse_mode="HTML",
    )

    await state.update_data(current_theme=current_theme)


# -----------------------------------------------------------------------------
# Отправка задания
# -----------------------------------------------------------------------------
async def send_task_16(
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

    # 3) Картинка
    image_file = task_data.get("image_file")
    if image_file:
        image_path = TASK_16_ASSETS_DIR / image_file
        if image_path.exists():
            photo = BufferedInputFile.from_file(image_path)
            msg = await bot.send_photo(chat_id=chat_id, photo=photo)

            state_data = await state.get_data()
            tracked = dict(state_data.get("tracked_messages", {}))
            tracked["task_16_image"] = msg.message_id

            tags = dict(state_data.get("message_tags_by_category", {}))
            tags.setdefault("tasks", []).append("task_16_image")

            await state.update_data(
                tracked_messages=tracked,
                message_tags_by_category=tags,
            )
        else:
            logger.warning("[Task16] PNG не найден: %s", image_path)

    # 4) Текст задания
    footer_text = await compose_after_task_message_from_state(state)

    question_text = task_data.get("question_text", "🔴 Ошибка: текст задания отсутствует!")
    if "Ответ" not in question_text and "🔴" not in question_text:
        question_text = question_text.strip() + "\n\nОтвет: ____________"

    theme_key = (await state.get_data()).get("current_theme", THEMES_ORDER[0])
    theme_title = THEMES_16[theme_key]["title"]

    final_text = (
        f"<b>Задание 16:</b> {theme_title}\n\n"
        f"{question_text}\n\n\n"
        f"{footer_text}"
    )

    keyboard = get_after_task_keyboard(
        task_number=16,
        task_subtype=task_data.get("pattern"),
    )

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=final_text,
        reply_markup=keyboard,
        message_tag="task_16_main_text",
        category="tasks",
        parse_mode="HTML",
    )

    # 5) FSM
    await state.update_data(
        task_type=16,
        task_16_data={
            **task_data,
            "pattern": task_data.get("pattern"),
            "theme_key": theme_key,
        },
    )
    await state.set_state(TaskState.waiting_for_answer_16)
