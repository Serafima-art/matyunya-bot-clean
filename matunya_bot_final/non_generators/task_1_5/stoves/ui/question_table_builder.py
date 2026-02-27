"""
UI builder для вопроса 1 (stove_match_table).

Строит вторую таблицу:
Объём/Масса/Стоимость  |  значения
Номер печи             |  ___ ___ ___
"""

from typing import Dict, Any


def build_stove_question_table(question: Dict[str, Any]) -> str:
    """
    Формирует вторую таблицу для Q1 (match_volume / match_weight / match_cost).
    """

    input_data = question["input_data"]
    columns = input_data["columns_order"]
    label = input_data["column_label"]
    narrative = question["narrative"]

    # --- форматируем значения ---
    values = []

    for val in columns:
        if narrative == "match_cost":
            formatted = f"{val:,}".replace(",", " ")
        else:
            formatted = str(val)

        values.append(formatted)

    header_1 = label
    header_2 = "Номер печи"

    first_col_width = max(len(header_1), len(header_2))
    value_width = max(len(v) for v in values)

    row_1 = header_1.ljust(first_col_width) + "   "
    for v in values:
        row_1 += v.center(value_width) + "   "

    row_2 = header_2.ljust(first_col_width) + "   "
    for _ in values:
        row_2 += "___".center(value_width) + "   "

    separator = "-" * max(len(row_1), len(row_2))

    lines = [
        row_1.rstrip(),
        separator,
        row_2.rstrip()
    ]

    return "<pre>\n" + "\n".join(lines) + "\n</pre>"
