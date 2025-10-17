"""Generator for task 20 rational_inequalities subtype (ОГЭ-2026).

Генерирует четыре вида рациональных неравенств:
1) compare_unit_fractions_linear:   1/x ⊙ 1/(x−a)
2) const_over_quadratic_nonpos_nonneg:  −C/(x²+bx+c) ⊙ 0 (c такой, чтобы корни были целыми)
3) x_vs_const_over_x:                x ⊙ K/x  → (x²−K)/x ⊙ 0
4) neg_const_over_shifted_square_minus_const:  −C/((x−a)²−d) ⊙ 0  (границы a±√d)
"""

from __future__ import annotations

import random
import uuid
import math
from typing import Any, Dict, List, Tuple

_AXIS_INF = 1e9
_AXIS_ROUND_DIGITS = 5


def _round_axis_value(value: float) -> float:
    return round(float(value), _AXIS_ROUND_DIGITS)


# ———————————————————————————————————————————————————————————————————————
# Общие утилиты оформления
# ———————————————————————————————————————————————————————————————————————

SUPERSCRIPTS = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
                "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}


def _to_superscripts(expr: str) -> str:
    s = expr
    for k, v in SUPERSCRIPTS.items():
        s = s.replace(f"^{k}", v)
    return s


def _qt(equation: str) -> str:
    """Стандартная обёртка для текста задания."""
    return f"Решите неравенство:\n{_to_superscripts(equation)}"


def _fmt_lin(b: int, with_plus: bool = True) -> str:
    if b == 0:
        return ""
    sign = "+ " if b > 0 and with_plus else ("- " if b < 0 else "")
    return f"{sign}{abs(b)}x" if abs(b) != 1 else f"{sign}x"


def _fmt_const(c: int, with_plus: bool = True) -> str:
    if c == 0:
        return ""
    sign = "+ " if c > 0 and with_plus else ("- " if c < 0 else "")
    return f"{sign}{abs(c)}"


def _interval_text(l_text: str, r_text: str, include_l: bool, include_r: bool) -> str:
    left_br = "[" if include_l else "("
    right_br = "]" if include_r else ")"
    return f"{left_br}{l_text}; {r_text}{right_br}"


def _join_intervals_text(chunks: List[str]) -> str:
    return " ∪ ".join(chunks)


def _axis_point(value_text: str, value_num: float, ptype: str) -> Dict[str, Any]:
    return {
        "value_text": value_text,
        "value_num": _round_axis_value(value_num),
        "type": ptype
    }  # ptype: "hollow"/"solid"


def _axis_interval(l_txt: str, l_num: float, r_txt: str, r_num: float, sign_char: str) -> Dict[str, Any]:
    return {
        "range": {
            "left_text": l_txt,
            "left_num": _round_axis_value(l_num),
            "right_text": r_txt,
            "right_num": _round_axis_value(r_num)
        },
        "sign": sign_char  # "+" or "-"
    }


def _shading_entry(l_txt: str, l_num: float, r_txt: str, r_num: float,
                   include_l: bool, include_r: bool) -> Dict[str, Any]:
    return {
        "left_text": l_txt,
        "left_num": _round_axis_value(l_num),
        "right_text": r_txt,
        "right_num": _round_axis_value(r_num),
        "include_left": include_l, "include_right": include_r
    }


# ———————————————————————————————————————————————————————————————————————
# 1) compare_unit_fractions_linear  : 1/x ⊙ 1/(x−a)
# ———————————————————————————————————————————————————————————————————————

