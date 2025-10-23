"""
Решатель для задач со степенями (TASK6_POWERS).
Модуль следует стандарту ГОСТ-2026 для формирования пошагового решения.
Поддерживает возведение в степень для обыкновенных и десятичных дробей.
"""

from fractions import Fraction
from typing import Dict, List, Any
import math


def solve(expression_tree: Dict[str, Any]) -> Dict[str, Any]:
    """
    Главная функция решателя для выражений со степенями.

    Args:
        expression_tree: Древовидная структура математического выражения

    Returns:
        Словарь с пошаговым решением по стандарту ГОСТ-2026
    """
    steps = []
    step_counter = [1]  # Используем список для mutable счетчика

    # Рекурсивно вычисляем выражение и собираем шаги
    final_fraction = _evaluate_tree(expression_tree, steps, step_counter)

    # Добавляем финальный шаг с преобразованием в десятичное число
    _add_decimal_conversion_step(final_fraction, steps, step_counter)

    # Формируем итоговый результат
    decimal_value = float(final_fraction)

    result = {
        "question_id": "placeholder_id",
        "question_group": "TASK6_POWERS",
        "explanation_idea": _generate_explanation_idea(),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": decimal_value,
            "value_display": str(decimal_value)
        },
        "hints": _generate_hints()
    }

    return result


def _evaluate_tree(node: Dict[str, Any], steps: List[Dict], step_counter: List[int]) -> Fraction:
    """
    Рекурсивно вычисляет выражение из дерева, добавляя шаги в список.
    Преобразует все числа в Fraction для единообразия.

    Args:
        node: Узел дерева (операция или значение)
        steps: Список для накопления шагов решения
        step_counter: Счетчик шагов (mutable)

    Returns:
        Результат вычисления в виде Fraction
    """
    # Базовый случай: это обыкновенная дробь
    if node.get("type") == "common":
        numerator, denominator = node["value"]
        return Fraction(numerator, denominator)

    # Базовый случай: это десятичная дробь - преобразуем в Fraction
    if node.get("type") == "decimal":
        decimal_value = node["value"]
        fraction = Fraction(str(decimal_value))

        # Добавляем шаг преобразования только если это не целое число
        if decimal_value != int(decimal_value):
            _add_conversion_step(decimal_value, fraction, steps, step_counter)

        return fraction

    # Рекурсивный случай: это операция
    operation = node["operation"]
    operands = node["operands"]

    # Вычисляем операнды рекурсивно
    left = _evaluate_tree(operands[0], steps, step_counter)
    right = _evaluate_tree(operands[1], steps, step_counter)

    # Выполняем операцию и добавляем шаг
    result = _perform_operation(operation, left, right, steps, step_counter)

    return result


def _add_conversion_step(decimal_value: float, fraction: Fraction,
                        steps: List[Dict], step_counter: List[int]) -> None:
    """
    Добавляет шаг преобразования десятичной дроби в обыкновенную.

    Args:
        decimal_value: Исходное десятичное число
        fraction: Результат преобразования в Fraction
        steps: Список шагов
        step_counter: Счетчик шагов
    """
    decimal_str = str(decimal_value)

    # Определяем количество знаков после запятой
    if '.' in decimal_str:
        decimal_places = len(decimal_str.split('.')[1])
        denominator = 10 ** decimal_places
        numerator = int(decimal_value * denominator)

        intermediate_fraction = Fraction(numerator, denominator)

        description = f"Преобразуем десятичную дробь {decimal_value} в обыкновенную."

        formula_repr = str(decimal_value)

        # Если дробь сократилась, показываем промежуточный шаг
        if intermediate_fraction != fraction:
            gcd = math.gcd(numerator, denominator)
            formula_calc = f"{decimal_value} = {numerator}/{denominator} = {_format_fraction(fraction)}"
            if gcd > 1:
                description += f" Сокращаем на {gcd}."
        else:
            formula_calc = f"{decimal_value} = {_format_fraction(fraction)}"
    else:
        # Целое число
        description = f"Преобразуем число {decimal_value} в обыкновенную дробь."
        formula_repr = str(decimal_value)
        formula_calc = f"{decimal_value} = {_format_fraction(fraction)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_fraction(fraction)
    })

    step_counter[0] += 1


def _perform_operation(operation: str, left: Fraction, right: Fraction,
                       steps: List[Dict], step_counter: List[int]) -> Fraction:
    """
    Выполняет математическую операцию и добавляет описание шага.

    Args:
        operation: Тип операции ('add', 'subtract', 'multiply', 'divide', 'power')
        left: Левый операнд
        right: Правый операнд
        steps: Список шагов
        step_counter: Счетчик шагов

    Returns:
        Результат операции
    """
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


def _perform_power(base: Fraction, exponent: Fraction,
                  steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Выполняет возведение в степень."""
    # Проверяем, что степень - целое число
    if exponent.denominator != 1:
        raise ValueError(f"Степень должна быть целым числом, получено: {exponent}")

    exp_value = exponent.numerator

    # Возводим в степень числитель и знаменатель отдельно
    result_num = base.numerator ** exp_value
    result_den = base.denominator ** exp_value
    result = Fraction(result_num, result_den)

    # Формируем описание
    if base.denominator == 1:
        description = f"Возводим число {base.numerator} в степень {exp_value}."
    else:
        description = f"Возводим дробь {_format_fraction(base)} в степень {exp_value}."

    formula_repr = f"({_format_fraction(base)})^{exp_value}"

    # Формируем расчет
    if base.denominator == 1:
        formula_calc = f"{base.numerator}^{exp_value} = {result_num}"
    else:
        formula_calc = f"({_format_fraction(base)})^{exp_value} = {base.numerator}^{exp_value} / {base.denominator}^{exp_value} = {result_num}/{result_den}"

    # Проверяем, нужно ли сокращение
    if result.numerator != result_num or result.denominator != result_den:
        gcd = math.gcd(result_num, result_den)
        if gcd > 1:
            formula_calc += f" = {_format_fraction(result)}"
            description += f" Сокращаем на {gcd}."

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_fraction(result)
    })

    step_counter[0] += 1
    return result


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

    description = f"Складываем дроби. Общий знаменатель: {lcm}."

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

    description = "Преобразуем результат в десятичное число."

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
    """Возвращает статическое объяснение для всех задач со степенями."""
    return "Для решения этого выражения сначала выполним возведение в степень, затем умножение и деление, и в конце сложение и вычитание."


def _generate_hints() -> List[str]:
    """Возвращает статический список подсказок для задач со степенями."""
    return [
        "Возведение в степень - операция наивысшего приоритета.",
        "При возведении дроби в степень, в степень возводится и числитель, и знаменатель.",
        "Не забывайте сокращать дроби после вычислений.",
        "Соблюдайте порядок действий: степени, затем умножение и деление, затем сложение и вычитание."
    ]
