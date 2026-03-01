"""
UI builder для вопроса 1 (stove_match_table).
Компактная мобильная версия.
"""

from typing import Dict, Any


def build_stoves_question_table(question: Dict[str, Any]) -> str:

    input_data = question["input_data"]
    columns = input_data["columns_order"]
    label = input_data["column_label"]

    values = [str(v) for v in columns]

    # ---- определяем ширину каждой колонки ----
    col_widths = [max(len(v), 5) for v in values]  # минимум 5, чтобы ___ не ломалось

    # ---- строка с числами ----
    values_line_parts = [
        v.center(col_widths[i])
        for i, v in enumerate(values)
    ]
    values_line = "   ".join(values_line_parts)

    # ---- строка для ответа ----
    answer_parts = [
        "___".center(col_widths[i])
        for i in range(len(values))
    ]
    answer_line = "   ".join(answer_parts)

    # ---- длина линии ----
    line_length = max(len(values_line), len(label))
    separator = "─" * line_length

    lines = [
        label,
        separator,
        values_line,
        "",
        "Номер печи",
        separator,
        answer_line,
    ]

    return "<pre>\n" + "\n".join(lines) + "\n</pre>"