def _gen_compare_unit_fractions_linear() -> Tuple[str, str, Dict[str, Any]]:
    a = random.randint(2, 9)
    sign = random.choice(["≥", "≤"])  # строгости тоже возможны, но в ОГЭ чаще нестрогие

    initial = f"1/x {sign} 1/(x−{a})"
    # Приводим к одной дроби: 1/x − 1/(x−a) ⊙ 0  =>  a / (x(x−a)) ⊙ 0
    transformed = f"{a}/(x(x−{a})) {sign} 0"

    # Нули: числитель = константа (нет нулей), знаменатель: 0 и a
    numerator_zeros: List[str] = []
    denominator_zeros_text = ["0", f"{a}"]
    denominator_zeros_num = [0.0, float(a)]

    # Точки на оси
    points = [
        _axis_point("0", 0.0, "hollow"),
        _axis_point(f"{a}", float(a), "hollow"),
    ]

    # Интервалы и их знак (a>0 => знак дроби = знак произведения знаменателя)
    crit = [-_AXIS_INF, 0.0, float(a), _AXIS_INF]
    crit_txt = ["−∞", "0", f"{a}", "+∞"]
    intervals = []
    signs = []
    for i in range(3):
        x_mid = (crit[i] + crit[i + 1]) / 2 if math.isfinite(crit[i]) and math.isfinite(crit[i + 1]) else \
            (-1.0 if i == 0 else (a + 1.0 if i == 2 else a / 2))
        s = (x_mid) * (x_mid - a)
        sign_char = "+" if s > 0 else "-"
        signs.append(sign_char)
        intervals.append(_axis_interval(crit_txt[i], crit[i], crit_txt[i + 1], crit[i + 1], sign_char))

    # Выбор закрашиваемых интервалов
    want_positive = sign in ("≥", ">")
    shading: List[Dict[str, Any]] = []
    chunks: List[str] = []
    for i in range(3):
        ok = (signs[i] == "+") if want_positive else (signs[i] == "-")
        if not ok:
            continue
        l_txt, r_txt = crit_txt[i], crit_txt[i + 1]
        l_num, r_num = crit[i], crit[i + 1]
        # включаться границы могут только в числителе (которого нет), поэтому всегда круглые скобки
        shading.append(_shading_entry(l_txt, l_num, r_txt, r_num, False, False))
        chunks.append(_interval_text(l_txt, r_txt, False, False))

    answer = _join_intervals_text(chunks)

    variables = {
        "solution_pattern": "compare_unit_fractions_linear",
        "coefficients": {"a": a, "sign": sign},
        "initial_expression": initial,
        "transformed_expression": transformed,
        "numerator_zeros": [],
        "denominator_zeros": denominator_zeros_text,
        "axis_data": {
            "points": points,
            "intervals": intervals,
            "shading_ranges": shading
        }
    }
    return initial, answer, variables


# ———————————————————————————————————————————————————————————————————————
# 2) const_over_quadratic_nonpos_nonneg : −C/(x²+bx+c) ⊙ 0
#    выбираем квадратики с ЦЕЛЫМИ корнями r1<r2
# ———————————————————————————————————————————————————————————————————————

def _gen_const_over_quadratic_nonpos_nonneg() -> Tuple[str, str, Dict[str, Any]]:
    # Возьмём пару целых корней
    r1, r2 = sorted(random.sample([-8, -6, -5, -4, -3, 1, 2, 3, 5, 6, 8], 2))
    b = -(r1 + r2)
    c = r1 * r2
    C = 19  # модуль константы
    # Берём отрицательный числитель как в оригиналах и знак ≤/≥
    numerator = -C
    sign = random.choice(["≤", "≥"])

    quad_text = f"x^2 {_fmt_lin(b)} {_fmt_const(c)}".replace("+ -", "- ")
    initial = f"{numerator}/{_to_superscripts(quad_text).replace('^', '')} {sign} 0"
    # transformed уже и есть эта же дробь
    transformed = f"{numerator}/({quad_text}) {sign} 0"

    # Нули
    numerator_zeros: List[str] = []  # числитель константа
    denominator_zeros_text = [str(r1), str(r2)]
    points = [
        _axis_point(str(r1), float(r1), "hollow"),
        _axis_point(str(r2), float(r2), "hollow"),
    ]

    # Знаки интервалов зависят от знака знаменателя; числитель <0
    # Для "≤ 0": нужен знаменатель ≥ 0  (внешние интервалы)
    # Для "≥ 0": нужен знаменатель ≤ 0  (внутренний интервал)
    crit = [-_AXIS_INF, float(r1), float(r2), _AXIS_INF]
    crit_txt = ["−∞", str(r1), str(r2), "+∞"]
    intervals, signs = [], []
    for i in range(3):
        # берём середину интервала
        if math.isfinite(crit[i]) and math.isfinite(crit[i + 1]):
            x_mid = (crit[i] + crit[i + 1]) / 2
        else:
            x_mid = r1 - 1 if i == 0 else (r2 + 1 if i == 2 else 0.0)
        denom_val = (x_mid - r1) * (x_mid - r2)
        frac_sign = "-" if denom_val > 0 else "+"  # потому что числитель отрицателен
        signs.append(frac_sign)
        intervals.append(_axis_interval(crit_txt[i], crit[i], crit_txt[i + 1], crit[i + 1], frac_sign))

    want_nonpos = (sign == "≤")
    shading: List[Dict[str, Any]] = []
    chunks: List[str] = []
    for i in range(3):
        ok = (signs[i] == "-") if want_nonpos else (signs[i] == "+")
        if not ok:
            continue
        l_txt, r_txt = crit_txt[i], crit_txt[i + 1]
        l_num, r_num = crit[i], crit[i + 1]
        # границы — точки разрыва, всегда круглые
        shading.append(_shading_entry(l_txt, l_num, r_txt, r_num, False, False))
        chunks.append(_interval_text(l_txt, r_txt, False, False))

    answer = _join_intervals_text(chunks)

    variables = {
        "solution_pattern": "const_over_quadratic_nonpos_nonneg",
        "coefficients": {"b": b, "c": c, "C": numerator, "roots": [r1, r2], "sign": sign},
        "initial_expression": f"{numerator}/({ _to_superscripts(quad_text) }) {sign} 0",
        "transformed_expression": transformed,
        "numerator_zeros": numerator_zeros,
        "denominator_zeros": denominator_zeros_text,
        "axis_data": {
            "points": points,
            "intervals": intervals,
            "shading_ranges": shading
        }
    }
    return initial, answer, variables


