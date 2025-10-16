"""Validator for task 20 rational_inequalities subtype (ФИПИ-строгий).

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
from typing import Any, Dict, List


def _sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _infty_text_to_num(t: str) -> float:
    if t == "−∞":
        return -math.inf
    if t == "+∞":
        return math.inf
    return float(t.replace("−", "-"))  # поддержим "−" в строке


def _interval_to_text(L: str, R: str, inc_l: bool, inc_r: bool) -> str:
    return f"{'[' if inc_l else '('}{L}; {R}{']' if inc_r else ')'}"


def _build_answer_from_shading(shading: List[Dict[str, Any]]) -> str:
    chunks = []
    for it in shading:
        chunks.append(_interval_to_text(it["left_text"], it["right_text"], it["include_left"], it["include_right"]))
    return " ∪ ".join(chunks)


def validate_task_20_rational_inequalities(task: Dict[str, Any]) -> bool:
    """Главная точка валидации."""
    try:
        assert task["task_number"] == 20
        assert task["topic"] == "inequalities"
        assert task["subtype"] == "rational_inequalities"

        vars_ = task["variables"]
        for k in ("solution_pattern", "initial_expression", "transformed_expression",
                  "numerator_zeros", "denominator_zeros", "axis_data"):
            assert k in vars_

        pattern = vars_["solution_pattern"]
        axis = vars_["axis_data"]
        points = axis["points"]
        intervals = axis["intervals"]
        shading = axis["shading_ranges"]
        coeffs = vars_.get("coefficients", {})

        # ——— 1) Проверка преобразования initial → transformed (по паттерну)
        init = vars_["initial_expression"]
        transf = vars_["transformed_expression"]
        if pattern == "compare_unit_fractions_linear":
            a = int(coeffs["a"])
            assert f"{a}/(x(x−{a}))" in transf
        elif pattern == "const_over_quadratic_nonpos_nonneg":
            # transformed = −C/(x^2 + b x + c) ⊙ 0
            b = coeffs["b"]; c = coeffs["c"]
            assert "(x^2" in transf and f"{'+' if b>=0 else '-'} {abs(b)}x" in transf and f"{'+' if c>=0 else '-'} {abs(c)}" in transf
        elif pattern == "x_vs_const_over_x":
            K = coeffs["K"]
            assert f"(x^2−{K})/x" in transf
        elif pattern == "neg_const_over_shifted_square_minus_const":
            a = coeffs["a"]; d = coeffs["d"]
            assert f"((x−{a})^2−{d})" in transf
        else:
            return False

        # ——— 2) Проверка нулей
        # Соберём текстовые нули числителя/знаменателя
        num_zeros_txt = set(vars_.get("numerator_zeros", []))
        den_zeros_txt = set(vars_.get("denominator_zeros", []))
        # Все точки оси должны содержать только эти нули
        axis_zeros_txt = {p["value_text"] for p in points}
        assert axis_zeros_txt == (num_zeros_txt | den_zeros_txt)

        # ——— 3) Типы точек
        # Деноминатор → всегда hollow
        for p in points:
            if p["value_text"] in den_zeros_txt:
                assert p["type"] == "hollow"
        # Нумератор → solid только при ≤/≥
        weak = any(sym in vars_["initial_expression"] for sym in ("≤", "≥"))
        for p in points:
            if p["value_text"] in num_zeros_txt:
                if weak:
                    assert p["type"] == "solid"
                else:
                    assert p["type"] == "hollow"

        # ——— 4) Проверка знаков интервалов через подстановку
        def _sign_of_fraction(x: float) -> int:
            if pattern == "compare_unit_fractions_linear":
                a = int(coeffs["a"])
                num = a
                den = x * (x - a)
            elif pattern == "const_over_quadratic_nonpos_nonneg":
                b = coeffs["b"]; c = coeffs["c"]; C = coeffs["C"]
                num = C  # отрицательное
                den = x*x + b*x + c
            elif pattern == "x_vs_const_over_x":
                K = coeffs["K"]
                num = x*x - K
                den = x
            else:  # neg_const_over_shifted_square_minus_const
                a = coeffs["a"]; d = coeffs["d"]; C = coeffs["C"]
                num = C  # <0
                den = (x - a)*(x - a) - d
            if den == 0:
                return 0
            s = _sign(num) * _sign(den)
            return s

        # Все интервалы должны иметь корректный знак
        for it in intervals:
            L_num = it["range"]["left_num"]; R_num = it["range"]["right_num"]
            # выберем тестовую точку
            if math.isfinite(L_num) and math.isfinite(R_num):
                x_test = (L_num + R_num) / 2
            else:
                if not math.isfinite(L_num) and math.isfinite(R_num):
                    x_test = R_num - 1.0
                elif math.isfinite(L_num) and not math.isfinite(R_num):
                    x_test = L_num + 1.0
                else:
                    x_test = 0.0
            s = _sign_of_fraction(x_test)
            expected = "+" if s > 0 else "-" if s < 0 else "0"
            assert it["sign"] == expected or (expected == "0" and it["sign"] in ("+", "-"))

        # ——— 5) Проверка shading по знакам и типу неравенства
        want_pos = "≥" in init or ">" in init
        want_nonneg = "≥" in init or "≤" in init  # слабость для включения нулей числителя
        # Сопоставим shading с intervals по границам
        def _inc_side(txt: str, is_left: bool) -> bool:
            # включаем только если это ноль числителя и знак слабый
            return (txt in num_zeros_txt) and want_nonneg

        for sh in shading:
            l_txt, r_txt = sh["left_text"], sh["right_text"]
            # найдём интервал с такими же границами
            found = None
            for it in intervals:
                if it["range"]["left_text"] == l_txt and it["range"]["right_text"] == r_txt:
                    found = it
                    break
            assert found is not None
            if want_pos:
                assert found["sign"] == "+"
            else:
                # хотим ≤0  → знак должен быть "−"
                assert found["sign"] == "-"

            # Проверка включения границ: только нули числителя и только при слабом знаке
            assert sh["include_left"] == _inc_side(l_txt, True)
            assert sh["include_right"] == _inc_side(r_txt, False)

        # ——— 6) Ответ = точное склеивание shading_ranges
        expected_answer = _build_answer_from_shading(shading)
        assert isinstance(task["answer"], list) and len(task["answer"]) == 1
        assert task["answer"][0] == expected_answer

        return True
    except AssertionError:
        return False


__all__ = ["validate_task_20_rational_inequalities"]
