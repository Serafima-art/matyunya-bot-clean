"""
task6_text_formatter.py — единый форматер и валидатор для всех подтипов задания №6.

Цели:
• устранить деление на ноль (в том числе «приобретённое»);
• очистить выражения от кракозябр, странных минусов, неразрывных пробелов;
• обернуть отрицательные множители и делители в скобки;
• унифицировать запись (запятые, пробелы, точки, умножение «·»);
• вернуть None, если выражение некорректно — генератор тогда делает перегенерацию.
"""

from __future__ import annotations
import re
from decimal import Decimal, InvalidOperation
import random
from fractions import Fraction

# --- 🔧 Базовые регулярки ---
_NEG_AFTER_OP_RE = re.compile(r'([·*/])\s*(−|-)\s*(\d+(?:[.,]\d+)?)')
_BAD_TRAILING_OP_RE = re.compile(r'[\+\-\*/:]$')
_NON_BREAK_SPACE_RE = re.compile(r'[\u00A0\u202F]')

# --- 🔍 Нормализация выражения ---
def normalize_expression(expr: str) -> str:
    """Приводит выражение к стандартной форме."""
    if not expr:
        return ""

    s = expr
    # символы и пробелы
    s = _NON_BREAK_SPACE_RE.sub(" ", s)
    s = s.replace("−", "-").replace("–", "-").replace("—", "-")
    s = s.replace(":", "/")
    s = s.replace("×", "·").replace("*", "·")
    s = re.sub(r"\s+", " ", s.strip())

    # десятичная точка -> запятая
    s = re.sub(r"(?<=\d)\.(?=\d)", ",", s)

    # пробелы вокруг знаков
    s = re.sub(r"\s*([+\-·/])\s*", r" \1 ", s)
    s = re.sub(r"\s+", " ", s.strip())

    return s


def fix_negative_after_operators(expr: str) -> str:
    """Обернуть отрицательные числа после · или / в скобки."""
    return _NEG_AFTER_OP_RE.sub(r'\1(−\3)', expr)


def validate_expression(expr: str) -> bool:
    """Проверяет, можно ли безопасно вычислить выражение."""
    if not expr or _BAD_TRAILING_OP_RE.search(expr):
        return False

    expr_eval = expr.replace("·", "*").replace(",", ".")
    try:
        val = Decimal(str(eval(expr_eval)))
        if val.is_nan() or val.is_infinite():
            return False
    except (InvalidOperation, ZeroDivisionError, SyntaxError, NameError):
        return False
    except Exception:
        return False
    return True


def prepare_expression(expr: str) -> str | None:
    """
    Универсальный фильтр для задания №6:
    нормализует, исправляет и проверяет выражение.
    Возвращает «чистую» строку или None, если выражение нужно перегенерировать.
    """
    if not expr or not isinstance(expr, str):
        return None

    s = normalize_expression(expr)
    s = fix_negative_after_operators(s)

    if not validate_expression(s):
        return None

    return s

def _fmt(x: float) -> str:
    """Format numbers for expressions using comma separator."""
    s = f"{x:.2f}".replace(".", ",")
    s = s.rstrip("0").rstrip(",")
    return f"({s})" if x < 0 else s


def _fmt_answer(x: float, use_comma: bool = False) -> str:
    """
    Форматирует ответ без скобок, по умолчанию с точкой, максимум двумя знаками.
    Если use_comma=True, заменяет точку на запятую и гарантирует наличие запятой.
    """
    try:
        val = float(x)
        s = f"{val:.2f}"
    except Exception:
        s = str(x)

    s = s.rstrip("0").rstrip(".")

    if s in ("-0",):
        s = "0"

    if use_comma:
        if "." in s:
            s = s.replace(".", ",")
        if "," not in s and any(ch.isdigit() for ch in s):
            s = f"{s},0"
    else:
        if "." not in s and any(ch.isdigit() for ch in s):
            if "," in str(x):
                s = s.replace(",", ".")
    return s





__all__ = [
    "normalize_expression",
    "fix_negative_after_operators",
    "validate_expression",
    "prepare_expression",
    "_fmt",
    "_fmt_answer",
]