# ———————————————————————————————————————————————————————————————————————
# 3) x_vs_const_over_x : x ⊙ K/x  →  (x²−K)/x ⊙ 0  ,  K=m²
# ———————————————————————————————————————————————————————————————————————

def _gen_x_vs_const_over_x() -> Tuple[str, str, Dict[str, Any]]:
    m = random.choice([2, 3, 4, 5, 6, 7, 8])
    K = m * m
    sign = random.choice(["≤", "≥"])  # оба варианта корректны

    initial = f"x {sign} {K}/x"
    transformed = f"(x^2−{K})/x {sign} 0"

    # Нули
    numerator_zeros_text = [f"−{m}", f"{m}"]
    numerator_zeros_num = [-float(m), float(m)]
    denominator_zeros_text = ["0"]
    denominator_zeros_num = [0.0]

    # Точки
    points = [
        _axis_point(f"−{m}", -float(m), "solid" if sign in ("≤", "≥") else "hollow"),
        _axis_point("0", 0.0, "hollow"),
        _axis_point(f"{m}", float(m), "solid" if sign in ("≤", "≥") else "hollow"),
    ]

    # Интервалы по критическим точкам: −∞, −m, 0, m, +∞
    crit = [-_AXIS_INF, -float(m), 0.0, float(m), _AXIS_INF]
    crit_txt = ["−∞", f"−{m}", "0", f"{m}", "+∞"]
    intervals, signs_list = [], []
    for i in range(4):
        if math.isfinite(crit[i]) and math.isfinite(crit[i + 1]):
            x_mid = (crit[i] + crit[i + 1]) / 2
        else:
            x_mid = -m - 1 if i == 0 else (m + 1 if i == 3 else (m / 2 if i == 2 else -m / 2))
        num_val = x_mid * x_mid - K
        den_val = x_mid
        sgn = "+" if (num_val > 0 and den_val > 0) or (num_val < 0 and den_val < 0) else "-"
        signs_list.append(sgn)
        intervals.append(_axis_interval(crit_txt[i], crit[i], crit_txt[i + 1], crit[i + 1], sgn))

    want_nonpos = (sign == "≤")
    shading: List[Dict[str, Any]] = []
    chunks: List[str] = []
    for i in range(4):
        ok = (signs_list[i] == "-") if want_nonpos else (signs_list[i] == "+")
        if not ok:
            continue
        l_txt, r_txt = crit_txt[i], crit_txt[i + 1]
        l_num, r_num = crit[i], crit[i + 1]

        # Включаем границы, если это нули числителя и знак нестрогий
        include_l = False
        include_r = False
        if l_txt in numerator_zeros_text and sign in ("≤", "≥"):
            include_l = True
        if r_txt in numerator_zeros_text and sign in ("≤", "≥"):
            include_r = True

        # Ноль знаменателя никогда не включаем
        if l_txt == "0":
            include_l = False
        if r_txt == "0":
            include_r = False

        shading.append(_shading_entry(l_txt, l_num, r_txt, r_num, include_l, include_r))
        chunks.append(_interval_text(l_txt, r_txt, include_l, include_r))

    answer = _join_intervals_text(chunks)

    variables = {
        "solution_pattern": "x_vs_const_over_x",
        "coefficients": {"K": K, "m": m, "sign": sign},
        "initial_expression": initial,
        "transformed_expression": transformed,
        "numerator_zeros": numerator_zeros_text,
        "denominator_zeros": denominator_zeros_text,
        "axis_data": {
            "points": points,
            "intervals": intervals,
            "shading_ranges": shading
        }
    }
    return initial, answer, variables


# ———————————————————————————————————————————————————————————————————————
# 4) neg_const_over_shifted_square_minus_const : −C/((x−a)²−d) ⊙ 0
# ———————————————————————————————————————————————————————————————————————

