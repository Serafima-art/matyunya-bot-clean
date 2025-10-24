# matunya_bot_final/help_core/solvers/task_6/powers_solver.py

"""
Решатель для подтипа 'powers' (Задание 6).
Содержит "внутренний роутер" и поддерживает возведение в степень.
Модуль следует стандарту ГОСТ-2026.
"""

from fractions import Fraction
from typing import Dict, List, Any
import math

# =============================================================================
# ★★★ ГЛАВНАЯ ФУНКЦИЯ-ДИСПЕТЧЕР (ВНУТРЕННИЙ РОУТЕР) ★★★
# =============================================================================

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Главная функция-роутер для подтипа 'powers'.
    Вызывает универсальный рекурсивный решатель.
    """
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    if not expression_tree:
        raise ValueError("Отсутствует 'expression_tree' в task_data")

    steps = []
    step_counter = [1]

    final_fraction = _evaluate_tree(expression_tree, steps, step_counter)
    _add_decimal_conversion_step(final_fraction, steps, step_counter)
    decimal_value = float(final_fraction)

    return {
        "question_id": task_data.get("id", "placeholder_id"),
        "question_group": "TASK6_POWERS",
        "explanation_idea": _generate_explanation_idea(),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": decimal_value,
            "value_display": str(decimal_value)
        },
        "hints": _generate_hints()
    }

# =============================================================================
# ★★★ УНИВЕРСАЛЬНЫЙ РЕКУРСИВНЫЙ ДВИЖОК (ВСЯ МАТЕМАТИКА) ★★★
# =============================================================================

def _evaluate_tree(node: Dict[str, Any], steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Рекурсивно вычисляет выражение, преобразуя все числа в Fraction."""
    if node.get("type") == "common":
        return Fraction(node["value"][0], node["value"][1])

    if node.get("type") == "decimal":
        decimal_value = node["value"]
        fraction = Fraction(str(decimal_value))
        if decimal_value != int(decimal_value):
             _add_conversion_step(decimal_value, fraction, steps, step_counter)
        return fraction

    operation = node["operation"]
    operands = node["operands"]

    left = _evaluate_tree(operands[0], steps, step_counter)
    right = _evaluate_tree(operands[1], steps, step_counter)

    return _perform_operation(operation, left, right, steps, step_counter)

