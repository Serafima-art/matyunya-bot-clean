# matunya_bot_final/utils/display.py

from __future__ import annotations

import re

_SUPERSCRIPT_MAP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³",
    "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷",
    "8": "⁸", "9": "⁹",
    "-": "⁻", "+": "⁺"
}


def to_superscript(value: int | str) -> str:
    s = str(value)
    return "".join(_SUPERSCRIPT_MAP.get(ch, ch) for ch in s)


def format_number(value: int | float | str) -> str:
    """
    Универсальный форматтер числа:
    - точка -> запятая
    - - -> −
    - убирает ,0 и ,00
    """

    s = str(value)

    # точка -> запятая
    s = re.sub(r'(?<=\d)\.(?=\d)', ',', s)

    # минус красивый
    s = s.replace("-", "−")

    # убрать ,0 / ,00
    s = re.sub(r',0+(?!\d)', '', s)

    return s


def format_power(base: int | str, power: int | str) -> str:
    """
    2, 6 -> 2⁶
    """
    return f"{base}{to_superscript(power)}"
