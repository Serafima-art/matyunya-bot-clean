# matunya_bot_final/help_core/solvers/task_6/decimal_fractions_solver.py

"""
Решатель для подтипа 'decimal_fractions' (Задание 6).
Содержит "внутренний роутер" для разных паттернов.
Модуль следует стандарту ГОСТ-2026.
"""

from decimal import Decimal, getcontext
from typing import Dict, List, Any

# =============================================================================
# ★★★ ГЛАВНАЯ ФУНКЦИЯ-ДИСПЕТЧЕР (ВНУТРЕННИЙ РОУТЕР) ★★★
# =============================================================================

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Главная функция-роутер для подтипа 'decimal_fractions'.
    Вызывает универсальный рекурсивный решатель.
    """
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    if not expression_tree:
        raise ValueError("Отсутствует 'expression_tree' в task_data")

    # Для 'decimal_fractions' все паттерны также решаются одним универсальным методом.

    getcontext().prec = 10 # Устанавливаем точность вычислений
    steps = []
    step_counter = [1]

    # Вызываем универсальный рекурсивный движок
    final_result = _evaluate_tree(expression_tree, steps, step_counter)

    result_value = float(final_result)

    # Собираем финальный solution_core по ГОСТ-2026
    return {
        "question_id": task_data.get("id", "placeholder_id"),
        "question_group": "TASK6_DECIMAL",
        "explanation_idea": _generate_explanation_idea(),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": result_value,
            "value_display": _format_decimal(final_result) # Используем наш форматтер для красоты
        },
        "hints": _generate_hints()
    }

# =============================================================================
# ★★★ УНИВЕРСАЛЬНЫЙ РЕКУРСИВНЫЙ ДВИЖОК (ВСЯ МАТЕМАТИКА) ★★★
# (Этот код остается практически без изменений)
# =============================================================================

def _evaluate_tree(node: Dict[str, Any], steps: List[Dict], step_counter: List[int]) -> Decimal:
    """Рекурсивно вычисляет выражение из дерева, добавляя шаги в список."""
    if node.get("type") == "decimal":
        return Decimal(str(node["value"]))

    operation = node["operation"]
    operands = node["operands"]

    left = _evaluate_tree(operands[0], steps, step_counter)
    right = _evaluate_tree(operands[1], steps, step_counter)

    return _perform_operation(operation, left, right, steps, step_counter)


def _perform_operation(operation: str, left: Decimal, right: Decimal,
                       steps: List[Dict], step_counter: List[int]) -> Decimal:
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

def _perform_addition(left: Decimal, right: Decimal,
                     steps: List[Dict], step_counter: List[int]) -> Decimal:
    """Выполняет сложение десятичных дробей."""
    result = left + right

    # Формируем описание с учетом знаков
    description = _generate_addition_description(left, right)

    formula_repr = f"{_format_decimal(left)} + {_format_decimal(right)}"
    formula_calc = f"{_format_decimal(left)} + {_format_decimal(right)} = {_format_decimal(result)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_decimal(result)
    })

    step_counter[0] += 1
    return result


def _perform_subtraction(left: Decimal, right: Decimal,
                        steps: List[Dict], step_counter: List[int]) -> Decimal:
    """Выполняет вычитание десятичных дробей."""
    result = left - right

    description = _generate_subtraction_description(left, right)

    formula_repr = f"{_format_decimal(left)} - {_format_decimal(right)}"
    formula_calc = f"{_format_decimal(left)} - {_format_decimal(right)} = {_format_decimal(result)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_decimal(result)
    })

    step_counter[0] += 1
    return result


def _perform_multiplication(left: Decimal, right: Decimal,
                           steps: List[Dict], step_counter: List[int]) -> Decimal:
    """Выполняет умножение десятичных дробей."""
    result = left * right

    description = _generate_multiplication_description(left, right)

    formula_repr = f"{_format_decimal(left)} * {_format_decimal(right)}"
    formula_calc = f"{_format_decimal(left)} * {_format_decimal(right)} = {_format_decimal(result)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_decimal(result)
    })

    step_counter[0] += 1
    return result


def _perform_division(left: Decimal, right: Decimal,
                     steps: List[Dict], step_counter: List[int]) -> Decimal:
    """Выполняет деление десятичных дробей."""
    result = left / right

    description = _generate_division_description(left, right)

    formula_repr = f"{_format_decimal(left)} : {_format_decimal(right)}"
    formula_calc = f"{_format_decimal(left)} : {_format_decimal(right)} = {_format_decimal(result)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": _format_decimal(result)
    })

    step_counter[0] += 1
    return result


def _generate_addition_description(left: Decimal, right: Decimal) -> str:
    """Генерирует описание для сложения с учетом знаков."""
    if left >= 0 and right >= 0:
        return f"Складываем числа {_format_decimal(left)} и {_format_decimal(right)}."
    elif left < 0 and right < 0:
        return f"Складываем отрицательные числа {_format_decimal(left)} и {_format_decimal(right)}."
    else:
        return f"Складываем числа {_format_decimal(left)} и {_format_decimal(right)}."


def _generate_subtraction_description(left: Decimal, right: Decimal) -> str:
    """Генерирует описание для вычитания с учетом знаков."""
    if right < 0:
        return f"Вычитаем отрицательное число {_format_decimal(right)} из {_format_decimal(left)}. Вычитание минуса равносильно сложению."
    else:
        return f"Вычитаем число {_format_decimal(right)} из {_format_decimal(left)}."


def _generate_multiplication_description(left: Decimal, right: Decimal) -> str:
    """Генерирует описание для умножения с учетом знаков."""
    if left < 0 and right < 0:
        return f"Умножаем числа {_format_decimal(left)} и {_format_decimal(right)}. Минус на минус дает плюс."
    elif (left < 0 and right > 0) or (left > 0 and right < 0):
        return f"Умножаем числа {_format_decimal(left)} и {_format_decimal(right)}. Плюс на минус дает минус."
    else:
        return f"Умножаем числа {_format_decimal(left)} и {_format_decimal(right)}."


def _generate_division_description(left: Decimal, right: Decimal) -> str:
    """Генерирует описание для деления с учетом знаков."""
    if left < 0 and right < 0:
        return f"Делим числа {_format_decimal(left)} на {_format_decimal(right)}. Минус на минус дает плюс."
    elif (left < 0 and right > 0) or (left > 0 and right < 0):
        return f"Делим числа {_format_decimal(left)} на {_format_decimal(right)}. Плюс на минус дает минус."
    else:
        return f"Делим число {_format_decimal(left)} на {_format_decimal(right)}."


def _format_decimal(value: Decimal) -> str:
    """Форматирует Decimal для отображения."""
    # Убираем лишние нули и экспоненциальную запись
    result = str(value)

    # Удаляем trailing zeros после точки
    if '.' in result:
        result = result.rstrip('0').rstrip('.')

    return result


def _generate_explanation_idea() -> str:
    """Возвращает статическое объяснение для всех задач с десятичными дробями."""
    return "Для решения этого выражения необходимо последовательно выполнить все действия с десятичными дробями, соблюдая порядок операций."


def _generate_hints() -> List[str]:
    """Возвращает статический список подсказок для десятичных дробей."""
    return [
        "При умножении или делении двух отрицательных чисел результат будет положительным.",
        "Соблюдайте порядок действий: сначала умножение и деление, затем сложение и вычитание.",
        "Внимательно следите за знаками при вычислениях.",
        "При вычитании отрицательного числа результат увеличивается."
    ]
