from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Используем CallbackData, как и в заданиях 1-5
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.navigation.navigation import back_and_main_kb

# Метаданные тем для отображения
THEMES_DISPLAY = {
    "read_graphs": "📊 Чтение графиков функций",
    "transformations": "🔄 Растяжения и сдвиги"
}

def generate_task_11_overview_text(themes_list: list, current_key: str) -> str:
    """
    Генерирует текст обзора для задания 11 (карусель с 2 темами).
    """
    header = "📘 <b>Задание 11: Выбери тему</b>\n"

    theme_lines = []
    for key in themes_list:
        display_name = THEMES_DISPLAY.get(key, f"❓ {key}")

        if key == current_key:
            # Текущая тема подсвечена стрелкой ▶️
            if len(display_name) > 2:
                name_part = display_name[2:]  # убираем эмодзи
                theme_lines.append(f"▶️ <b>{name_part}</b>")
            else:
                theme_lines.append(f"▶️ <b>{display_name}</b>")
        else:
            theme_lines.append(display_name)

    themes_section = "\n".join(theme_lines)
    footer = "\nИспользуй стрелку ▶️ для переключения\nи нажми «✅ Открыть задание»!"

    return header + "\n" + themes_section + "\n" + footer


def get_task_11_carousel_keyboard(
    themes_list: list,
    current_key: str
) -> InlineKeyboardMarkup:
    """
    Создает inline-карусель для выбора темы Задания 11.
    """
    builder = InlineKeyboardBuilder()

    try:
        current_index = themes_list.index(current_key)
    except ValueError:
        current_index = 0
        current_key = themes_list[0]

    # Следующая тема по кругу
    next_index = (current_index + 1) % len(themes_list)
    next_key = themes_list[next_index]

    # --- Первый ряд: стрелка и "Открыть задание"
    builder.row(
        InlineKeyboardButton(
            text="▶️",
            callback_data=TaskCallback(
                action="11_carousel_nav",
                subtype_key=next_key
            ).pack()
        ),
        InlineKeyboardButton(
            text="✅ Открыть задание",
            callback_data=TaskCallback(
                action="select_subtype",
                subtype_key=current_key
            ).pack()
        )
    )

    nav = back_and_main_kb()  # ⬅️ back_to_parts + 🏠 back_to_main_menu
    for row in nav.inline_keyboard:
        builder.row(*row)

    return builder.as_markup()


def get_current_theme_name(theme_key: str) -> str:
    """Возвращает отображаемое название темы"""
    return THEMES_DISPLAY.get(theme_key, f"❓ {theme_key}")
