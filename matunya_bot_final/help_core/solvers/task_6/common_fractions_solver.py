# matunya_bot_final/help_core/solvers/task_6/common_fractions_solver.py

"""
Решатель для подтипа 'common_fractions' (Задание 6).
Содержит "внутренний роутер" для разных паттернов.
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
    Главная функция-роутер для подтипа 'common_fractions'.
    Вызывает универсальный рекурсивный решатель.
    """
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    if not expression_tree:
        raise ValueError("Отсутствует 'expression_tree' в task_data")

    # Для 'common_fractions' все паттерны решаются одним и тем же универсальным методом.
    # Поэтому "роутер" здесь очень простой - он всегда вызывает одну и ту же логику.

    steps = []
    step_counter = [1]

    # Вызываем универсальный рекурсивный движок
    final_fraction = _evaluate_tree(expression_tree, steps, step_counter)

    # Добавляем финальный шаг
    _add_decimal_conversion_step(final_fraction, steps, step_counter)

    decimal_value = float(final_fraction)

    # Собираем финальный solution_core по ГОСТ-2026
    return {
        "question_id": task_data.get("id", "placeholder_id"),
        "question_group": "TASK6_COMMON",
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
# (Этот код остается практически без изменений, он идеален)
# =============================================================================

def _evaluate_tree(node: Dict[str, Any], steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Рекурсивно вычисляет выражение из дерева, добавляя шаги в список."""
    if node.get("type") == "common":
        numerator, denominator = node["value"]
        return Fraction(numerator, denominator)

    operation = node["operation"]
    operands = node["operands"]

    left = _evaluate_tree(operands[0], steps, step_counter)
    right = _evaluate_tree(operands[1], steps, step_counter)

    return _perform_operation(operation, left, right, steps, step_counter)


def _perform_operation(operation: str, left: Fraction, right: Fraction,
                       steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Выполняет математическую операцию и добавляет описание шага."""
    if operation == "add":
        return _perform_addition(left, right, steps, step_counter)
    elif operation == "subtract":
        return _perform_subtraction(left, right, steps, step_counter)
    elif operation == "multiply":
        return _perform_multiplication(left, right, steps, step_counter)
    elif operation == "divide":
        return _perform_division(left, right, steps, step_counter)
    else:
        raise ValueError(f"Неизвестная операция: {operation}")


def _perform_addition(left: Fraction, right: Fraction,
                     steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Выполняет сложение дробей."""
    lcm = _lcm(left.denominator, right.denominator)

    # Приводим к общему знаменателю
    left_mult = lcm // left.denominator
    right_mult = lcm // right.denominator

    left_new_num = left.numerator * left_mult
    right_new_num = right.numerator * right_mult

    result_num = left_new_num + right_new_num
    result = Fraction(result_num, lcm)

    # Формируем описание шага
    description = f"Складываем дроби. Общий знаменатель: {lcm}."

    # Добавляем информацию о сокращении если нужно
    if result.numerator != result_num or result.denominator != lcm:
        gcd = math.gcd(result_num, lcm)
        if gcd > 1:
            description += f" Сокращаем на {gcd}."

    formula_repr = f"{_format_fraction(left)} + {_format_fraction(right)}"

    if lcm != left.denominator or lcm != right.denominator:
        formula_calc = f"{left_new_num}/{lcm} + {right_new_num}/{lcm} = {result_num}/{lcm}"
        if result.numerator != result_num or result.denominator != lcm:
            formula_calc += f" = {_format_fraction(result)}"
    else:
        formula_calc = f"{result_num}/{lcm}"
        if result.numerator != result_num or result.denominator != lcm:
            formula_calc += f" = {_format_fraction(result)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_fraction(result)
    })

    step_counter[0] += 1
    return result


def _perform_subtraction(left: Fraction, right: Fraction,
                        steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Выполняет вычитание дробей."""
    lcm = _lcm(left.denominator, right.denominator)

    left_mult = lcm // left.denominator
    right_mult = lcm // right.denominator

    left_new_num = left.numerator * left_mult
    right_new_num = right.numerator * right_mult

    result_num = left_new_num - right_new_num
    result = Fraction(result_num, lcm)

    description = f"Вычитаем дроби. Общий знаменатель: {lcm}."

    if result.numerator != result_num or result.denominator != lcm:
        gcd = math.gcd(abs(result_num), lcm)
        if gcd > 1:
            description += f" Сокращаем на {gcd}."

    formula_repr = f"{_format_fraction(left)} - {_format_fraction(right)}"

    if lcm != left.denominator or lcm != right.denominator:
        formula_calc = f"{left_new_num}/{lcm} - {right_new_num}/{lcm} = {result_num}/{lcm}"
        if result.numerator != result_num or result.denominator != lcm:
            formula_calc += f" = {_format_fraction(result)}"
    else:
        formula_calc = f"{result_num}/{lcm}"
        if result.numerator != result_num or result.denominator != lcm:
            formula_calc += f" = {_format_fraction(result)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_fraction(result)
    })

    step_counter[0] += 1
    return result


def _perform_multiplication(left: Fraction, right: Fraction,
                           steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Выполняет умножение дробей."""
    result_num = left.numerator * right.numerator
    result_den = left.denominator * right.denominator
    result = Fraction(result_num, result_den)

    description = "Умножаем дроби. Перемножаем числители и знаменатели."

    # Проверяем, нужно ли сокращение
    if result.numerator != result_num or result.denominator != result_den:
        gcd = math.gcd(result_num, result_den)
        if gcd > 1:
            description += f" Сокращаем на {gcd}."

    formula_repr = f"{_format_fraction(left)} * {_format_fraction(right)}"
    formula_calc = f"{result_num}/{result_den}"

    if result.numerator != result_num or result.denominator != result_den:
        formula_calc += f" = {_format_fraction(result)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_fraction(result)
    })

    step_counter[0] += 1
    return result


def _perform_division(left: Fraction, right: Fraction,
                     steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Выполняет деление дробей."""
    # Деление = умножение на перевернутую дробь
    result_num = left.numerator * right.denominator
    result_den = left.denominator * right.numerator
    result = Fraction(result_num, result_den)

    description = f"Делим дроби. Умножаем на перевернутую дробь {right.denominator}/{right.numerator}."

    if result.numerator != result_num or result.denominator != result_den:
        gcd = math.gcd(abs(result_num), abs(result_den))
        if gcd > 1:
            description += f" Сокращаем на {gcd}."

    formula_repr = f"{_format_fraction(left)} : {_format_fraction(right)}"
    formula_calc = f"{_format_fraction(left)} * {right.denominator}/{right.numerator} = {result_num}/{result_den}"

    if result.numerator != result_num or result.denominator != result_den:
        formula_calc += f" = {_format_fraction(result)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_fraction(result)
    })

    step_counter[0] += 1
    return result


