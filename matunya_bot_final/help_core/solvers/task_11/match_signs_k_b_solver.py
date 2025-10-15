"""Solver for task 11 subtype ``match_signs_k_b``."""

from __future__ import annotations

from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

_LABEL_FALLBACK = ["A", "B", "C"]


def _format_linear_formula(k_value: Any, b_value: Any) -> str:
    if k_value is None and b_value is None:
        return "N/A"

    if k_value in (None, ""):
        slope_part = "kx"
    elif k_value == 0:
        slope_part = "0"
    elif k_value == 1:
        slope_part = "x"
    elif k_value == -1:
        slope_part = "-x"
    else:
        slope_part = f"{k_value}x"

    intercept_part = ""
    if isinstance(b_value, (int, float)) and b_value != 0:
        sign = "+" if b_value > 0 else "-"
        intercept_part = f" {sign} {abs(b_value)}"

    return f"y = {slope_part}{intercept_part}".strip()


def _describe_slope(k_value: Any) -> str:
    if isinstance(k_value, (int, float)):
        if k_value > 0:
            return "график возрастает"
        if k_value < 0:
            return "график убывает"
        return "график горизонтальный"
    return "наклон определить нельзя"


def _describe_intercept(b_value: Any) -> str:
    if isinstance(b_value, (int, float)):
        if b_value > 0:
            return "пересекает ось Y выше нуля"
        if b_value < 0:
            return "пересекает ось Y ниже нуля"
        return "проходит через начало координат"
    return "пересечение не указано"


async def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Solver match_signs_k_b started (GOST-RESHATEL-2025)")

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
            coeffs = func_data[index].get("coeffs") or {}
        k_value = coeffs.get("k")
        b_value = coeffs.get("b")

        slope_text = _describe_slope(k_value)
        if isinstance(k_value, (int, float)):
            k_sign = "k > 0" if k_value > 0 else ("k < 0" if k_value < 0 else "k = 0")
        else:
            k_sign = "k неизвестно"

        intercept_text = _describe_intercept(b_value)
        if isinstance(b_value, (int, float)):
            b_sign = "b > 0" if b_value > 0 else ("b < 0" if b_value < 0 else "b = 0")
        else:
            b_sign = "b неизвестно"

        calc_result = (
            f"{slope_text} ({k_sign}), {intercept_text} ({b_sign}). "
            f"Это вариант №{option_key}: {option_text}"
        )

        steps.append({
            "step_number": index + 1,
            "description": f"Анализируем график {label}",
            "formula_representation": _format_linear_formula(k_value, b_value),
            "calculation_result": calc_result,
            "result_unit": "N/A",
        })

        if option_key is not None:
            display_pairs.append(f"{label}-{option_key}")

    value_machine = "".join(answers) if answers else "N/A"
    value_display = ", ".join(display_pairs) if display_pairs else "N/A"

    solution_core = {
        "question_id": str(task_data.get("id", "match_signs_k_b")),
        "explanation_idea": (
            "Определяем знак коэффициента k по наклону прямой и знак b по точке пересечения с осью Y."
        ),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": value_machine,
            "value_display": value_display,
            "unit": "N/A",
        },
        "hints": [
            "Если прямая возрастает слева направо, наклон k положителен; если убывает — отрицателен.",
            "Значение b видно по точке пересечения с осью Y при x = 0.",
        ],
    }

    logger.info("Solver match_signs_k_b finished (GOST-RESHATEL-2025)")
    return solution_core


__all__ = ["solve"]
