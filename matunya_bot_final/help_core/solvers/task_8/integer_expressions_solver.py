from __future__ import annotations

import math
from fractions import Fraction
from typing import Any, Dict, List, Tuple


SUPERSCRIPT_MAP = {
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
    "+": "⁺",
}


def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Главная точка входа для help_core.
    На вход: task_data (как из БД/валидатора).
    На выход: solution_core по ГОСТ-2026.
    """
    if not isinstance(task_data, dict):
        raise ValueError("task_data должен быть словарём")

    if task_data.get("task_type") != "8" or task_data.get("subtype") != "integer_expressions":
        raise ValueError("Некорректный тип задания или подтип")

    pattern = task_data.get("solution_pattern")
    if pattern == "alg_power_fraction":
        return _solve_power_fraction(task_data)
    if pattern == "alg_radical_power":
        return _solve_radical_power(task_data)
    if pattern == "alg_radical_fraction":
        return _solve_radical_fraction(task_data)

    raise ValueError(f"Неизвестный solution_pattern: {pattern!r}")


def _solve_power_fraction(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Решатель для solution_pattern == 'alg_power_fraction'."""
    steps = _build_steps_for_power_fraction(task_data)
    answer_str = task_data["answer"]
    return {
        "question_id": "task8_integer_expressions_alg_power_fraction",
        "question_group": "task_8_integer_expressions",
        "explanation_idea": (
            "Сначала приводим выражение к самой простой степени, используя свойства степеней "
            "(степень в степени, умножение и деление степеней), а уже потом подставляем число вместо переменной."
        ),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": _convert_answer_value(answer_str),
            "value_display": answer_str,
            "unit": None,
        },
        "hints": [
            "При умножении степеней с одним основанием показатели складываются: aᵐ · aⁿ = aᵐ⁺ⁿ.",
            "При делении степеней с одним основанием показатели вычитаются: aᵐ : aⁿ = aᵐ⁻ⁿ.",
            "Степень в степени означает перемножение показателей: (aᵐ)ⁿ = aᵐⁿ.",
            "Отрицательная степень — это просто запись дроби: a⁻ⁿ = 1 / aⁿ.",
            "Число подставляем в самую последнюю, уже упрощённую форму выражения.",
        ],
        "validation_code": None,
    }


def _solve_radical_power(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Решатель для solution_pattern == 'alg_radical_power'."""
    steps = _build_steps_for_radical_power(task_data)
    answer_str = task_data["answer"]
    return {
        "question_id": "task8_integer_expressions_alg_radical_power",
        "question_group": "task_8_integer_expressions",
        "explanation_idea": (
            "Сначала упрощаем выражение под корнем, используя свойства степеней, затем извлекаем корень "
            "и только после этого подставляем значение переменной."
        ),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": _convert_answer_value(answer_str),
            "value_display": answer_str,
            "unit": None,
        },
        "hints": [
            "При делении степеней с одинаковым основанием вычитаем показатели: aᵐ : aⁿ = aᵐ⁻ⁿ.",
            "Корень от произведения можно вынести на множители: √(k·x) = √k · √x.",
            "Если показатель степени чётный, под корнем всегда получается неотрицательное число.",
            "Извлекаем корень только после упрощения выражения под радикалом.",
            "Число подставляем уже в разложенную форму без лишних степеней.",
        ],
        "validation_code": None,
    }


def _solve_radical_fraction(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Решатель для solution_pattern == 'alg_radical_fraction'."""
    steps = _build_steps_for_radical_fraction(task_data)
    answer_str = task_data["answer"]
    return {
        "question_id": "task8_integer_expressions_alg_radical_fraction",
        "question_group": "task_8_integer_expressions",
        "explanation_idea": (
            "Сначала раскладываем корни на множители и выносим из-под корня всё, что можно, затем сокращаем "
            "одинаковые корни в числителе и знаменателе, и только потом подставляем числа."
        ),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": _convert_answer_value(answer_str),
            "value_display": answer_str,
            "unit": None,
        },
        "hints": [
            "Корень из произведения равен произведению корней: √(ab) = √a · √b.",
            "Полные квадраты выносим из-под корня: √(k²·x) = k√x.",
            "Одинаковые множители под корнем можно сократить, если они стоят в числителе и знаменателе.",
            "Сначала упростите корни, потом переходите к подстановке чисел.",
            "Оставляйте под корнем только те множители, которые нельзя вынести целиком.",
        ],
        "validation_code": None,
    }


