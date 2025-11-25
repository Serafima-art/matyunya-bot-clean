"""Handlers for Task 8: Numbers, Calculations, and Algebraic Expressions."""

from __future__ import annotations
import logging
import random
import json # Добавили для отладки
from typing import Dict, Iterable, Any

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    compose_after_task_message_from_state,
    get_after_task_keyboard,
)
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_8.task_8_carousel import (
    generate_task_8_overview_text,
    get_task_8_carousel_keyboard,
    get_current_theme_name,
)
from matunya_bot_final.loader import TASKS_DB
from matunya_bot_final.utils.message_manager import cleanup_messages_by_category, send_tracked_message

# Импорт форматтера
from matunya_bot_final.help_core.solvers.task_8.task_8_text_formatter import render_node, fmt_number

router = Router()
logger = logging.getLogger(__name__)

__all__ = ("task_8_router",)
task_8_router = router

THEMES: tuple[str, ...] = (
    "integer_expressions",
    "powers_and_roots",
)

def _build_question_text(task_data: dict) -> str:
    """Собирает текст задачи из дерева и переменных."""
    tree = task_data.get("expression_tree")
    if not tree:
        return "🔴 Ошибка: expression_tree отсутствует в данных задачи!"

    # Пытаемся отрендерить
    try:
        expr_str = render_node(tree)
    except Exception as e:
        logger.error(f"Task 8 Render Error: {e}", exc_info=True)
        return f"🔴 Исключение при рендеринге: {e}"

    # Если вернулась пустота - выводим отладку прямо в чат
    if not expr_str:
        debug_tree = json.dumps(tree, ensure_ascii=False, indent=2)
        return (
            f"🔴 Ошибка: Форматтер вернул пустую строку!\n\n"
            f"<b>Сырое дерево (для анализа):</b>\n"
            f"<pre>{debug_tree}</pre>"
        )

    # Штатный режим
    if tree.get("type") == "range_query":
        text = f"Посчитай, сколько целых чисел находится между <b>{expr_str}</b>?"
    else:
        text = f"Вычисли значение выражения:\n\n<b>{expr_str}</b>"

        vars_disp = task_data.get("variables_display") or task_data.get("variables")
        if vars_disp:
            vars_list = []
            for k, v in vars_disp.items():
                val_str = fmt_number(v) if isinstance(v, (int, float)) else str(v)
                vars_list.append(f"{k} = {val_str}")
            vars_str = ", ".join(vars_list)
            text += f"\n\nпри <b>{vars_str}</b>"

    return text


def _pick_task_for_theme(tasks: Iterable[dict], theme_key: str) -> dict | None:
    items = list(tasks)
    if not items: return None
    pool = [t for t in items if t.get("subtype") == theme_key]
    if not pool: pool = items
    return random.choice(pool)


# Хендлеры без изменений, кроме вызова _build_question_text внутри send_task_8

@router.callback_query(TaskCallback.filter((F.action == "select_task") & (F.task_type == 8)))
async def handle_task_8(query: CallbackQuery, state: FSMContext, callback_data: TaskCallback, bot: Bot) -> None:
    if callback_data.question_num and callback_data.question_num != 8: return
    await query.answer()
    chat_id = query.message.chat.id
    await cleanup_messages_by_category(bot, state, chat_id, "menus")
    current_key = THEMES[0]
    overview_text = generate_task_8_overview_text(list(THEMES), current_key)
    keyboard = get_task_8_carousel_keyboard(list(THEMES), current_key)
    await send_tracked_message(bot=bot, chat_id=chat_id, state=state, text=overview_text, reply_markup=keyboard, message_tag="task_8_carousel", category="menus", parse_mode="HTML")
    await state.update_data(current_theme=current_key)

@router.callback_query(TaskCallback.filter(F.action == "8_carousel_nav"))
async def task_8_carousel_nav(query: CallbackQuery, callback_data: TaskCallback, bot: Bot) -> None:
    current_key = callback_data.subtype_key or THEMES[0]
    overview_text = generate_task_8_overview_text(list(THEMES), current_key)
    keyboard = get_task_8_carousel_keyboard(list(THEMES), current_key)
    try: await query.message.edit_text(overview_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception: await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)
    await query.answer()

@router.callback_query(TaskCallback.filter(F.action == "8_select_theme"))
async def task_8_open_selected(query: CallbackQuery, state: FSMContext, callback_data: TaskCallback, bot: Bot) -> None:
    await query.answer()
    theme_key = callback_data.subtype_key or THEMES[0]
    tasks_object = TASKS_DB.get("8", {})
    tasks = tasks_object.get("tasks", []) if isinstance(tasks_object, dict) else tasks_object
    chat_id = query.message.chat.id
    if not tasks:
        await bot.send_message(chat_id, "Пока нет заданий для этой темы.")
        return
    task_data = _pick_task_for_theme(tasks, theme_key)
    if not task_data:
        await bot.send_message(chat_id, "Не удалось подобрать задание.")
        return
    await state.update_data(current_theme=theme_key)
    await send_task_8(query, bot, state, task_data)

@router.callback_query(F.data == "back_to_carousel_8")
async def back_to_carousel_8(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await callback.answer()
    chat_id = callback.message.chat.id
    await cleanup_messages_by_category(bot, state, chat_id, "tasks")
    await cleanup_messages_by_category(bot, state, chat_id, "menus")
    current_key = THEMES[0]
    overview_text = generate_task_8_overview_text(list(THEMES), current_key)
    keyboard = get_task_8_carousel_keyboard(list(THEMES), current_key)
    await send_tracked_message(bot=bot, chat_id=chat_id, state=state, text=overview_text, reply_markup=keyboard, message_tag="task_8_carousel", category="menus", parse_mode="HTML")
    await state.update_data(current_theme=current_key)

async def send_task_8(query: CallbackQuery, bot: Bot, state: FSMContext, task_data: dict) -> None:
    chat_id = query.message.chat.id
    await cleanup_messages_by_category(bot, state, chat_id, "tasks")
    footer_text = await compose_after_task_message_from_state(state)

    question_text = _build_question_text(task_data)

    if "Ответ" not in question_text and "🔴" not in question_text:
        question_text = question_text.strip() + "\n\nОтвет: ____________"

    topic_key = task_data.get("subtype") or "default"
    topic_name = get_current_theme_name(topic_key)

    final_text = (
        f"<b>Задание 8:</b> {topic_name}\n\n"
        f"{question_text}\n\n\n"
        f"{footer_text}"
    )

    keyboard = get_after_task_keyboard(task_number=8, task_subtype=topic_key)

    await send_tracked_message(bot=bot, chat_id=chat_id, state=state, text=final_text, reply_markup=keyboard, message_tag="task_8_main_text", category="tasks", parse_mode="HTML")
    await state.update_data(task_8_data=task_data)
