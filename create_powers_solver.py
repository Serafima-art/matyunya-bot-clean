import json

# Код для создания powers_solver.py
code = '''# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import math
import re

IDEA_KEY_MAP: Dict[str, tuple] = {
    "powers_with_fractions": ("POWERS_FRACTIONS_IDEA", {}),
    "powers_of_ten": ("POWERS_OF_TEN_IDEA", {}),
}

@dataclass
class StepBuilder:
    """Построитель шагов решения."""
    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1

    def add(self, description_key: str, description_params: Optional[Dict[str, Any]] = None,
            formula_representation: Optional[str] = None, formula_general: Optional[str] = None,
            formula_calculation: Optional[str] = None, calculation_result: Optional[str] = None) -> None:
        step = {"step_number": self.counter, "description_key": description_key, "description_params": description_params or {}}
        if formula_representation: step["formula_representation"] = formula_representation
        if formula_general: step["formula_general"] = formula_general
        if formula_calculation: step["formula_calculation"] = formula_calculation
        if calculation_result: step["calculation_result"] = calculation_result
        self.steps.append(step)
        self.counter += 1

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    pattern = task_data.get("pattern")
    variables = task_data.get("variables", {})
    
    if not pattern:
        raise ValueError("Некорректные данные задачи: отсутствует pattern.")

    idea_key, idea_params = IDEA_KEY_MAP.get(pattern, ("GENERIC_IDEA", {}))

    if pattern == "powers_with_fractions":
        solution_core = _solve_powers_with_fractions(task_data, variables)
    elif pattern == "powers_of_ten":
        solution_core = _solve_powers_of_ten(task_data, variables)
    else:
        raise ValueError(f"Неизвестный паттерн: {pattern}")

    solution_core.update({
        "question_id": task_data.get("id", "task_6_powers"),
        "question_group": "TASK6_POWERS",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": idea_params,
        "hints_keys": [],
    })
    return solution_core

def _solve_powers_with_fractions(task_data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
    expression_tree = variables.get("expression_tree", {})
    expression_preview = _extract_expression_from_question(task_data)
    has_common_factor = variables.get("has_common_factor", False)
    operation = expression_tree.get("operation", "subtract")
    
    if has_common_factor:
        standard_builder = StepBuilder()
        rational_builder = StepBuilder()
        _generate_powers_fractions_standard_path(expression_tree, expression_preview, operation, standard_builder, task_data)
        _generate_powers_fractions_rational_path(expression_tree, expression_preview, operation, rational_builder, task_data)
        return {
            "explanation_idea": "",
            "calculation_paths": [
                {"path_title": "Способ 1: Стандартный (по порядку действий)", "steps": standard_builder.steps},
                {"path_title": "Способ 2: Рациональный (вынесение общего множителя)", "is_recommended": True, "steps": rational_builder.steps}
            ],
            "final_answer": {"value_machine": _compute_final_answer(task_data), "value_display": task_data.get("answer", "0"), "requested_part": "numerator", "final_answer_part": "numerator"},
            "hints": [],
        }
    else:
        builder = StepBuilder()
        _generate_powers_fractions_standard_path(expression_tree, expression_preview, operation, builder, task_data)
        return {
            "explanation_idea": "",
            "calculation_steps": builder.steps,
            "final_answer": {"value_machine": _compute_final_answer(task_data), "value_display": task_data.get("answer", "0"), "requested_part": "numerator", "final_answer_part": "numerator"},
            "hints": [],
        }

def _solve_powers_of_ten(task_data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
    expression_tree = variables.get("expression_tree", {})
    expression_preview = _extract_expression_from_question(task_data)
    builder = StepBuilder()
    _generate_powers_of_ten_path(expression_tree, expression_preview, builder, task_data)
    return {
        "explanation_idea": "",
        "calculation_steps": builder.steps,
        "final_answer": {"value_machine": _compute_final_answer(task_data), "value_display": task_data.get("answer", "0"), "requested_part": "numerator", "final_answer_part": "numerator"},
        "hints": [],
    }

def _generate_powers_fractions_standard_path(expression_tree: Dict[str, Any], expression_preview: str, operation: str, builder: StepBuilder, task_data: Dict[str, Any]) -> None:
    builder.add("INITIAL_EXPRESSION", {"expression": expression_preview}, expression_preview)
    power_info = _extract_power_fraction_info(expression_tree)
    if power_info:
        base_num, base_den, power, first_mult = power_info.values()
        result_num, result_den = base_num ** power, base_den ** power
        builder.add("POWER_OF_FRACTION", {"base_num": base_num, "base_den": base_den, "power": power, "result_num": result_num, "result_den": result_den}, 
                   formula_general="(a/b)^n = a^n / b^n", formula_calculation=f"({base_num}/{base_den})^{power} = {result_num}/{result_den}")
        if first_mult:
            m_num, m_den = first_mult * result_num, result_den
            gcd = math.gcd(m_num, m_den)
            if gcd > 1: m_num, m_den = m_num // gcd, m_den // gcd
            builder.add("MULTIPLY_FRACTION", {"integer": first_mult, "frac_num": result_num, "frac_den": result_den, "result_num": m_num, "result_den": m_den},
                       formula_calculation=f"{first_mult} * {result_num}/{result_den} = {m_num}/{m_den}")
    second_info = _extract_second_term_info(expression_tree)
    if second_info:
        m_c, s_n, s_d = second_info.values()
        if m_c:
            s_num, s_den = m_c * s_n, s_d
            gcd2 = math.gcd(s_num, s_den)
            if gcd2 > 1: s_num, s_den = s_num // gcd2, s_den // gcd2
            builder.add("MULTIPLY_FRACTION", {"integer": m_c, "frac_num": s_n, "frac_den": s_d, "result_num": s_num, "result_den": s_den})
    builder.add("FINAL_CALCULATION", {"operation": "вычитание" if operation == "subtract" else "сложение"})

def _generate_powers_fractions_rational_path(expression_tree: Dict[str, Any], expression_preview: str, operation: str, builder: StepBuilder, task_data: Dict[str, Any]) -> None:
    builder.add("INITIAL_EXPRESSION", {"expression": expression_preview}, expression_preview)
    power_info = _extract_power_fraction_info(expression_tree)
    if power_info:
        builder.add("RATIONAL_PATH_IDEA", {"common_fraction": f"{power_info['num']}/{power_info['den']}"})
        builder.add("POWER_AS_PRODUCT", {"base_num": power_info["num"], "base_den": power_info["den"], "power": power_info["power"]})
        builder.add("FACTORING_OUT", {"common_fraction": f"{power_info['num']}/{power_info['den']}"})
        builder.add("CALCULATE_IN_PARENTHESES", {})
        builder.add("FINAL_MULTIPLICATION_RATIONAL", {})

def _generate_powers_of_ten_path(expression_tree: Dict[str, Any], expression_preview: str, builder: StepBuilder, task_data: Dict[str, Any]) -> None:
    builder.add("INITIAL_EXPRESSION", {"expression": expression_preview}, expression_preview)
    builder.add("EXPANDING_PARENTHESES", {}, formula_general="(ab)^n = a^n b^n, (a^n)^m = a^nm")
    builder.add("SUBSTITUTING_RESULT", {})
    builder.add("GROUPING_FACTORS", {})
    builder.add("CALCULATING_POWERS", {}, formula_general="a^n * a^m = a^n+m")

def _extract_expression_from_question(task_data: Dict[str, Any]) -> Optional[str]:
    question_text = task_data.get("question_text", "")
    pattern = "Вычисли выражение:\\s*\\n(.+?)\\s*\\n\\nОтвет:"
    match = re.search(pattern, question_text, re.DOTALL)
    return match.group(1).strip() if match else None

def _extract_power_fraction_info(expression_tree: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if expression_tree.get("operation") in {"add", "subtract"}:
        left = expression_tree.get("operands", [None])[0]
        if left and left.get("operation") == "multiply":
            ops = left.get("operands", [])
            if len(ops) >= 2:
                first_mult = None
                for op in ops:
                    if op.get("type") == "integer": first_mult = op.get("value")
                    elif op.get("operation") == "power":
                        pow_ops = op.get("operands", [])
                        if len(pow_ops) == 2:
                            frac = pow_ops[0]
                            pw = pow_ops[1].get("value")
                            if frac.get("operation") == "divide":
                                f_ops = frac.get("operands", [])
                                if len(f_ops) == 2:
                                    return {"num": f_ops[0].get("value"), "den": f_ops[1].get("value"), "power": pw, "first_mult": first_mult}
    return None

def _extract_second_term_info(expression_tree: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if expression_tree.get("operation") in {"add", "subtract"}:
        right = expression_tree.get("operands", [None, None])[1]
        if right:
            if right.get("operation") == "multiply":
                ops = right.get("operands", [])
                if len(ops) >= 2:
                    mult, fnum, fden = None, None, None
                    for op in ops:
                        if op.get("type") == "integer": mult = op.get("value")
                        elif op.get("operation") == "divide":
                            d_ops = op.get("operands", [])
                            if len(d_ops) == 2: fnum, fden = d_ops[0].get("value"), d_ops[1].get("value")
                    if mult and fnum and fden: return {"mult": mult, "num": fnum, "den": fden}
            elif right.get("operation") == "divide":
                d_ops = right.get("operands", [])
                if len(d_ops) == 2: return {"mult": 1, "num": d_ops[0].get("value"), "den": d_ops[1].get("value")}
    return None

def _compute_final_answer(task_data: Dict[str, Any]) -> any:
    answer = task_data.get("answer", "0")
    answer_type = task_data.get("answer_type", "integer")
    if answer_type == "integer":
        try: return int(answer.replace(",", "."))
        except: return 0
    else:
        try: return float(answer.replace(",", "."))
        except: return 0.0
'''

path = r'c:\Users\user\Documents\matunya\matunya_bot_final\help_core\solvers\task_6\powers_solver.py'
with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
print(f'File created: {path}')
