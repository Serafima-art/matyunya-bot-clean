"""Solver for task 11 subtype ``match_signs_a_c``."""

from __future__ import annotations

from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

_LABEL_FALLBACK = ["A", "B", "C"]


def _format_parabola_formula(coeffs: Dict[str, Any]) -> str:
    if not coeffs:
        return "N/A"

    a = coeffs.get("a")
    b = coeffs.get("b")
    c = coeffs.get("c")

    if a is None:
        return "N/A"

    parts: List[str] = []
    if a == 0:
        parts.append("0")
    elif a == 1:
        parts.append("x^2")
    elif a == -1:
        parts.append("-x^2")
    else:
        parts.append(f"{a}x^2")

    if b:
        sign_b = "+" if b > 0 else "-"
        abs_b = abs(b)
        term_b = "x" if abs_b == 1 else f"{abs_b}x"
        parts.append(f" {sign_b} {term_b}")

    if c:
        sign_c = "+" if c > 0 else "-"
        parts.append(f" {sign_c} {abs(c)}")

    formula = "".join(parts).strip()
    return f"y = {formula}" if formula else "y = 0"


def _describe_intersection(c_value: Any) -> str:
    if isinstance(c_value, (int, float)):
        if c_value > 0:
            return "пересекает ось Y выше нуля"
        if c_value < 0:
            return "пересекает ось Y ниже нуля"
        return "проходит через начало координат"
    return "пересечение не указано"


async def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Solver match_signs_a_c started (GOST-RESHATEL-2025)")

    source_params = (task_data.get("source_plot") or {}).get("params") or {}
    labels: List[str] = list(source_params.get("labels") or _LABEL_FALLBACK)
    options: Dict[str, str] = dict(source_params.get("options") or {})
    answers: List[str] = list(task_data.get("answer") or [])
    func_data: List[Dict[str, Any]] = list(task_data.get("func_data") or [])

    steps: List[Dict[str, Any]] = []
    display_pairs: List[str] = []

    for index, label in enumerate(labels):
        option_key = answers[index] if index < len(answers) else None
        option_text = options.get(option_key, "N/A")
        coeffs = {}
        if index < len(func_data):
            coeffs = func_data[index].get("coeffs") or func_data[index].get("_debug_coeffs") or {}

        a_value = coeffs.get("a")
        c_value = coeffs.get("c")

        if isinstance(a_value, (int, float)):
            orientation = "ветви направлены вверх" if a_value > 0 else "ветви направлены вниз"
            a_sign_text = "a > 0" if a_value > 0 else "a < 0"
        else:
            orientation = "направление ветвей не определяется"
            a_sign_text = "a неизвестно"

        intersection_text = _describe_intersection(c_value)
        if isinstance(c_value, (int, float)):
            c_sign_text = "c > 0" if c_value > 0 else ("c < 0" if c_value < 0 else "c = 0")
        else:
            c_sign_text = "c неизвестно"

        formula_repr = _format_parabola_formula(coeffs)
        calc_result = (
            f"{orientation} ({a_sign_text}), {intersection_text} ({c_sign_text}). "
            f"Это вариант №{option_key}: {option_text}"
        )

        steps.append({
            "step_number": index + 1,
            "description": f"Анализируем график {label}",
            "formula_representation": formula_repr,
            "calculation_result": calc_result,
            "result_unit": "N/A",
        })

        if option_key is not None:
            display_pairs.append(f"{label}-{option_key}")

    value_machine = "".join(answers) if answers else "N/A"
    value_display = ", ".join(display_pairs) if display_pairs else "N/A"

    solution_core = {
        "question_id": str(task_data.get("id", "match_signs_a_c")),
        "explanation_idea": (
            "Определяем знак коэффициента a по направлению ветвей параболы и знак c по точке пересечения с осью Y."
        ),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": value_machine,
            "value_display": value_display,
            "unit": "N/A",
        },
        "hints": [
            "Если ветви параболы направлены вверх, коэффициент a положителен; если вниз — отрицателен.",
            "Значение коэффициента c совпадает со значением функции при x = 0 (точка пересечения с осью Y).",
        ],
    }

    logger.info("Solver match_signs_a_c finished (GOST-RESHATEL-2025)")
    return solution_core


__all__ = ["solve"]
