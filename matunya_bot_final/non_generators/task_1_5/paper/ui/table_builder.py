"""
Table builder for Paper (Tasks 1–5).

Формирует текстовую таблицу для Telegram при нажатии кнопки «Вопрос 1».
Таблица строится по данным из table_context JSON.

Архитектура:
non_generators → JSON (источник истины) → UI builder → вывод в боте
"""

from typing import Dict, Any


def build_paper_table(table_context: Dict[str, Any]) -> str:
    """
    Возвращает форматированную таблицу размеров бумаги.

    :param table_context: dict из JSON:
        {
            "table_order": ["A1", "A4", "A6", "A7"],
            "formats_data": { ... }
        }
    :return: str — текст таблицы для Telegram
    """

    table_order = table_context["table_order"]
    formats_data = table_context["formats_data"]

    rows_data = []

    # Формируем строки таблицы
    for index, format_name in enumerate(table_order, start=1):
        format_info = formats_data[format_name]

        rows_data.append({
            "num": str(index),
            "length": str(format_info["length_mm"]),
            "width": str(format_info["width_mm"])
        })

    # Заголовки
    headers = {
        "num": "№ Листа",
        "length": "Длина (мм)",
        "width": "Ширина (мм)"
    }

    # Вычисляем ширины колонок
    num_width = max(len(row["num"]) for row in rows_data + [{"num": headers["num"]}])
    length_width = max(len(row["length"]) for row in rows_data + [{"length": headers["length"]}])
    width_width = max(len(row["width"]) for row in rows_data + [{"width": headers["width"]}])

    # Формируем шапку
    header = (
        f"{headers['num'].ljust(num_width)}   "
        f"{headers['length'].ljust(length_width)}   "
        f"{headers['width'].ljust(width_width)}"
    )

    separator = "-" * (len(header))

    # Формируем строки таблицы
    lines = [header, separator]

    for row in rows_data:
        line = (
            f"{row['num'].ljust(num_width)}   "
            f"{row['length'].ljust(length_width)}   "
            f"{row['width'].ljust(width_width)}"
        )
        lines.append(line)

    # Telegram лучше отображает таблицы в <pre>
    return "<pre>\n" + "\n".join(lines) + "\n</pre>"
