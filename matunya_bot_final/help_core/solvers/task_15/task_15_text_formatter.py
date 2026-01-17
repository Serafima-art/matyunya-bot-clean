# matunya_bot_final/help_core/solvers/task_15/task_15_text_formatter.py
# -*- coding: utf-8 -*-

"""
Legacy wrapper for Task 15 number formatting.

В проекте используется единый форматер ответов ОГЭ:
matunya_bot_final/utils/number_formatter.py

Этот файл оставлен ради совместимости со старыми импортами.
"""

from __future__ import annotations

from typing import Union
from matunya_bot_final.utils.number_formatter import format_oge_number


def format_number(value: Union[float, int, None]) -> Union[int, str, None]:
    return format_oge_number(value)
