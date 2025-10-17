"""
ГОСТ-ВАЛИДАТОР-2025
Validator for task 20 rational_inequalities subtype (ФИПИ-строгий).

Проверяет:
1) Корректность преобразования initial_expression → transformed_expression (по паттерну).
2) Правильность нулей числителя/знаменателя.
3) Соответствие типов точек на оси (solid/hollow).
4) Знак на каждом интервале через подстановку тестовой точки.
5) Корректность shading_ranges по знакам и типу неравенства.
6) Точное соответствие answer ↔ shading_ranges (строка из ∪).
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Tuple


def _sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _interval_to_text(L: str, R: str, inc_l: bool, inc_r: bool) -> str:
    return f"{'[' if inc_l else '('}{L}; {R}{']' if inc_r else ')'}"


def _build_answer_from_shading(shading: List[Dict[str, Any]]) -> str:
    chunks = []
    for it in shading:
        chunks.append(_interval_to_text(it["left_text"], it["right_text"],
                                        it["include_left"], it["include_right"]))
    return " ∪ ".join(chunks)


def validate_task_20_rational_inequalities(task: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Главная точка валидации (ГОСТ-2025)."""
    errors: List[str] = []

    # 1. Базовая структура
    if task.get("task_number") != 20:
        errors.append("Неверный task_number (ожидался 20).")

    if task.get("topic") != "inequalities":
        errors.append("Неверный topic (ожидался 'inequalities').")

    if task.get("subtype") != "rational_inequalities":
        errors.append("Неверный subtype (ожидался 'rational_inequalities').")

    vars_ = task.get("variables")
    if not isinstance(vars_, dict):
        errors.append("Отсутствует ключ 'variables'.")
        return False, errors

    required_keys = [
        "solution_pattern", "initial_expression", "transformed_expression",
        "numerator_zeros", "denominator_zeros", "axis_data"
    ]
    for k in required_keys:
        if k not in vars_:
            errors.append(f"Отсутствует ключ '{k}' в variables.")

    if errors:
        return False, errors

    # 2. Проверка преобразования initial → transformed
    pattern = vars_["solution_pattern"]
    coeffs = vars_.get("coefficients", {})
    init = vars_["initial_expression"]
    transf = vars_["transformed_expression"]

    if pattern == "compare_unit_fractions_linear":
        a = int(coeffs.get("a", 0))
        if f"{a}/(x(x−{a}))" not in transf:
            errors.append(f"Некорректное преобразование для pattern={pattern}: "
                          f"ожидалось '...{a}/(x(x−{a}))...'")
    elif pattern == "const_over_quadratic_nonpos_nonneg":
        b = coeffs.get("b"); c = coeffs.get("c")
        if b is None or c is None:
            errors.append("Нет коэффициентов b или c.")
        else:
            if not all(s in transf for s in ("x^2", "x")):
                errors.append("В transformed_expression отсутствует форма квадратного выражения.")
    elif pattern == "x_vs_const_over_x":
        K = coeffs.get("K")
        if K is None or f"(x^2−{K})/x" not in transf:
            errors.append("Неверное преобразование для x_vs_const_over_x.")
    elif pattern == "neg_const_over_shifted_square_minus_const":
        a = coeffs.get("a"); d = coeffs.get("d")
        if a is None or d is None or f"((x−{a})^2−{d})" not in transf:
            errors.append("Неверное преобразование для neg_const_over_shifted_square_minus_const.")
    else:
        errors.append(f"Неизвестный pattern: {pattern}")

    # 3. Проверка нулей
    num_zeros_txt = set(vars_.get("numerator_zeros", []))
    den_zeros_txt = set(vars_.get("denominator_zeros", []))
    axis = vars_["axis_data"]
    points = axis.get("points", [])
    axis_zeros_txt = {p["value_text"] for p in points}
    if axis_zeros_txt != (num_zeros_txt | den_zeros_txt):
        errors.append("Набор точек на оси не совпадает с нулями числителя и знаменателя.")

    # 4. Типы точек
    weak = any(sym in init for sym in ("≤", "≥"))
    for p in points:
        if p["value_text"] in den_zeros_txt and p["type"] != "hollow":
            errors.append(f"Точка {p['value_text']} (знаменатель) должна быть hollow.")
        if p["value_text"] in num_zeros_txt:
            expected_type = "solid" if weak else "hollow"
            if p["type"] != expected_type:
                errors.append(f"Точка {p['value_text']} (числитель) должна быть {expected_type}.")

    # 5. Проверка знаков интервалов через подстановку
    def _sign_of_fraction(x: float) -> int:
        try:
            if pattern == "compare_unit_fractions_linear":
                a = int(coeffs["a"])
                num = a
                den = x * (x - a)
            elif pattern == "const_over_quadratic_nonpos_nonneg":
                b = coeffs["b"]; c = coeffs["c"]; C = coeffs["C"]
                num = C; den = x*x + b*x + c
            elif pattern == "x_vs_const_over_x":
                K = coeffs["K"]; num = x*x - K; den = x
            else:
                a = coeffs["a"]; d = coeffs["d"]; C = coeffs["C"]
                num = C; den = (x - a)*(x - a) - d
            if den == 0:
                return 0
            return _sign(num) * _sign(den)
        except Exception:
            return 0

    intervals = axis.get("intervals", [])
    for it in intervals:
        L = it["range"]["left_num"]; R = it["range"]["right_num"]
        if math.isfinite(L) and math.isfinite(R):
            x_test = (L + R) / 2
        elif not math.isfinite(L):
            x_test = R - 1.0
        elif not math.isfinite(R):
            x_test = L + 1.0
        else:
            x_test = 0.0

        s = _sign_of_fraction(x_test)
        expected = "+" if s > 0 else "-" if s < 0 else "0"
        if it["sign"] != expected and not (expected == "0" and it["sign"] in ("+", "-")):
            errors.append(f"Неверный знак на интервале {it['range']} (ожидался {expected}).")

    # 6. Проверка shading
    shading = axis.get("shading_ranges", [])
    want_pos = "≥" in init or ">" in init
    want_nonneg = "≥" in init or "≤" in init

    def _inc_side(txt: str) -> bool:
        return (txt in num_zeros_txt) and want_nonneg

    for sh in shading:
        l_txt, r_txt = sh["left_text"], sh["right_text"]
        found = next((it for it in intervals
                      if it["range"]["left_text"] == l_txt and it["range"]["right_text"] == r_txt), None)
        if not found:
            errors.append(f"Не найден интервал для shading {l_txt}–{r_txt}.")
            continue
        if want_pos and found["sign"] != "+":
            errors.append(f"Ожидался знак '+' для shading {l_txt}–{r_txt}.")
        if not want_pos and found["sign"] != "-":
            errors.append(f"Ожидался знак '−' для shading {l_txt}–{r_txt}.")
        if sh["include_left"] != _inc_side(l_txt):
            errors.append(f"Неверное включение левой границы {l_txt}.")
        if sh["include_right"] != _inc_side(r_txt):
            errors.append(f"Неверное включение правой границы {r_txt}.")

    # 7. Проверка answer
    expected_answer = _build_answer_from_shading(shading)
    answer = task.get("answer")
    if not (isinstance(answer, list) and len(answer) == 1):
        errors.append("Поле 'answer' должно быть списком с одним элементом.")
    elif answer[0] != expected_answer:
        errors.append(f"Ответ '{answer[0]}' не совпадает с shading '{expected_answer}'.")

    # Финал
    is_valid = len(errors) == 0
    return is_valid, errors


__all__ = ["validate_task_20_rational_inequalities"]
