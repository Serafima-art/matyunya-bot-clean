from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.navigation.navigation import back_and_main_kb

THEMES_DISPLAY = {
    "algebraic_expressions": "🧮 Алгебраические выражения",
    "equations": "📐 Уравнения",
    "inequalities": "⚖️ Неравенства",
    "systems_equations": "🔢 Системы уравнений",
    "systems_inequalities": "🧠 Системы неравенств",
}


def generate_task_20_overview_text(themes_list: list, current_key: str) -> str:
    header = "📘 <b>Задание 20: Выбери тему</b>\n"

    theme_lines = []
    for key in themes_list:
        display_name = THEMES_DISPLAY.get(key, f"❓ {key}")
        if key == current_key:
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


def get_task_20_carousel_keyboard(
    themes_list: list,
    current_key: str,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

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
                action="20_carousel_nav",
                subtype_key=next_key,
                task_type=20,
            ).pack(),
        ),
        InlineKeyboardButton(
            text="✅ Открыть задание",
            callback_data=TaskCallback(
                action="20_select_theme",
                subtype_key=current_key,
                task_type=20,
            ).pack(),
        ),
    )

    nav = back_and_main_kb()
    for row in nav.inline_keyboard:
        builder.row(*row)

    return builder.as_markup()


def get_current_theme_name(theme_key: str) -> str:
    return THEMES_DISPLAY.get(theme_key, f"❓ {theme_key}")