def _gen_neg_const_over_shifted_square_minus_const() -> Tuple[str, str, Dict[str, Any]]:
    a = random.randint(1, 6)
    d = random.choice([2, 3, 5, 6, 7, 8, 11])
    C = -random.choice([5, 7, 9, 11])  # отрицательный числитель
    sign = random.choice(["≥", "≤"])

    initial = f"{C}/((x−{a})^2−{d}) {sign} 0"
    transformed = initial  # форма уже приведённая

    left_txt = f"{a}−√{d}"
    right_txt = f"{a}+√{d}"
    left_num = a - math.sqrt(d)
    right_num = a + math.sqrt(d)

    # Нули
    numerator_zeros: List[str] = []
    denominator_zeros_text = [left_txt, right_txt]

    # Точки
    points = [
        _axis_point(left_txt, left_num, "hollow"),
        _axis_point(right_txt, right_num, "hollow"),
    ]

    # Знак дроби: числитель < 0 ⇒ знак противоположен знаку знаменателя.
    # Знаменатель (x−a)^2−d <= 0 ⇔ x ∈ (a−√d ; a+√d)
    crit_txt = ["−∞", left_txt, right_txt, "+∞"]
    crit = [-_AXIS_INF, left_num, right_num, _AXIS_INF]
    intervals, signs_list = [], []
    for i in range(3):
        if math.isfinite(crit[i]) and math.isfinite(crit[i + 1]):
            x_mid = (crit[i] + crit[i + 1]) / 2
        else:
            x_mid = left_num - 1 if i == 0 else (right_num + 1 if i == 2 else a)
        denom_val = (x_mid - a) ** 2 - d
        frac_sign = "-" if denom_val > 0 else "+"  # числитель отрицателен
        signs_list.append(frac_sign)
        intervals.append(_axis_interval(crit_txt[i], crit[i], crit_txt[i + 1], crit[i + 1], frac_sign))

    want_nonneg = (sign == "≥")
    shading: List[Dict[str, Any]] = []
    chunks: List[str] = []
    for i in range(3):
        ok = (signs_list[i] == "+") if want_nonneg else (signs_list[i] == "-")
        if not ok:
            continue
        l_txt, r_txt = crit_txt[i], crit_txt[i + 1]
        l_num, r_num = crit[i], crit[i + 1]
        shading.append(_shading_entry(l_txt, l_num, r_txt, r_num, False, False))
        chunks.append(_interval_text(l_txt, r_txt, False, False))

    answer = _join_intervals_text(chunks)

    variables = {
        "solution_pattern": "neg_const_over_shifted_square_minus_const",
        "coefficients": {"a": a, "d": d, "C": C, "sign": sign},
        "initial_expression": initial,
        "transformed_expression": transformed,
        "numerator_zeros": numerator_zeros,
        "denominator_zeros": denominator_zeros_text,
        "axis_data": {
            "points": points,
            "intervals": intervals,
            "shading_ranges": shading
        }
    }
    return initial, answer, variables


# ———————————————————————————————————————————————————————————————————————
# Карта паттернов и главная функция
# ———————————————————————————————————————————————————————————————————————

PATTERN_GENERATORS = {
    "compare_unit_fractions_linear": _gen_compare_unit_fractions_linear,
    "const_over_quadratic_nonpos_nonneg": _gen_const_over_quadratic_nonpos_nonneg,
    "x_vs_const_over_x": _gen_x_vs_const_over_x,
    "neg_const_over_shifted_square_minus_const": _gen_neg_const_over_shifted_square_minus_const,
}


def generate_task_20_rational_inequalities(pattern: str | None = None) -> Dict[str, Any]:
    """
    Генерирует задачу подтипа rational_inequalities с полным набором данных для оси.

    Аргументы:
        pattern: (опционально) имя паттерна из PATTERN_GENERATORS.
                 Если None — выбирается случайный из доступных.

    Возвращает:
        Полный словарь задачи (совместим с populate и валидатором).
    """
    import uuid
    import random

    # Если pattern не передан — выбираем случайный
    if pattern is None:
        pattern_key = random.choice(list(PATTERN_GENERATORS))
    else:
        if pattern not in PATTERN_GENERATORS:
            raise ValueError(
                f"❌ Неизвестный pattern: {pattern}. "
                f"Допустимые: {', '.join(PATTERN_GENERATORS.keys())}"
            )
        pattern_key = pattern

    gen = PATTERN_GENERATORS[pattern_key]
    initial, answer, variables = gen()
    variables.setdefault("solution_pattern", pattern_key)

    # Защита от случайного совпадения с оригиналами
    banned_examples = {
        "1/x ≥ 1/(x−3)",
        "−19/(x^2 + x − 12) ≤ 0",
        "x ≤ 25/x",
        "−11/((x−2)^2 − 3) ≥ 0",
    }
    if variables.get("initial_expression") in banned_examples:
        return generate_task_20_rational_inequalities(pattern)

    return {
        "id": f"20_rational_inequalities_{uuid.uuid4().hex[:6]}",
        "task_number": 20,
        "topic": "inequalities",
        "subtype": "rational_inequalities",
        "question_text": _qt(variables["initial_expression"]),
        "answer": [answer],
        "variables": variables,
    }


__all__ = ["generate_task_20_rational_inequalities"]
