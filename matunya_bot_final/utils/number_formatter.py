# matunya_bot_final/utils/number_formatter.py
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Union

Number = Union[float, int, str]

def format_oge_number(value: Union[Number, None]) -> Union[int, str, None]:
    """
    Универсальный форматер чисел для ответов ОГЭ:
    - 5.0 -> 5
    - 0.8 -> "0,8"
    - 1.25 -> "1,25"
    - "43,5" -> "43,5"
    - None -> None

    ⚠️ Никогда не падает
    """
    if value is None:
        return None

    # Приводим строку ОГЭ-формата к float-совместимой
    try:
        if isinstance(value, str):
            normalized = value.replace(",", ".")
        else:
            normalized = value

        v = float(normalized)

    except (ValueError, TypeError):
        # Если вообще не число — возвращаем как есть
        return value

    # Убираем погрешности float около целых
    if abs(v - round(v)) < 1e-9:
        return int(round(v))

    # Форматируем без лишних нулей
    text = f"{v:.6f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")