def _add_decimal_conversion_step(fraction: Fraction, steps: List[Dict],
                                 step_counter: List[int]) -> None:
    """Добавляет финальный шаг с преобразованием в десятичное число."""
    decimal_value = float(fraction)

    description = "Преобразуем дробь в десятичное число."

    formula_repr = _format_fraction(fraction)
    formula_calc = f"{_format_fraction(fraction)} = {decimal_value}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": str(decimal_value)
    })


def _format_fraction(frac: Fraction) -> str:
    """Форматирует дробь для отображения."""
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def _lcm(a: int, b: int) -> int:
    """Вычисляет наименьшее общее кратное."""
    return abs(a * b) // math.gcd(a, b)


def _generate_explanation_idea() -> str:
    """Возвращает статическое объяснение для всех задач с обыкновенными дробями."""
    return "Для решения этого выражения необходимо последовательно выполнить все действия с дробями, соблюдая порядок операций."


def _generate_hints() -> List[str]:
    """Возвращает статический список подсказок для обыкновенных дробей."""
    return [
        "При сложении и вычитании дробей приводите их к общему знаменателю.",
        "При умножении дробей перемножайте числители и знаменатели отдельно.",
        "При делении на дробь умножайте на перевернутую дробь.",
        "Всегда сокращайте результат, если это возможно."
    ]
