"""Validator for task 20 radical_equations subtype."""

from __future__ import annotations
from typing import Any, Dict, List


def validate_task_20_radical_equations(task: Dict[str, Any]) -> bool:
    """
    Проверяет корректность структуры и логики задания.
    Возвращает True, если всё корректно, иначе вызывает ValueError.
    """

    # --- 1. Общие поля ---
    required_fields = ["task_number", "topic", "subtype", "variables", "answer"]
    for field in required_fields:
        if field not in task:
            raise ValueError(f"Missing required field: {field}")

    variables = task["variables"]
    pattern = variables.get("solution_pattern")
    if pattern not in ("sum_zero", "same_radical_cancel", "cancel_identical_radicals"):
        raise ValueError(f"Invalid solution_pattern: {pattern}")

    # --- 2. Проверки по паттернам ---
    if pattern == "sum_zero":
        radicals = variables.get("radicals", {})
        if not isinstance(radicals, dict):
            raise ValueError("radicals must be a dictionary.")
        if not all(k in radicals for k in ("A", "B")):
            raise ValueError("Both radicals A and B must be present.")

        A_roots = radicals["A"].get("roots", [])
        B_roots = radicals["B"].get("roots", [])
        if not (isinstance(A_roots, list) and isinstance(B_roots, list)):
            raise ValueError("A.roots and B.roots must be lists.")
        if not all(isinstance(x, (int, float)) for x in A_roots + B_roots):
            raise ValueError("All roots in A and B must be numeric.")

        expected = sorted(set(A_roots) & set(B_roots))
        given = [float(x) for x in task.get("answer", [])]
        if not all(x in expected for x in given):
            raise ValueError(f"Answer mismatch: expected {expected}, got {given}")

    elif pattern == "same_radical_cancel":
        radicals = variables.get("radicals", {})
        if not isinstance(radicals, dict):
            raise ValueError("radicals must be a dictionary.")
        if not all(k in radicals for k in ("A", "B")):
            raise ValueError("Both radicals A and B must be present.")

        A_text = radicals["A"].get("text", "")
        B_text = radicals["B"].get("text", "")
        if not (A_text and B_text):
            raise ValueError("Missing A.text or B.text in radicals.")
        if "x" not in A_text or "x" not in B_text:
            raise ValueError("Both radicals must contain variable x.")

        extraneous = variables.get("extraneous_roots", [])
        if not isinstance(extraneous, list):
            raise ValueError("extraneous_roots must be a list (can be empty).")

    elif pattern == "cancel_identical_radicals":
        ident = variables.get("identical_radical", "")
        od_ineq = variables.get("od_inequality", "")
        req = variables.get("resulting_equation", {})

        if not ident or not isinstance(ident, str):
            raise ValueError("identical_radical must be a non-empty string.")
        if not od_ineq or not isinstance(od_ineq, str) or not od_ineq.startswith("x <="):
            raise ValueError("od_inequality must be like 'x <= N'.")

        # --- извлекаем S из 'x <= S' ---
        try:
            S = float(od_ineq.split("<=")[1].strip())
        except Exception as e:
            raise ValueError("Failed to parse od_inequality 'x <= S'.") from e

        # --- проверка resulting_equation ---
        if not isinstance(req, dict):
            raise ValueError("resulting_equation must be a dict.")
        coeffs = req.get("coeffs")
        roots = req.get("roots")
        if not (isinstance(coeffs, list) and len(coeffs) == 3):
            raise ValueError("resulting_equation.coeffs must be [c, b, a].")
        if coeffs[2] != 1:
            raise ValueError("Quadratic leading coeff a must be 1.")
        if not (isinstance(roots, list) and len(roots) == 2 and all(isinstance(x, (int, float)) for x in roots)):
            raise ValueError("resulting_equation.roots must be two numeric roots.")

        # корни должны удовлетворять уравнению
        c, b, a = coeffs
        for r in roots:
            val = a * r * r + b * r + c
            if abs(val) > 1e-6:
                raise ValueError("Provided roots do not satisfy resulting_equation.")

        # --- проверка ответов и ложных корней ---
        expected_valid = sorted([str(r) for r in roots if r <= S], key=lambda z: float(z))
        given = sorted(task.get("answer", []), key=lambda z: float(z))
        if given != expected_valid:
            raise ValueError(f"Answer mismatch for cancel_identical_radicals: expected {expected_valid}, got {given}")

        extraneous = variables.get("extraneous_roots", [])
        if not isinstance(extraneous, list):
            raise ValueError("extraneous_roots must be a list.")
        expected_extraneous = [r for r in roots if r > S]
        if sorted(extraneous) != sorted(expected_extraneous):
            raise ValueError("extraneous_roots mismatch.")

    # --- 3. Ответ ---
    if not isinstance(task["answer"], list):
        raise ValueError("Answer must be a list of strings.")
    if not all(isinstance(x, str) for x in task["answer"]):
        raise ValueError("Each answer must be a string.")

    return True


__all__ = ["validate_task_20_radical_equations"]
