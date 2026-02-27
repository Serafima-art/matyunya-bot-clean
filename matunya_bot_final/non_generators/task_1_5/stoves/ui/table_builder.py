"""
Table builder for Stoves (Tasks 1–5).

Формирует текстовую таблицу печей для Telegram.
Таблица строится по данным из table_context JSON.

Архитектура:
non_generators → JSON (источник истины) → UI builder → вывод в боте
"""

from typing import Dict, Any


def build_stoves_table(table_context: Dict[str, Any]) -> str:
    """
    Возвращает форматированную таблицу печей.

    :param table_context: dict из JSON:
        {
            "stoves": [
                {
                    "stove_no": 1,
                    "type": "wood",
                    "volume_range": "10–15",
                    "mass": 35,
                    "cost": 19000
                },
                ...
            ]
        }
    :return: str — текст таблицы для Telegram
    """

    stoves = table_context["stoves"]

    rows_data = []

    # Преобразуем тип к красивому виду
    type_map = {
        "wood": "дровяная",
        "electric": "электрическая"
    }

    for stove in stoves:
        rows_data.append({
            "num": str(stove["stove_no"]),
            "type": type_map.get(stove["type"], stove["type"]),
            "volume": stove["volume_range"],
            "mass": str(stove["mass"]),
            "cost": f"{stove['cost']:,}".replace(",", " ")
        })

    # Заголовки
    headers = {
        "num": "№",
        "type": "Тип",
        "volume": "Объём (м³)",
        "mass": "Масса (кг)",
        "cost": "Стоимость (руб.)"
    }

    # Вычисляем ширины колонок
    num_width = max(len(row["num"]) for row in rows_data + [{"num": headers["num"]}])
    type_width = max(len(row["type"]) for row in rows_data + [{"type": headers["type"]}])
    volume_width = max(len(row["volume"]) for row in rows_data + [{"volume": headers["volume"]}])
    mass_width = max(len(row["mass"]) for row in rows_data + [{"mass": headers["mass"]}])
    cost_width = max(len(row["cost"]) for row in rows_data + [{"cost": headers["cost"]}])

    # Формируем шапку
    header = (
        f"{headers['num'].ljust(num_width)}   "
        f"{headers['type'].ljust(type_width)}   "
        f"{headers['volume'].ljust(volume_width)}   "
        f"{headers['mass'].ljust(mass_width)}   "
        f"{headers['cost'].ljust(cost_width)}"
    )

    separator = "-" * len(header)

    lines = [header, separator]

    for row in rows_data:
        line = (
            f"{row['num'].ljust(num_width)}   "
            f"{row['type'].ljust(type_width)}   "
            f"{row['volume'].ljust(volume_width)}   "
            f"{row['mass'].ljust(mass_width)}   "
            f"{row['cost'].ljust(cost_width)}"
        )
        lines.append(line)

    return "<pre>\n" + "\n".join(lines) + "\n</pre>"