def _perform_operation(operation: str, left: Fraction, right: Fraction,
                       steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Выполняет математическую операцию, включая 'power'."""
    if operation == "add":
        return _perform_addition(left, right, steps, step_counter)
    elif operation == "subtract":
        return _perform_subtraction(left, right, steps, step_counter)
    elif operation == "multiply":
        return _perform_multiplication(left, right, steps, step_counter)
    elif operation == "divide":
        return _perform_division(left, right, steps, step_counter)
    elif operation == "power":
        return _perform_power(left, right, steps, step_counter)
    else:
        raise ValueError(f"Неизвестная операция: {operation}")


# =============================================================================
# ★★★ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (ПОЛНЫЙ КОМПЛЕКТ) ★★★
# =============================================================================

def _perform_power(base: Fraction, exponent: Fraction, steps: List[Dict], step_counter: List[int]) -> Fraction:
    if exponent.denominator != 1:
        raise ValueError(f"Степень должна быть целым числом, получено: {exponent}")
    exp_value = exponent.numerator
    result = base ** exp_value
    description = f"Возводим {_format_fraction(base)} в степень {exp_value}."
    formula_repr = f"({_format_fraction(base)})**{exp_value}"
    formula_calc = f"{formula_repr} = {_format_fraction(result)}"
    steps.append({"step_number": step_counter[0], "description": description, "formula_representation": formula_repr, "formula_calculation": formula_calc, "calculation_result": str(result)})
    step_counter[0] += 1
    return result

def _add_conversion_step(decimal_value: float, fraction: Fraction, steps: List[Dict], step_counter: List[int]) -> None:
    decimal_str = str(decimal_value)
    description = f"Преобразуем десятичную дробь {decimal_value} в обыкновенную."
    formula_repr = decimal_str
    if '.' in decimal_str and decimal_str.split('.')[1] != '0':
        decimal_places = len(decimal_str.split('.')[1])
        denominator = 10 ** decimal_places
        numerator = int(float(decimal_str) * denominator)
        intermediate_fraction = Fraction(numerator, denominator)
        formula_calc = f"{decimal_str} = {numerator}/{denominator}"
        if intermediate_fraction != fraction:
            formula_calc += f" = {_format_fraction(fraction)}"
    else:
        formula_calc = f"{decimal_str} = {_format_fraction(fraction)}"
    steps.append({"step_number": step_counter[0], "description": description, "formula_representation": formula_repr, "formula_calculation": formula_calc, "calculation_result": _format_fraction(fraction)})
    step_counter[0] += 1

def _perform_addition(left: Fraction, right: Fraction, steps: List[Dict], step_counter: List[int]) -> Fraction:
    lcm = _lcm(left.denominator, right.denominator)
    left_new_num = left.numerator * (lcm // left.denominator)
    right_new_num = right.numerator * (lcm // right.denominator)
    result_num = left_new_num + right_new_num
    result = Fraction(result_num, lcm)
    description = f"Складываем дроби {_format_fraction(left)} и {_format_fraction(right)}. Общий знаменатель: {lcm}."
    formula_repr = f"{_format_fraction(left)} + {_format_fraction(right)}"
    formula_calc = f"{left_new_num}/{lcm} + {right_new_num}/{lcm} = {result_num}/{lcm}"
    if result != Fraction(result_num, lcm):
        formula_calc += f" = {_format_fraction(result)}"
    steps.append({"step_number": step_counter[0], "description": description, "formula_representation": formula_repr, "formula_calculation": formula_calc, "calculation_result": _format_fraction(result)})
    step_counter[0] += 1
    return result

def _perform_subtraction(left: Fraction, right: Fraction, steps: List[Dict], step_counter: List[int]) -> Fraction:
    lcm = _lcm(left.denominator, right.denominator)
    left_new_num = left.numerator * (lcm // left.denominator)
    right_new_num = right.numerator * (lcm // right.denominator)
    result_num = left_new_num - right_new_num
    result = Fraction(result_num, lcm)
    description = f"Вычитаем дроби {_format_fraction(left)} и {_format_fraction(right)}. Общий знаменатель: {lcm}."
    formula_repr = f"{_format_fraction(left)} - {_format_fraction(right)}"
    formula_calc = f"{left_new_num}/{lcm} - {right_new_num}/{lcm} = {result_num}/{lcm}"
    if result != Fraction(result_num, lcm):
        formula_calc += f" = {_format_fraction(result)}"
    steps.append({"step_number": step_counter[0], "description": description, "formula_representation": formula_repr, "formula_calculation": formula_calc, "calculation_result": _format_fraction(result)})
    step_counter[0] += 1
    return result

def _perform_multiplication(left: Fraction, right: Fraction, steps: List[Dict], step_counter: List[int]) -> Fraction:
    result_num = left.numerator * right.numerator
    result_den = left.denominator * right.denominator
    result = Fraction(result_num, result_den)
    description = f"Умножаем дроби {_format_fraction(left)} и {_format_fraction(right)}."
    formula_repr = f"{_format_fraction(left)} * {_format_fraction(right)}"
    formula_calc = f"{result_num}/{result_den}"
    if result != Fraction(result_num, result_den):
        formula_calc += f" = {_format_fraction(result)}"
    steps.append({"step_number": step_counter[0], "description": description, "formula_representation": formula_repr, "formula_calculation": formula_calc, "calculation_result": _format_fraction(result)})
    step_counter[0] += 1
    return result

def _perform_division(left: Fraction, right: Fraction, steps: List[Dict], step_counter: List[int]) -> Fraction:
    inverted_right = Fraction(right.denominator, right.numerator)
    result_num = left.numerator * inverted_right.numerator
    result_den = left.denominator * inverted_right.denominator
    result = Fraction(result_num, result_den)
    description = f"Делим дробь {_format_fraction(left)} на {_format_fraction(right)}. Умножаем на перевернутую дробь {inverted_right}."
    formula_repr = f"{_format_fraction(left)} : {_format_fraction(right)}"
    formula_calc = f"{_format_fraction(left)} * {inverted_right} = {result_num}/{result_den}"
    if result != Fraction(result_num, result_den):
        formula_calc += f" = {_format_fraction(result)}"
    steps.append({"step_number": step_counter[0], "description": description, "formula_representation": formula_repr, "formula_calculation": formula_calc, "calculation_result": _format_fraction(result)})
    step_counter[0] += 1
    return result

def _add_decimal_conversion_step(fraction: Fraction, steps: List[Dict], step_counter: List[int]) -> None:
    decimal_value = float(fraction)
    description = f"Преобразуем итоговый результат {_format_fraction(fraction)} в десятичное число."
    formula_repr = _format_fraction(fraction)
    formula_calc = f"{_format_fraction(fraction)} = {decimal_value}"
    steps.append({"step_number": step_counter[0], "description": description, "formula_representation": formula_repr, "formula_calculation": formula_calc, "calculation_result": str(decimal_value)})
    step_counter[0] += 1

def _format_fraction(frac: Fraction) -> str:
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"

def _lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)

def _generate_explanation_idea() -> str:
    return "Для решения этого выражения сначала выполним возведение в степень, затем умножение и деление, и в конце сложение и вычитание."

def _generate_hints() -> List[str]:
    return [
        "Возведение в степень - операция наивысшего приоритета.",
        "При возведении дроби в степень, в степень возводится и числитель, и знаменатель.",
        "Не забывайте сокращать дроби после вычислений.",
        "Соблюдайте порядок действий: степени, затем умножение и деление, затем сложение и вычитание."
    ]
