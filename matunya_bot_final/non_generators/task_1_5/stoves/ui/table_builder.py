"""
Table builder for Stoves (Tasks 1–5).
Левое выравнивание, расширенная мобильная версия (~340px).
"""

from typing import Dict, Any


def build_stoves_table(table_context: Dict[str, Any]) -> str:

    stoves = table_context.get("stoves") or []

    if not stoves:
        return "<pre>Нет данных о печах</pre>"

    type_map = {
        "wood": "дровяная",
        "electric": "электрическая",
    }

    rows = []

    for stove in stoves:
        num = str(stove.get("stove_no", ""))
        typ = type_map.get(stove.get("type"), stove.get("type", ""))
        volume = str(stove.get("volume_range", ""))
        mass = str(stove.get("mass", ""))

        cost = stove.get("cost", "")
        if isinstance(cost, int):
            cost = str(cost)  # без пробелов

        rows.append({
            "num": num,
            "type": typ,
            "volume": volume,
            "mass": mass,
            "cost": cost,
        })

    # Заголовки
    headers_top = {
        "num": "№",
        "type": "Тип",
        "volume": "Объём",
        "mass": "Масса",
        "cost": "Цена",
    }

    headers_bottom = {
        "num": "",
        "type": "",
        "volume": "(м³)",
        "mass": "(кг)",
        "cost": "(руб)",
    }

    # Немного увеличенные ширины
    num_w = max(2, max(len(r["num"]) for r in rows))
    type_w = max(12, max(len(r["type"]) for r in rows))
    volume_w = max(8, max(len(r["volume"]) for r in rows))
    mass_w = max(6, max(len(r["mass"]) for r in rows))
    cost_w = max(8, max(len(r["cost"]) for r in rows))

    def line(values):
        return (
            f"{values[0].ljust(num_w)}"
            f"{values[1].ljust(type_w)}  "
            f"{values[2].ljust(volume_w)}  "
            f"{values[3].ljust(mass_w)}  "
            f"{values[4].ljust(cost_w)}"
        )

    lines = []

    lines.append(line([
        headers_top["num"],
        headers_top["type"],
        headers_top["volume"],
        headers_top["mass"],
        headers_top["cost"],
    ]))

    lines.append(line([
        headers_bottom["num"],
        headers_bottom["type"],
        headers_bottom["volume"],
        headers_bottom["mass"],
        headers_bottom["cost"],
    ]))

    lines.append("-" * (len(lines[0]) - 3)) # разделитель

    for r in rows:
        lines.append(line([
            r["num"],
            r["type"],
            r["volume"],
            r["mass"],
            r["cost"],
        ]))

    return "<pre>\n" + "\n".join(lines) + "\n</pre>"
