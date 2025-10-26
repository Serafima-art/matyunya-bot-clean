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

_ALLOWED = "0123456789 +-−·:/()"

# --- 🔍 Нормализация выражения ---
def normalize_expression(expr: str) -> str:
    """
    Приводит выражение к стандартной, идеально отформатированной форме.
    Финальная, надежная версия.
    """
    if not expr:
        return ""

    s = expr

    # 1. Базовая стандартизация символов
    s = _NON_BREAK_SPACE_RE.sub(" ", s)
    s = s.replace("−", "-").replace("–", "-").replace("—", "-")
    s = s.replace("×", "*").replace("·", "*") # Временно приводим все умножения к *
    s = s.replace(":", "/") # Временно приводим все деления к /

    # 2. Заменяем десятичную точку на запятую
    s = re.sub(r"(?<=\d)\.(?=\d)", ",", s)

    # 3. ★★★ НОВАЯ, ПРОСТАЯ И НАДЕЖНАЯ ЛОГИКА ★★★

    # Сначала "склеиваем" все, что может быть дробью
    s = re.sub(r'\s*/\s*', '/', s)

    # Теперь расставляем пробелы вокруг всех операторов
    operators = ['+', '-', '*', '/']
    for op in operators:
        s = s.replace(op, f' {op} ')

    # 4. Возвращаем красивые символы умножения и деления
    s = re.sub(r'\*', ' · ', s)
    s = re.sub(r'/', ' : ', s) # Сначала все деления становятся ':',

    # А теперь исправляем только те, что внутри дробей
    s = re.sub(r'(\d+)\s*:\s*(\d+)', r'\1/\2', s) # Находим "цифра : цифра" и меняем на "цифра/цифра"

    # 5. Убираем лишние пробелы
    s = re.sub(r'\s+', ' ', s).strip()

    s = s.replace(" · ", " ⋅ ")

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

def prepare_expression(expr: str) -> str:
    """
    Форматирует выражение для красивого отображения:
    - заменяет ^n и ^-n на надстрочные символы (², ³, ⁻² и т.д.)
    - заменяет * на ·
    - убирает двойные пробелы.
    """
    # --- таблица надстрочных символов ---
    superscripts = {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "-": "⁻",
    }

    # заменяем ^n (например ^2 или ^-3) на надстрочные символы
    def replace_power(match):
        power = match.group(1)  # например "-3"
        return "".join(superscripts.get(ch, ch) for ch in power)

    expr = re.sub(r"\^(-?\d+)", replace_power, expr)
    expr = expr.replace("*", "·")
    expr = expr.replace("  ", " ").strip()
    return expr


def prepare_expression(src: str) -> str | None:
    """??????? ???????? ?????????. ?????????? None, ???? ? ?????????? ??? ??????????."""
    if src is None:
        return None

    s = (src.replace("\u00a0", " ")
             .replace("\u202f", " ")
             .strip())

    # ????????? ?????? ?????????? ???????
    s = "".join(ch for ch in s if ch in _ALLOWED)

    # ????????????
    s = s.replace("--", "+")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("-", "−")  # ?????? ?????

    # ???? ????? ?????? ??? ?? ?????, ?? ?????????? ? ??????? ????????? ??????????
    if not s or not re.search(r"[0-9]", s):
        return None
    if not re.search(r"[/:·+\-−()]", s):
        return None

    # ??????? ?????? ?? ?????? ??????
    if re.search(r"\(\s*\)", s):
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
