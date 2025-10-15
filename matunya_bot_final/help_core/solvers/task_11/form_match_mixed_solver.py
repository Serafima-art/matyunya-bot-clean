"""Solver for task 11 subtype ``form_match_mixed``."""

from __future__ import annotations

from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

_LABEL_FALLBACK = ["A", "B", "C"]


_FUNCTION_TYPES = {
    "linear": "линейной функции",
    "parabola": "параболы",
    "hyperbola": "гиперболы",
    "sqrt": "корневой функции",
}


def _detect_formula_type(formula: str) -> str:
    if not formula:
        return "неопределённого типа"
    formula_lower = formula.lower()
    if "sqrt" in formula_lower or "√" in formula_lower or "корень" in formula_lower:
        return _FUNCTION_TYPES["sqrt"]
    if "/x" in formula_lower:
        return _FUNCTION_TYPES["hyperbola"]
    if "x^2" in formula_lower or "x²" in formula_lower:
        return _FUNCTION_TYPES["parabola"]
    return _FUNCTION_TYPES["linear"]


async def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Solver form_match_mixed started (GOST-RESHATEL-2025)")

    source_params = (task_data.get("source_plot") or {}).get("params") or {}
    labels: List[str] = list(source_params.get("labels") or _LABEL_FALLBACK)
    options: Dict[str, str] = dict(source_params.get("options") or {})
    answers: List[str] = list(task_data.get("answer") or [])

    steps: List[Dict[str, Any]] = []
    display_pairs: List[str] = []

    for index, label in enumerate(labels):
        option_key = answers[index] if index < len(answers) else None
        formula = options.get(option_key, "N/A")
        function_type = _detect_formula_type(formula)

        description = f"Сопоставляем график {label} с формулами"
        calc_result = (
            f"График соответствует признакам {function_type}, поэтому выбираем формулу {formula} (вариант №{option_key})."
        )

        steps.append({
            "step_number": index + 1,
            "description": description,
            "formula_representation": formula,
            "calculation_result": calc_result,
            "result_unit": "N/A",
        })

        if option_key is not None:
            display_pairs.append(f"{label}-{option_key}")

    value_machine = "".join(answers) if answers else "N/A"
    value_display = ", ".join(display_pairs) if display_pairs else "N/A"

    solution_core = {
        "question_id": str(task_data.get("id", "form_match_mixed")),
        "explanation_idea": (
            "Сравниваем характер кривой (рост, вершина, асимптоты) с аналитической формой функций из списка."
        ),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": value_machine,
            "value_display": value_display,
            "unit": "N/A",
        },
        "hints": [
            "Линейная функция даёт прямую: наклон определяется знаком коэффициента перед x.",
            "Гипербола y = k/x имеет асимптоты и не определяется в точке x = 0.",
        ],
    }

    logger.info("Solver form_match_mixed finished (GOST-RESHATEL-2025)")
    return solution_core


__all__ = ["solve"]
