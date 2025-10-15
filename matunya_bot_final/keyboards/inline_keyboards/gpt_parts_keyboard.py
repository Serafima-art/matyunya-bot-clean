import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback

# ======================
# 🎯 Клавиатуры
# ======================

def parts_menu() -> InlineKeyboardMarkup:
    """Экран выбора части: две кнопки в верхнем ряду + отдельная кнопка 'В главное меню'."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📘 Часть 1", callback_data="part_1"),
                InlineKeyboardButton(text="📗 Часть 2", callback_data="part_2"),
            ],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="to_main_menu")]
        ]
    )

# --- НОВЫЕ, "УМНЫЕ" КЛАВИАТУРЫ ---

def part1_tasks_menu() -> InlineKeyboardMarkup:
    """
    Часть 1. ВЕРСИЯ 4.0: Возвращаем визуальный ряд, но с "умным" TaskCallback.
    """
    # Убедись, что этот импорт есть вверху файла:
    # from core.callbacks.tasks_callback import TaskCallback

    items = [
        # Кнопка 1-5 теперь тоже использует TaskCallback
        ("📘 1–5", TaskCallback(action="show_task_1_5_carousel").pack())
    ]

    emoji_map = {
        6: "➗", 7: "📐", 8: "🔢", 9: "📊", 10: "📉", 11: "📈", 12: "🔍",
        13: "🧮", 14: "📝", 15: "📏", 16: "📦", 17: "📒", 18: "📚", 19: "🧾",
    }
    # Кнопки 6-19 тоже переводим на TaskCallback
    for n in range(6, 20):
        items.append(
            (
                f"{emoji_map.get(n, '🔹')}{n}",
                TaskCallback(action="select_task", task_type=n, question_num=n).pack(),
            )
        )

    # --- ВОТ НАША СТАРАЯ, НАДЕЖНАЯ ЛОГИКА СБОРКИ ---
    rows = []
    row = []
    for text, cb in items:
        row.append(InlineKeyboardButton(text=text, callback_data=cb))
        if len(row) == 5: # Собираем по 5 кнопок в ряд
            rows.append(row)
            row = []
    if row: # Добавляем последний неполный ряд, если он есть
        rows.append(row)
    # ---------------------------------------------

    rows.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def part2_tasks_menu() -> InlineKeyboardMarkup:
    """
    Часть 2. ВЕРСИЯ 4.0: Использует "умный" TaskCallback.
    """
    items = []
    emoji_map = {20: "📘", 21: "➗", 22: "📐", 23: "🔢", 24: "📊", 25: "🧮"}

    for n in range(20, 26):
        callback_data = TaskCallback(
            action="select_task",
            task_type=n,
            question_num=n,
        ).pack()

        items.append(
            (
                f"{emoji_map.get(n, '🔹')}{n}",
                callback_data,
            )
        )

    # Собираем ряды по 3 кнопки
    rows = []
    for i in range(0, len(items), 3):
        chunk = items[i:i+3]
        rows.append([InlineKeyboardButton(text=t, callback_data=cb) for t, cb in chunk])

    rows.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
