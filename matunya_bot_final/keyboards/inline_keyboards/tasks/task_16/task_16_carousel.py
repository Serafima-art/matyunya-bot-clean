# -*- coding: utf-8 -*-
"""Inline keyboard carousel for Task 16: Geometry (Circle)."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.navigation.navigation import back_and_main_kb

# -----------------------------------------------------------------------------
# Темы задания 16 и их отображение
# -----------------------------------------------------------------------------
THEMES_DISPLAY_16 = {
    "central_and_inscribed_angles": "📐 Центральные и вписанные углы",
    "circle_elements_relations": "🧭 Касательная, хорда, секущая, радиус",
    "circle_around_polygon": "🔵 Окружность вокруг многоугольника",
}


# -----------------------------------------------------------------------------
# Текст карусели
# -----------------------------------------------------------------------------
def generate_task_16_overview_text(
    themes_dict: dict[str, dict],
    current_key: str,
) -> str:
    """Return formatted carousel overview text for Task 16."""
    header = "📙 <b>Задание 16:</b> <i>Окружность, круг и их элементы</i>\n"

    theme_lines: list[str] = []
    for key in themes_dict.keys():
        display_name = THEMES_DISPLAY_16.get(key, f"❓ {key}")
        if key == current_key:
            # убираем цветной квадрат у активной темы (как в задании 15)
            if len(display_name) > 2:
                name_part = display_name[2:]
                theme_lines.append(f"▶️ <b>{name_part}</b>")
            else:
                theme_lines.append(f"▶️ <b>{display_name}</b>")
        else:
            theme_lines.append(display_name)

    themes_section = "\n".join(theme_lines)
    footer = "\nИспользуй стрелку ▶️ для переключения\nи нажми «✅ Открыть задание»!"
    return header + "\n" + themes_section + "\n" + footer


# -----------------------------------------------------------------------------
# Клавиатура карусели
# -----------------------------------------------------------------------------
def get_task_16_carousel_keyboard(
    themes_dict: dict[str, dict],
    current_key: str,
) -> InlineKeyboardMarkup:
    """Build keyboard for Task 16 carousel (no flicker)."""
    builder = InlineKeyboardBuilder()

    themes_list = list(themes_dict.keys())

    try:
        current_index = themes_list.index(current_key)
    except ValueError:
        current_index = 0
        current_key = themes_list[0]

    next_index = (current_index + 1) % len(themes_list)
    next_key = themes_list[next_index]

    builder.row(
        InlineKeyboardButton(
            text="▶️",
            callback_data=TaskCallback(
                action="16_carousel_nav",
                subtype_key=next_key,
                task_type=16,
            ).pack(),
        ),
        InlineKeyboardButton(
            text="✅ Открыть задание",
            callback_data=TaskCallback(
                action="16_select_theme",
                subtype_key=current_key,
                task_type=16,
            ).pack(),
        ),
    )

    nav = back_and_main_kb()
    for row in nav.inline_keyboard:
        builder.row(*row)

    return builder.as_markup()


# -----------------------------------------------------------------------------
# Утилита: человекочитаемое имя темы
# -----------------------------------------------------------------------------
def get_task_16_theme_name(theme_key: str) -> str:
    """Return human-readable name for given Task 16 theme key."""
    return THEMES_DISPLAY_16.get(theme_key, f"❓ {theme_key}")