def _build_steps_for_power_fraction(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    variables = task_data["variables"]
    if tree.get("type") != "fraction":
        raise ValueError("Для alg_power_fraction ожидаем дробь в корне выражения")

    steps: List[Dict[str, Any]] = []
    step_number = 1

    original_expr = _format_expression_from_tree(tree)
    steps.append(
        {
            "step_number": step_number,
            "description": "Рассмотрим исходное выражение.",
            "formula_general": None,
            "formula_calculation": None,
            "expression_after_step": original_expr,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    collapsed_tree, power_transforms = _collapse_power_of_power(tree)
    expr_after_collapse = _format_expression_from_tree(collapsed_tree)
    formula_calc = None
    if power_transforms:
        transform = power_transforms[0]
        base_str = _format_expression_from_tree(transform["base"])
        if _needs_parentheses_in_power(transform["base"]):
            base_str = f"({base_str})"
        inner = _to_superscript(transform["inner"])
        outer = _to_superscript(transform["outer"])
        result_sup = _to_superscript(transform["result"])
        formula_calc = f"{base_str}{inner}{outer} = {base_str}{result_sup}"
    steps.append(
        {
            "step_number": step_number,
            "description": "Раскрываем степень в степени.",
            "formula_general": "(aᵐ)ⁿ = aᵐⁿ",
            "formula_calculation": formula_calc,
            "expression_after_step": expr_after_collapse,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    num_coeff, num_powers, num_details = _combine_product_to_map(collapsed_tree["numerator"])
    den_expr = _format_expression_from_tree(collapsed_tree["denominator"])
    num_expr = _format_product_from_map(num_coeff, num_powers)
    expr_after_sum = f"{num_expr} / {den_expr}"
    steps.append(
        {
            "step_number": step_number,
            "description": "Перемножаем степени в числителе.",
            "formula_general": "aᵐ · aⁿ = aᵐ⁺ⁿ",
            "formula_calculation": _build_sum_formula(num_details),
            "expression_after_step": expr_after_sum,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    den_coeff, den_powers = _extract_linear_powers(collapsed_tree["denominator"])
    combined_coeff = num_coeff / den_coeff
    combined_powers = _subtract_power_maps(num_powers, den_powers)
    expr_after_div = _format_product_from_map(combined_coeff, combined_powers)
    steps.append(
        {
            "step_number": step_number,
            "description": "Делим степени с одинаковыми основаниями.",
            "formula_general": "aᵐ : aⁿ = aᵐ⁻ⁿ",
            "formula_calculation": _build_division_formula(num_powers, den_powers),
            "expression_after_step": expr_after_div,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    substitution_expr = _format_numeric_substitution(combined_coeff, combined_powers, variables)
    numeric_value = _evaluate_expression_map(combined_coeff, combined_powers, variables)
    calc_result = _format_number(numeric_value)
    steps.append(
        {
            "step_number": step_number,
            "description": "Подставляем значение переменной.",
            "formula_general": None,
            "formula_calculation": None,
            "expression_after_step": substitution_expr,
            "calculation_result": calc_result,
            "result_unit": None,
        }
    )
    step_number += 1

    answer_display = task_data["answer"]
    steps.append(
        {
            "step_number": step_number,
            "description": "Переводим результат в десятичный вид.",
            "formula_general": None,
            "formula_calculation": f"{calc_result} = {answer_display}",
            "expression_after_step": answer_display,
            "calculation_result": answer_display,
            "result_unit": None,
        }
    )

    return steps


def _build_steps_for_radical_power(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    variables = task_data["variables"]
    if tree.get("type") != "sqrt":
        raise ValueError("Для alg_radical_power ожидаем корень верхнего уровня")

    steps: List[Dict[str, Any]] = []
    step_number = 1

    original_expr = _format_expression_from_tree(tree)
    steps.append(
        {
            "step_number": step_number,
            "description": "Рассмотрим исходное выражение под корнем.",
            "formula_general": None,
            "formula_calculation": None,
            "expression_after_step": original_expr,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    radicand = tree["radicand"]
    simplified_radicand_coeff, simplified_radicand_powers = _extract_linear_powers(radicand)
    simplified_radicand_str = _format_product_from_map(simplified_radicand_coeff, simplified_radicand_powers)
    expr_after_simplify = f"√({simplified_radicand_str})"

    div_formula = None
    if radicand.get("type") == "fraction":
        num_coeff, num_powers = _extract_linear_powers(radicand["numerator"])
        den_coeff, den_powers = _extract_linear_powers(radicand["denominator"])
        _ = den_coeff
        div_formula = _build_division_formula(num_powers, den_powers)
    steps.append(
        {
            "step_number": step_number,
            "description": "Упрощаем степень под корнем.",
            "formula_general": "aᵐ : aⁿ = aᵐ⁻ⁿ",
            "formula_calculation": div_formula,
            "expression_after_step": expr_after_simplify,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    split_expr = _format_split_root(simplified_radicand_coeff, simplified_radicand_powers)
    steps.append(
        {
            "step_number": step_number,
            "description": "Разносим корень на множители.",
            "formula_general": "√(k·x) = √k · √x",
            "formula_calculation": None,
            "expression_after_step": split_expr,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    extracted_expr, after_root_coeff, after_root_powers, inner_coeff, inner_powers = _format_extracted_root(
        simplified_radicand_coeff, simplified_radicand_powers, with_components=True
    )
    steps.append(
        {
            "step_number": step_number,
            "description": "Извлекаем корень из полного квадрата.",
            "formula_general": "√a² = a",
            "formula_calculation": None,
            "expression_after_step": extracted_expr,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    substitution_expr = _format_numeric_substitution(after_root_coeff, after_root_powers, variables)
    inside_value = _evaluate_expression_map(inner_coeff, inner_powers, variables)
    if inside_value != 1:
        substitution_expr = f"{substitution_expr} · √({_format_number(inside_value)})"
    numeric_value = _evaluate_radical_composed(after_root_coeff, after_root_powers, inner_coeff, inner_powers, variables)
    calc_result = _format_number(numeric_value)
    steps.append(
        {
            "step_number": step_number,
            "description": "Подставляем значение переменной и считаем.",
            "formula_general": None,
            "formula_calculation": None,
            "expression_after_step": substitution_expr,
            "calculation_result": calc_result,
            "result_unit": None,
        }
    )
    step_number += 1

    answer_display = task_data["answer"]
    steps.append(
        {
            "step_number": step_number,
            "description": "Записываем десятичный ответ.",
            "formula_general": None,
            "formula_calculation": f"{calc_result} = {answer_display}",
            "expression_after_step": answer_display,
            "calculation_result": answer_display,
            "result_unit": None,
        }
    )

    return steps


def _build_steps_for_radical_fraction(task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    tree = task_data["expression_tree"]
    variables = task_data["variables"]
    if tree.get("type") != "fraction":
        raise ValueError("Для alg_radical_fraction ожидаем дробь верхнего уровня")

    steps: List[Dict[str, Any]] = []
    step_number = 1

    original_expr = _format_expression_from_tree(tree)
    steps.append(
        {
            "step_number": step_number,
            "description": "Записываем исходную дробь с корнями.",
            "formula_general": None,
            "formula_calculation": None,
            "expression_after_step": original_expr,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    numerator_factors = _extract_factors(tree["numerator"])
    sqrt_positions = [i for i, node in enumerate(numerator_factors) if node.get("type") == "sqrt"]

    for pos_index, pos in enumerate(sqrt_positions):
        sqrt_node = numerator_factors[pos]
        comp = _decompose_sqrt_node(sqrt_node)
        numerator_factors[pos] = {"__custom_str": _format_radical_component(*comp)}
        expr_after_step = _format_fraction_with_custom_numerator(numerator_factors, tree["denominator"])
        steps.append(
            {
                "step_number": step_number,
                "description": f"Раскладываем корень {pos_index + 1} в числителе.",
                "formula_general": "√(k²·x) = k√x",
                "formula_calculation": None,
                "expression_after_step": expr_after_step,
                "calculation_result": None,
                "result_unit": None,
            }
        )
        step_number += 1

    num_out, num_powers, num_in_coeff, num_in_powers = _simplify_radical_product(tree["numerator"])
    numerator_combined = _format_radical_component(num_out, num_powers, num_in_coeff, num_in_powers)
    steps.append(
        {
            "step_number": step_number,
            "description": "Перемножаем упрощённые множители в числителе.",
            "formula_general": None,
            "formula_calculation": None,
            "expression_after_step": numerator_combined,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    den_out, den_powers, den_in_coeff, den_in_powers = _simplify_radical_product(tree["denominator"])
    numerator_full = numerator_combined
    denominator_full = _format_radical_component(den_out, den_powers, den_in_coeff, den_in_powers)
    expr_fraction = f"{numerator_full} / {denominator_full}"
    steps.append(
        {
            "step_number": step_number,
            "description": "Подставляем результат в дробь.",
            "formula_general": None,
            "formula_calculation": None,
            "expression_after_step": expr_fraction,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    reduced_out_coeff = num_out / den_out
    reduced_out_powers = _subtract_power_maps(num_powers, den_powers)
    reduced_in_coeff = num_in_coeff / den_in_coeff
    reduced_in_powers = _subtract_power_maps(num_in_powers, den_in_powers)
    reduced_expr = _format_radical_component(reduced_out_coeff, reduced_out_powers, reduced_in_coeff, reduced_in_powers)
    steps.append(
        {
            "step_number": step_number,
            "description": "Сокращаем одинаковые корни в числителе и знаменателе.",
            "formula_general": None,
            "formula_calculation": None,
            "expression_after_step": reduced_expr,
            "calculation_result": None,
            "result_unit": None,
        }
    )
    step_number += 1

    substitution_expr = _format_numeric_substitution(reduced_out_coeff, reduced_out_powers, variables)
    inside_value = _evaluate_expression_map(reduced_in_coeff, reduced_in_powers, variables)
    if inside_value != 1:
        substitution_expr = f"{substitution_expr} · √({_format_number(inside_value)})"
    numeric_value = _evaluate_radical_composed(
        reduced_out_coeff, reduced_out_powers, reduced_in_coeff, reduced_in_powers, variables
    )
    calc_result = _format_number(numeric_value)
    steps.append(
        {
            "step_number": step_number,
            "description": "Подставляем значения переменных и считаем.",
            "formula_general": None,
            "formula_calculation": None,
            "expression_after_step": substitution_expr,
            "calculation_result": calc_result,
            "result_unit": None,
        }
    )
    step_number += 1

    answer_display = task_data["answer"]
    steps.append(
        {
            "step_number": step_number,
            "description": "Записываем десятичный ответ.",
            "formula_general": None,
            "formula_calculation": f"{calc_result} = {answer_display}",
            "expression_after_step": answer_display,
            "calculation_result": answer_display,
            "result_unit": None,
        }
    )

    return steps


def _format_expression_from_tree(tree: Dict[str, Any]) -> str:
    """
    Строит человекочитаемую строку выражения из expression_tree.
    Формат строго по «азбуке» задания 8.
    """
    node_type = tree.get("type")
    if node_type == "integer":
        return str(tree["value"])
    if node_type == "variable":
        return tree["name"]
    if node_type == "power":
        base = tree["base"]
        exp = tree["exp"]
        if exp.get("type") != "integer":
            raise ValueError("Ожидаем целочисленную степень в power")
        base_str = _format_expression_from_tree(base)
        if _needs_parentheses_in_power(base):
            base_str = f"({base_str})"
        exp_sup = _to_superscript(exp["value"])
        return f"{base_str}{exp_sup}"
    if node_type == "product":
        factors = tree.get("factors", [])
        formatted = []
        for factor in factors:
            factor_str = _format_expression_from_tree(factor)
            if factor.get("type") == "fraction":
                factor_str = f"({factor_str})"
            formatted.append(factor_str)
        return " · ".join(formatted)
    if node_type == "fraction":
        num = _format_expression_from_tree(tree["numerator"])
        den = _format_expression_from_tree(tree["denominator"])
        if tree["numerator"].get("type") in {"product", "fraction"}:
            num = f"({num})"
        if tree["denominator"].get("type") in {"product", "fraction"}:
            den = f"({den})"
        return f"{num} / {den}"
    if node_type == "sqrt":
        radicand = _format_expression_from_tree(tree["radicand"])
        return f"√({radicand})"
    if "__custom_str" in tree:
        return tree["__custom_str"]
    raise ValueError(f"Неизвестный тип узла: {node_type}")


def _needs_parentheses_in_power(node: Dict[str, Any]) -> bool:
    """Решаем, нужны ли скобки вокруг основания степени."""
    return node.get("type") in {"power", "product", "fraction"} or (
        node.get("type") == "integer" and node.get("value", 0) < 0
    )


def _to_superscript(value: int | str) -> str:
    """Переводит число или строку в надстрочный формат."""
    text = str(value)
    return "".join(SUPERSCRIPT_MAP.get(ch, ch) for ch in text)


def _convert_answer_value(answer_str: str) -> int | float:
    """Преобразуем значение ответа из строки в int/float для value_machine."""
    if "," in answer_str:
        return float(answer_str.replace(",", "."))
    if "." in answer_str:
        return float(answer_str)
    return int(answer_str)


def _collapse_power_of_power(tree: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Сворачивает (xᵐ)ⁿ → xᵐⁿ и собирает информацию о преобразованиях
    для формулы расчёта.
    """
    transforms: List[Dict[str, Any]] = []

    def _walk(node: Dict[str, Any]) -> Dict[str, Any]:
        node_type = node.get("type")
        if node_type == "power":
            base_processed = _walk(node["base"])
            exp_processed = _walk(node["exp"])
            if base_processed.get("type") == "power":
                inner_exp = base_processed["exp"]
                outer_exp = exp_processed
                if inner_exp.get("type") != "integer" or outer_exp.get("type") != "integer":
                    return {"type": "power", "base": base_processed, "exp": exp_processed}
                new_exp_value = inner_exp["value"] * outer_exp["value"]
                transforms.append(
                    {
                        "base": base_processed["base"],
                        "inner": inner_exp["value"],
                        "outer": outer_exp["value"],
                        "result": new_exp_value,
                    }
                )
                return {"type": "power", "base": base_processed["base"], "exp": {"type": "integer", "value": new_exp_value}}
            return {"type": "power", "base": base_processed, "exp": exp_processed}
        if node_type == "product":
            return {"type": "product", "factors": [_walk(f) for f in node.get("factors", [])]}
        if node_type == "fraction":
            return {"type": "fraction", "numerator": _walk(node["numerator"]), "denominator": _walk(node["denominator"])}
        if node_type == "sqrt":
            return {"type": "sqrt", "radicand": _walk(node["radicand"])}
        return dict(node)

    collapsed = _walk(tree)
    return collapsed, transforms


def _extract_linear_powers(node: Dict[str, Any]) -> Tuple[Fraction, Dict[str, int]]:
    """
    Разворачивает выражение в коэффициент и показатели степеней по переменным.
    Не поддерживает sqrt (для них отдельные декомпозиции).
    """
    node_type = node.get("type")
    if node_type == "integer":
        return Fraction(node["value"]), {}
    if node_type == "variable":
        return Fraction(1), {node["name"]: 1}
    if node_type == "power":
        base_coeff, base_powers = _extract_linear_powers(node["base"])
        exp_node = node["exp"]
        if exp_node.get("type") != "integer":
            raise ValueError("Ожидаем целочисленную степень")
        exp_value = exp_node["value"]
        coeff = base_coeff ** exp_value
        powers = {var: power * exp_value for var, power in base_powers.items()}
        return coeff, powers
    if node_type == "product":
        coeff = Fraction(1)
        powers: Dict[str, int] = {}
        for factor in node.get("factors", []):
            f_coeff, f_powers = _extract_linear_powers(factor)
            coeff *= f_coeff
            for var, power in f_powers.items():
                powers[var] = powers.get(var, 0) + power
        return coeff, powers
    if node_type == "fraction":
        num_coeff, num_powers = _extract_linear_powers(node["numerator"])
        den_coeff, den_powers = _extract_linear_powers(node["denominator"])
        coeff = num_coeff / den_coeff
        powers = _subtract_power_maps(num_powers, den_powers)
        return coeff, powers
    raise ValueError(f"Неожиданный тип для разворачивания степеней: {node_type}")


def _subtract_power_maps(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]:
    """Вычитает показатели степеней правой карты из левой."""
    result: Dict[str, int] = {}
    all_vars = set(left) | set(right)
    for var in all_vars:
        result[var] = left.get(var, 0) - right.get(var, 0)
    return {var: power for var, power in result.items() if power != 0}


def _combine_product_to_map(node: Dict[str, Any]) -> Tuple[Fraction, Dict[str, int], Dict[str, List[int]]]:
    """Суммирует множители произведения в коэффициент и показатели степеней."""
    factors = node.get("factors", []) if node.get("type") == "product" else [node]
    coeff = Fraction(1)
    powers: Dict[str, int] = {}
    details: Dict[str, List[int]] = {}
    for factor in factors:
        f_coeff, f_powers = _extract_linear_powers(factor)
        coeff *= f_coeff
        for var, power in f_powers.items():
            powers[var] = powers.get(var, 0) + power
            details.setdefault(var, []).append(power)
    return coeff, powers, details


def _format_product_from_map(coeff: Fraction, powers: Dict[str, int]) -> str:
    """Собирает строку произведения из коэффициента и показателей степеней."""
    parts: List[str] = []
    coeff_str = _format_fraction_value(coeff)
    if coeff != 1 or not powers:
        parts.append(coeff_str)
    for var in sorted(powers):
        exp_value = powers[var]
        if exp_value == 0:
            continue
        if exp_value == 1:
            parts.append(var)
        else:
            parts.append(f"{var}{_to_superscript(exp_value)}")
    if not parts:
        return "1"
    return " · ".join(parts)


def _format_fraction_value(value: Fraction) -> str:
    """Форматирует Fraction как строку."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _build_sum_formula(details: Dict[str, List[int]]) -> str | None:
    """Строит строку вида a¹⁵ · a³ = a¹⁵⁺³; для нескольких переменных объединяет через '; '."""
    if not details:
        return None
    parts = []
    for var in sorted(details):
        exps = details[var]
        if len(exps) < 2:
            continue
        left = " · ".join(f"{var}{_to_superscript(exp)}" for exp in exps)
        right_sup = _to_superscript(sum(exps))
        parts.append(f"{left} = {var}{right_sup}")
    return "; ".join(parts) if parts else None


def _build_division_formula(num_powers: Dict[str, int], den_powers: Dict[str, int]) -> str | None:
    """Строит формулу для деления степеней."""
    if not num_powers and not den_powers:
        return None
    parts = []
    for var in sorted(set(num_powers) | set(den_powers)):
        left_sup = _to_superscript(num_powers.get(var, 0))
        right_sup = _to_superscript(den_powers.get(var, 0))
        res_sup = _to_superscript(num_powers.get(var, 0) - den_powers.get(var, 0))
        parts.append(f"{var}{left_sup} / {var}{right_sup} = {var}{res_sup}")
    return "; ".join(parts)


def _format_numeric_substitution(coeff: Fraction, powers: Dict[str, int], variables: Dict[str, float]) -> str:
    """Формирует строку после подстановки чисел в основание степени."""
    parts: List[str] = []
    if coeff != 1 or not powers:
        parts.append(_format_fraction_value(coeff))
    for var in sorted(powers):
        if var not in variables:
            raise ValueError(f"Не передано значение для переменной {var!r}")
        base_val = variables[var]
        base_str = _format_base_number(base_val)
        exp = powers[var]
        exp_sup = _to_superscript(exp)
        parts.append(f"{base_str}{exp_sup}")
    return " · ".join(parts) if parts else "1"


def _format_base_number(value: float) -> str:
    """Формирует базовое число с запятой для отображения, если это не целое."""
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        return str(int(value))
    text = str(value).replace(".", ",")
    return text


def _evaluate_expression_map(coeff: Fraction, powers: Dict[str, int], variables: Dict[str, float]) -> Fraction:
    """Считает коэффициент * ∏ value^power используя Fraction для аккуратности."""
    result = coeff
    for var, power in powers.items():
        if var not in variables:
            raise ValueError(f"Не передано значение для переменной {var!r}")
        base_val = Fraction(str(variables[var]))
        if power >= 0:
            result *= base_val ** power
        else:
            result /= base_val ** (-power)
    return result


def _format_number(value: Fraction | float) -> str:
    """Форматирует число (Fraction либо float) в строку с запятой при необходимости."""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return f"{value.numerator}/{value.denominator}"
    return str(value).replace(".", ",")


def _format_split_root(coeff: Fraction, powers: Dict[str, int]) -> str:
    """
    Форматирует выражение √(coeff · vars) как произведение корней:
    √coeff · √(vars часть).
    """
    coeff_part = _format_fraction_value(coeff)
    vars_part = _format_product_from_map(Fraction(1), powers)
    if vars_part == "1":
        return f"√{coeff_part}"
    return f"√{coeff_part} · √({vars_part})"


def _sqrt_fraction_if_perfect(value: Fraction) -> Fraction | None:
    """Возвращает корень из дроби, если числитель и знаменатель — полные квадраты."""
    num_sqrt = int(math.isqrt(value.numerator))
    den_sqrt = int(math.isqrt(value.denominator))
    if num_sqrt * num_sqrt == value.numerator and den_sqrt * den_sqrt == value.denominator:
        return Fraction(num_sqrt, den_sqrt)
    return None


def _format_extracted_root(
    coeff: Fraction, powers: Dict[str, int], with_components: bool = False
) -> Tuple[str, Fraction, Dict[str, int], Fraction, Dict[str, int]] | str:
    """
    Возвращает строку после извлечения корня, а при необходимости и новые компоненты
    (коэффициент и показатели), чтобы использовать их дальше.
    """
    sqrt_coeff = _sqrt_fraction_if_perfect(coeff) or Fraction(1)
    outside_powers = {var: power // 2 for var, power in powers.items() if power // 2 != 0}
    inside_coeff = coeff / (sqrt_coeff ** 2)
    inside_powers = {var: power % 2 for var, power in powers.items() if power % 2 != 0}
    outside_part = _format_product_from_map(sqrt_coeff, outside_powers)
    if inside_coeff == 1 and not inside_powers:
        result_expr = outside_part
    else:
        inside_part = _format_product_from_map(inside_coeff, inside_powers)
        if outside_part == "1":
            result_expr = f"√({inside_part})"
        else:
            result_expr = f"{outside_part} · √({inside_part})"
    if with_components:
        return result_expr, sqrt_coeff, outside_powers, inside_coeff, inside_powers
    return result_expr


def _extract_factors(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Возвращает список множителей для product либо одиночный элемент."""
    if node.get("type") == "product":
        return list(node.get("factors", []))
    return [node]


def _decompose_under_sqrt(coeff: Fraction, powers: Dict[str, int]) -> Tuple[Fraction, Dict[str, int], Fraction, Dict[str, int]]:
    """
    Делит радиканд на вынесенную часть (outside) и оставшуюся под корнем (inside).
    """
    outside_coeff = _sqrt_fraction_if_perfect(coeff) or Fraction(1)
    inside_coeff = coeff / (outside_coeff ** 2)
    outside_powers = {var: power // 2 for var, power in powers.items() if power // 2 != 0}
    inside_powers = {var: power % 2 for var, power in powers.items() if power % 2 != 0}
    return outside_coeff, outside_powers, inside_coeff, inside_powers


def _decompose_sqrt_node(node: Dict[str, Any]) -> Tuple[Fraction, Dict[str, int], Fraction, Dict[str, int]]:
    """Декомпозирует sqrt-узел в (outside_coeff, outside_powers, inside_coeff, inside_powers)."""
    if node.get("type") != "sqrt":
        raise ValueError("Ожидаем sqrt-узел")
    coeff, powers = _extract_linear_powers(node["radicand"])
    return _decompose_under_sqrt(coeff, powers)


def _format_radical_component(
    outside_coeff: Fraction, outside_powers: Dict[str, int], inside_coeff: Fraction, inside_powers: Dict[str, int]
) -> str:
    """Собирает выражение вида (outside)·√(inside)."""
    outside_part = _format_product_from_map(outside_coeff, outside_powers)
    inside_part = _format_product_from_map(inside_coeff, inside_powers)
    if inside_part == "1":
        return outside_part
    if outside_part == "1":
        return f"√({inside_part})"
    return f"{outside_part}√({inside_part})"


def _format_fraction_with_custom_numerator(numerator_factors: List[Dict[str, Any]], denominator: Dict[str, Any]) -> str:
    """Формирует строку дроби, где часть множителей уже заменена на кастомные строки."""
    num_parts = []
    for factor in numerator_factors:
        if "__custom_str" in factor:
            num_parts.append(factor["__custom_str"])
        else:
            num_parts.append(_format_expression_from_tree(factor))
    numerator_str = " · ".join(num_parts)
    denominator_str = _format_expression_from_tree(denominator)
    return f"{numerator_str} / {denominator_str}"


def _simplify_radical_product(node: Dict[str, Any]) -> Tuple[Fraction, Dict[str, int], Fraction, Dict[str, int]]:
    """
    Упрощает произведение, содержащие корни: возвращает outside_coeff, outside_powers, inside_coeff, inside_powers.
    """
    factors = _extract_factors(node)
    outside_coeff = Fraction(1)
    outside_powers: Dict[str, int] = {}
    inside_coeff = Fraction(1)
    inside_powers: Dict[str, int] = {}

    for factor in factors:
        if factor.get("type") == "sqrt":
            out_c, out_p, in_c, in_p = _decompose_sqrt_node(factor)
            outside_coeff *= out_c
            for var, power in out_p.items():
                outside_powers[var] = outside_powers.get(var, 0) + power
            inside_coeff *= in_c
            for var, power in in_p.items():
                inside_powers[var] = inside_powers.get(var, 0) + power
        else:
            f_coeff, f_powers = _extract_linear_powers(factor)
            outside_coeff *= f_coeff
            for var, power in f_powers.items():
                outside_powers[var] = outside_powers.get(var, 0) + power

    return outside_coeff, outside_powers, inside_coeff, inside_powers


def _evaluate_radical_composed(
    outside_coeff: Fraction,
    outside_powers: Dict[str, int],
    inside_coeff: Fraction,
    inside_powers: Dict[str, int],
    variables: Dict[str, float],
) -> Fraction:
    """Вычисляет значение для outside·√(inside)."""
    outside_value = _evaluate_expression_map(outside_coeff, outside_powers, variables)
    inside_value = _evaluate_expression_map(inside_coeff, inside_powers, variables)
    inside_float = float(inside_value) ** 0.5
    return Fraction(str(float(outside_value) * inside_float))
