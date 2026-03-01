from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Используем CallbackData для "умных" кнопок
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.navigation.navigation import back_and_main_kb

# Метаданные подтипов для отображения
SUBTYPES_DISPLAY = {
    "stoves": "🔥 Печи",
    "paper": "📄 Бумага",
    "apartment": "🏠 Квартира",
    "tires": "🚗 Шины",
    "plot": "🌱 Участок"
}

def generate_task_1_5_overview_text(subtypes_list: list, current_key: str) -> str:
    """
    Генерирует текст обзора карусели с полным списком подтипов и выделением текущего

    Args:
        subtypes_list: Список ключей подтипов ["stoves", "paper", "apartment", "tires", "plot"]
        current_key: Текущий активный ключ подтипа

    Returns:
        Отформатированный текст карусели с заголовком, списком и подвалом
    """
    # Заголовок
    header = "📘 <b>Задания 1-5: Выбери подтип</b>\n"

    # Генерируем список подтипов
    subtype_lines = []
    for key in subtypes_list:
        display_name = SUBTYPES_DISPLAY.get(key, f"❓ {key}")

        if key == current_key:
            # --- НАША НОВАЯ, УМНАЯ ЛОГИКА ЗАМЕНЫ ---
            # Отделяем эмодзи (первый символ) от названия
            parts = display_name.split(maxsplit=1)
            if len(parts) == 2:
                # Если удалось разделить, берем только текстовую часть
                name_part = parts[1]
            else:
                # Если не удалось (вдруг нет пробела), берем все как есть
                name_part = display_name

            subtype_lines.append(f"▶️ <b>{name_part}</b>")
            # --------------------------------------------
        else:
            # Для невыбранных элементов используем полное значение
            subtype_lines.append(display_name)

    # Объединяем список
    subtypes_section = "\n".join(subtype_lines)

    # Подвал
    footer = "\nИспользуй стрелку ▶️ для навигации\nи нажми «✅ Открыть задание» для старта!"

    # Собираем полный текст
    return header + "\n" + subtypes_section + "\n" + footer

def get_task_1_5_carousel_keyboard(
    subtypes_list: list,
    current_key: str
) -> InlineKeyboardMarkup:
    """
    Создает "умную" клавиатуру-карусель для выбора подтипа Заданий 1-5.

    Args:
        subtypes_list: Список ключей подтипов ["stoves", "paper", "apartment", "tires", "plot"]
        current_key: Текущий активный ключ подтипа
    """
    builder = InlineKeyboardBuilder()

    try:
        current_index = subtypes_list.index(current_key)
    except ValueError:
        # Если текущий ключ не найден, берем первый
        current_index = 0
        current_key = subtypes_list[0]

    # --- НАША НОВАЯ ЛОГИКА: ТОЛЬКО ВПЕРЕД ---
    # Кнопка "вперед" (▶️) будет показывать следующий элемент, зацикливаясь
    next_index = (current_index + 1) % len(subtypes_list)
    next_key = subtypes_list[next_index]

    # --- НАША НОВАЯ, ОДНОРЯДНАЯ ЛОГИКА ---
    builder.row(
        # Кнопка "вперед" (теперь она слева)
        InlineKeyboardButton(
            text="▶️",
            callback_data=TaskCallback(
                action="1-5_carousel_nav",
                subtype_key=next_key
            ).pack()
        ),
        # Кнопка выбора (теперь она справа)
        InlineKeyboardButton(
            text="✅ Открыть задание",
            callback_data=TaskCallback(
                action="1-5_select_subtype",
                subtype_key=current_key
            ).pack()
        )
    )

    nav = back_and_main_kb  # готовая пара кнопок из общего файла
    for row in back_and_main_kb().inline_keyboard:
        builder.row(*row)

    return builder.as_markup()


def get_current_subtype_name(subtype_key: str) -> str:
    """Возвращает отображаемое название подтипа"""
    return SUBTYPES_DISPLAY.get(subtype_key, f"❓ {subtype_key}")
