"""Пошаговый решатель для подтипа common_fractions (Задание 6).

АРХИТЕКТУРНЫЙ ПРИНЦИП:
Решатель генерирует ТОЛЬКО структурированные данные (solution_core).
Вся текстовая логика вынесена в humanizer через систему ключей-шаблонов.

Решение формируется по педагогическим рекомендациям ФИПИ:
- отдельные ветки для каждого паттерна;
- подробные пояснения на каждом шаге (через ключи);
- соблюдение порядка действий и явное отображение всех преобразований.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple
import math

# ---------------------------------------------------------------------------
# Константы для идей и подсказок
# ---------------------------------------------------------------------------

IDEA_KEY_MAP: Dict[str, Tuple[str, Dict[str, Any]]] = {
    "cf_addition_subtraction": ("ADD_SUB_FRACTIONS_IDEA", {}),
    "multiplication_division": ("MULTIPLY_DIVIDE_FRACTIONS_IDEA", {}),
    "parentheses_operations": ("PARENTHESES_OPERATIONS_IDEA", {}),
    "complex_fraction": ("COMPLEX_FRACTION_IDEA", {}),
}

HINTS_KEY_MAP: Dict[str, List[str]] = {
    "cf_addition_subtraction": [
        "HINT_ORDER_OF_OPERATIONS",
        "HINT_FIND_LCM",
        "HINT_CHECK_REDUCTION",
    ],
    "multiplication_division": [
        "HINT_CONVERT_MIXED",
        "HINT_DIVIDE_AS_MULTIPLY",
        "HINT_CROSS_CANCEL",
    ],
    "parentheses_operations": [
        "HINT_ORDER_OF_OPERATIONS",
        "HINT_FIND_LCM",
        "HINT_MULTIPLY_AFTER_PARENTHESES",
    ],
    "complex_fraction": [
        "HINT_PROCESS_NUMERATOR",
        "HINT_DIVIDE_AS_MULTIPLY",
        "HINT_CROSS_CANCEL",
    ],
}

# ---------------------------------------------------------------------------
# Вспомогательные структуры
# ---------------------------------------------------------------------------


@dataclass
class StepBuilder:
    """Построитель шагов решения с поддержкой системы ключей-шаблонов."""

    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1

    def add(
        self,
        description_key: str,
        description_params: Optional[Dict[str, Any]] = None,
        formula_representation: Optional[str] = None,
        formula_general: Optional[str] = None,
        formula_calculation: Optional[str] = None,
        calculation_result: Optional[str] = None,
    ) -> None:
        """Добавляет шаг в соответствии с ГОСТ-2025.

        Args:
            description_key: Ключ для шаблона текста
            description_params: Параметры для подстановки в шаблон
            formula_representation: Визуальное состояние выражения
            formula_general: Общая формула (теория)
            formula_calculation: Формула с числами (практика)
            calculation_result: Результат вычисления
        """
        step = {
            "step_number": self.counter,
            "description_key": description_key,
            "description_params": description_params or {},
        }

        if formula_representation is not None:
            step["formula_representation"] = formula_representation
        if formula_general is not None:
            step["formula_general"] = formula_general
        if formula_calculation is not None:
            step["formula_calculation"] = formula_calculation
        if calculation_result is not None:
            step["calculation_result"] = calculation_result

        self.steps.append(step)
        self.counter += 1


# ---------------------------------------------------------------------------
# Публичный интерфейс
# ---------------------------------------------------------------------------

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Главная функция решателя. Возвращает solution_core по ГОСТ-2025.

    Args:
        task_data: Данные задачи из tasks_6.json

    Returns:
        Словарь solution_core, полностью соответствующий ГОСТ-2025
    """
    pattern = task_data.get("pattern")
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    if not pattern or not expression_tree:
        raise ValueError("Некорректные данные задачи: отсутствует pattern или expression_tree.")

    builder = StepBuilder()
    expression_preview = _render_expression(expression_tree)

    # Шаг 0: Предварительный обзор выражения
    builder.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": expression_preview},
        formula_representation=expression_preview,
    )

    # Выбор стратегии решения в зависимости от паттерна
    idea_key, idea_params = IDEA_KEY_MAP.get(pattern, ("GENERIC_IDEA", {}))
    hints_keys = HINTS_KEY_MAP.get(pattern, [])

    if pattern == "cf_addition_subtraction":
        result_fraction = _solve_addition_subtraction(expression_tree, builder)
    elif pattern == "multiplication_division":
        result_fraction = _solve_multiplication_division(expression_tree, builder)
    elif pattern == "parentheses_operations":
        result_fraction = _solve_parentheses_operations(expression_tree, builder)
    elif pattern == "complex_fraction":
        result_fraction = _solve_complex_fraction(expression_tree, builder)
    else:
        raise ValueError(f"Неизвестный паттерн: {pattern}")

    # Финальный шаг (преобразование к требуемому формату ответа)
    requested_part = _detect_requested_part(task_data)
    _add_final_step(task_data, builder, result_fraction, requested_part, pattern)

    # Формирование финального ответа
    answer_type = task_data.get("answer_type", "decimal")
    if answer_type == "decimal":
        display_value = str(float(result_fraction))
    else:  # integer
        if requested_part == "denominator":
            display_value = str(result_fraction.denominator)
        else:
            display_value = str(result_fraction.numerator)

    return {
        "question_id": task_data.get("id", "task_6_common"),
        "question_group": "TASK6_COMMON",
        "explanation_idea": "",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": idea_params,
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": float(result_fraction),
            "value_display": display_value,
            "requested_part": requested_part,
            "final_answer_part": requested_part or "value",
        },
        "hints": [],
        "hints_keys": hints_keys,
    }


# ---------------------------------------------------------------------------
# Решатели для отдельных паттернов
# ---------------------------------------------------------------------------

def _solve_addition_subtraction(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
    """Решает задачи типа: a/b + c/d или a/b - c/d"""
    left_node, right_node = node["operands"]
    operation = node["operation"]

    left_frac = _extract_fraction(left_node)
    right_frac = _extract_fraction(right_node)

    return _explain_fraction_combination(
        left_frac,
        right_frac,
        builder,
        operation,
        context=None,
    )


def _solve_multiplication_division(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
    """Пошаговое решение для умножения или деления дробей."""

    left_node, right_node = node["operands"]
    operation = node["operation"]

    left_frac, left_conversion = _convert_possible_mixed(left_node)
    right_frac, right_conversion = _convert_possible_mixed(right_node)

    conversions: List[Dict[str, Any]] = []
    if left_conversion:
        conversions.append(left_conversion)
    if right_conversion:
        conversions.append(right_conversion)

    for idx, info in enumerate(conversions):
        key = "CONVERT_MIXED_FIRST" if idx == 0 else "CONVERT_MIXED_NEXT"
        builder.add(
            description_key=key,
            description_params={
                "mixed_text": info["mixed_text"],
                "whole": info["whole"],
                "num": info["num"],
                "den": info["den"],
                "result_num": info["result_num"],
                "result_den": info["result_den"],
            },
            formula_general="(a b/c) = (a·c + b) / c",
            formula_calculation=(
                f"{info['mixed_text']} = ({info['whole']}·{info['den']} + {info['num']})/{info['den']} "
                f"= {info['result_num']}/{info['result_den']}"
            ),
            calculation_result=f"{info['result_num']}/{info['result_den']}",
        )

    if conversions:
        op_symbol = "·" if operation == "multiply" else ":"
        converted_expression = f"{_format_fraction(left_frac)} {op_symbol} {_format_fraction(right_frac)}"
        builder.add(
            description_key="SHOW_CONVERTED_EXPRESSION",
            description_params={"expression": converted_expression},
            formula_representation=converted_expression,
            calculation_result=converted_expression,
        )

    if operation == "divide":
        result = _divide_fractions(
            builder,
            left_frac,
            right_frac,
            setup_context="Преобразуем деление в умножение: переворачиваем вторую дробь.",
            combined_context="Перемножаем дроби и выполняем возможные сокращения.",
            final_context="Получаем результат деления двух дробей.",
        )
    else:
        result = _explain_multiplication(
            builder,
            left_frac,
            right_frac,
            context="Выполняем умножение дробей.",
        )

    return result



def _solve_parentheses_operations(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
    """Решает задачи типа: (a/b ± c/d) * e/f или (a/b ± c/d) / e/f"""
    left_node, right_node = node["operands"]
    outer_operation = node["operation"]

    # Вычисляем выражение в скобках
    if left_node.get("operation") in {"add", "subtract"}:
        inner_result = _explain_fraction_combination(
            _extract_fraction(left_node["operands"][0]),
            _extract_fraction(left_node["operands"][1]),
            builder,
            left_node["operation"],
            context="В скобках",
        )
    else:
        inner_result = _extract_fraction(left_node)

    other_operand = _extract_fraction(right_node)

    # Выполняем внешнюю операцию
    if outer_operation == "multiply":
        result = _explain_multiplication(
            builder,
            inner_result,
            other_operand,
            context="После вычисления выражения в скобках умножаем полученную дробь на второй множитель"
        )
    else:  # divide
        result = _divide_fractions(
            builder,
            inner_result,
            other_operand,
            setup_context="Делим результат выражения в скобках: переворачиваем вторую дробь.",
            combined_context="Перемножаем дроби и сокращаем общие множители.",
            final_context="Получаем значение после деления на вторую дробь.",
        )

    return result


def _solve_complex_fraction(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
    """Решает сложную дробь с упрощённой логикой."""

    numerator_node, denominator_node = node["operands"]

    if numerator_node.get("operation") in {"add", "subtract"}:
        numerator = _explain_fraction_combination(
            _extract_fraction(numerator_node["operands"][0]),
            _extract_fraction(numerator_node["operands"][1]),
            builder,
            numerator_node["operation"],
            context="В числителе",
        )
    else:
        numerator = _extract_fraction(numerator_node)

    builder.add(
        description_key="COMPLEX_NUMERATOR_RESULT",
        description_params={"context": "В числителе", "value": _format_fraction(numerator)},
        formula_representation=_format_fraction(numerator),
        calculation_result=_format_fraction(numerator),
    )

    denominator = _extract_fraction(denominator_node)

    builder.add(
        description_key="COMPLEX_DIVISION_SETUP",
        description_params={
            "numerator": _format_fraction(numerator),
            "denominator": _format_fraction(denominator),
        },
    )

    result = _divide_fractions(
        builder,
        numerator,
        denominator,
        setup_context="Разделим найденный числитель на знаменатель: заменяем деление умножением.",
        combined_context="Перемножаем полученные дроби и выполняем сокращение, если это возможно.",
        final_context="Фиксируем итоговое значение сложной дроби.",
    )

    return result



# ---------------------------------------------------------------------------
# Объяснение базовых операций
# ---------------------------------------------------------------------------

def _explain_fraction_combination(
    left: Fraction,
    right: Fraction,
    builder: StepBuilder,
    operation: str,
    context: Optional[str],
) -> Fraction:
    """Выполняет сложение или вычитание дробей с полным объяснением.

    Args:
        left: Левая дробь
        right: Правая дробь
        builder: Построитель шагов
        operation: "add" или "subtract"
        context: Контекст операции (например, "В скобках")
    """
    op_symbol = "+" if operation == "add" else "−"

    # Шаг 1: Находим НОК
    lcm_value = _lcm(left.denominator, right.denominator)
    builder.add(
        description_key="FIND_LCM",
        description_params={
            "den1": left.denominator,
            "den2": right.denominator,
            "lcm": lcm_value,
            "operation": operation,
            "context": context,
        },
        formula_representation=f"{_format_fraction(left)} {op_symbol} {_format_fraction(right)}",
        formula_general=f"НОК(a, b)",
        formula_calculation=f"НОК({left.denominator}, {right.denominator}) = {lcm_value}",
        calculation_result=str(lcm_value),
    )

    # Шаг 2: Приводим к общему знаменателю
    left_multiplier = lcm_value // left.denominator
    right_multiplier = lcm_value // right.denominator
    left_scaled_num = left.numerator * left_multiplier
    right_scaled_num = right.numerator * right_multiplier

    builder.add(
        description_key="SCALE_TO_COMMON_DENOM",
        description_params={
            "left_num": left.numerator,
            "left_den": left.denominator,
            "left_mult": left_multiplier,
            "right_num": right.numerator,
            "right_den": right.denominator,
            "right_mult": right_multiplier,
            "lcm": lcm_value,
            "left_scaled_num": left_scaled_num,
            "right_scaled_num": right_scaled_num,
            "context": context,
        },
        formula_representation=f"{_format_fraction(left)} {op_symbol} {_format_fraction(right)}",
        formula_calculation=(
            f"{left.numerator}·{left_multiplier}/{left.denominator}·{left_multiplier} = {left_scaled_num}/{lcm_value}, "
            f"{right.numerator}·{right_multiplier}/{right.denominator}·{right_multiplier} = {right_scaled_num}/{lcm_value}"
        ),
        calculation_result=f"{left_scaled_num}/{lcm_value} {op_symbol} {right_scaled_num}/{lcm_value}",
    )

    # Шаг 3: Складываем/вычитаем числители
    raw_numerator = left_scaled_num + (right_scaled_num if operation == "add" else -right_scaled_num)

    builder.add(
        description_key="ADD_NUMERATORS" if operation == "add" else "SUBTRACT_NUMERATORS",
        description_params={
            "left_num": left_scaled_num,
            "right_num": right_scaled_num,
            "result_num": raw_numerator,
            "common_den": lcm_value,
            "context": context,
        },
        formula_representation=f"{left_scaled_num}/{lcm_value} {op_symbol} {right_scaled_num}/{lcm_value}",
        formula_calculation=f"{left_scaled_num} {op_symbol} {right_scaled_num} = {raw_numerator}",
        calculation_result=f"{raw_numerator}/{lcm_value}",
    )

    # Шаг 4: Сокращаем результат
    result_fraction = Fraction(raw_numerator, lcm_value)
    gcd_value = math.gcd(abs(result_fraction.numerator), result_fraction.denominator)

    if gcd_value > 1:
        builder.add(
            description_key="REDUCE_FRACTION",
            description_params={
                "num": raw_numerator,
                "den": lcm_value,
                "gcd": gcd_value,
                "result_num": result_fraction.numerator,
                "result_den": result_fraction.denominator,
                "context": context,
            },
            formula_representation=f"{raw_numerator}/{lcm_value}",
            formula_calculation=f"{raw_numerator}:{gcd_value} = {result_fraction.numerator}, {lcm_value}:{gcd_value} = {result_fraction.denominator}",
            calculation_result=_format_fraction(result_fraction),
        )
    else:
        builder.add(
            description_key="FRACTION_ALREADY_REDUCED",
            description_params={
                "num": raw_numerator,
                "den": lcm_value,
                "context": context,
            },
            formula_representation=f"{raw_numerator}/{lcm_value}",
            calculation_result=_format_fraction(result_fraction),
        )

    return result_fraction


def _explain_multiplication(
    builder: StepBuilder,
    left: Fraction,
    right: Fraction,
    context: Optional[str] = None,
) -> Fraction:
    """Выполняет умножение дробей с перекрестным сокращением."""

    # Шаг 1: Представляем произведение
    builder.add(
        description_key="MULTIPLY_FRACTIONS_SETUP",
        description_params={
            "left_num": left.numerator,
            "left_den": left.denominator,
            "right_num": right.numerator,
            "right_den": right.denominator,
            "context": context,
        },
        formula_representation=f"{_format_fraction(left)} · {_format_fraction(right)}",
        formula_general="(a/b) · (c/d) = (a·c)/(b·d)",
        formula_calculation=f"({left.numerator}·{right.numerator})/({left.denominator}·{right.denominator})",
        calculation_result=f"({left.numerator}·{right.numerator})/({left.denominator}·{right.denominator})",
    )

    # Шаг 2: Перекрестное сокращение
    num_factors = [left.numerator, right.numerator]
    den_factors = [left.denominator, right.denominator]
    cancellations: List[Dict[str, int]] = []

    for i in range(len(num_factors)):
        for j in range(len(den_factors)):
            g = math.gcd(num_factors[i], den_factors[j])
            if g > 1:
                original_num = num_factors[i]
                original_den = den_factors[j]
                num_factors[i] //= g
                den_factors[j] //= g
                cancellations.append({
                    "num": original_num,
                    "den": original_den,
                    "gcd": g,
                    "num_result": num_factors[i],
                    "den_result": den_factors[j],
                })

    if cancellations:
        builder.add(
            description_key="CROSS_CANCEL",
            description_params={
                "cancellations": cancellations,
                "num1": num_factors[0],
                "num2": num_factors[1],
                "den1": den_factors[0],
                "den2": den_factors[1],
                "context": context,
            },
            formula_representation=f"{_format_fraction(left)} · {_format_fraction(right)}",
            formula_calculation=f"({left.numerator}·{right.numerator})/({left.denominator}·{right.denominator}) = ({num_factors[0]}·{num_factors[1]})/({den_factors[0]}·{den_factors[1]})",
            calculation_result=f"({num_factors[0]}·{num_factors[1]})/({den_factors[0]}·{den_factors[1]})",
        )
    else:
        builder.add(
            description_key="NO_CROSS_CANCEL",
            description_params={
                "num1": num_factors[0],
                "num2": num_factors[1],
                "den1": den_factors[0],
                "den2": den_factors[1],
                "context": context,
            },
            formula_representation=f"{_format_fraction(left)} · {_format_fraction(right)}",
        )

    # Шаг 3: Финальное умножение
    raw_num = num_factors[0] * num_factors[1]
    raw_den = den_factors[0] * den_factors[1]
    result = Fraction(raw_num, raw_den)

    builder.add(
        description_key="FINAL_MULTIPLICATION",
        description_params={
            "num1": num_factors[0],
            "num2": num_factors[1],
            "den1": den_factors[0],
            "den2": den_factors[1],
            "result_num": raw_num,
            "result_den": raw_den,
            "context": context,
        },
        formula_calculation=f"({num_factors[0]}·{num_factors[1]})/({den_factors[0]}·{den_factors[1]}) = {raw_num}/{raw_den}",
        calculation_result=_format_fraction(result),
    )

    return result


def _divide_fractions(
    builder: StepBuilder,
    left: Fraction,
    right: Fraction,
    setup_context: str,
    combined_context: str,
    final_context: str,
) -> Fraction:

    if left == right and left != 0:
        builder.add(
            description_key="DIVIDE_SAME_VALUE",
            description_params={},
            formula_calculation=f"{_format_fraction(left)} : {_format_fraction(right)} = 1",
            calculation_result="1",
        )
        return Fraction(1, 1)

    flipped = Fraction(right.denominator, right.numerator)
    builder.add(
        description_key="DIVISION_TO_MULTIPLICATION",
        description_params={
            "left_num": left.numerator,
            "left_den": left.denominator,
            "right_num": right.numerator,
            "right_den": right.denominator,
            "flipped_num": flipped.numerator,
            "flipped_den": flipped.denominator,
            "context": setup_context,
        },
        formula_representation=f"{_format_fraction(left)} : {_format_fraction(right)}",
    )

    num_factors = [left.numerator, flipped.numerator]
    den_factors = [left.denominator, flipped.denominator]
    cancellations: List[Dict[str, int]] = []
    for i in range(len(num_factors)):
        for j in range(len(den_factors)):
            g = math.gcd(num_factors[i], den_factors[j])
            if g > 1:
                original_num = num_factors[i]
                original_den = den_factors[j]
                num_factors[i] //= g
                den_factors[j] //= g
                cancellations.append({
                    "num": original_num,
                    "den": original_den,
                    "gcd": g,
                    "num_result": num_factors[i],
                    "den_result": den_factors[j],
                })

    simplified_expr = f"({num_factors[0]}·{num_factors[1]})/({den_factors[0]}·{den_factors[1]})"
    description_key = "DIVISION_COMBINED_CANCEL" if cancellations else "DIVISION_COMBINED_NO_CANCEL"
    description_params: Dict[str, Any] = {"context": combined_context}
    if cancellations:
        description_params["cancellations"] = cancellations

    builder.add(
        description_key=description_key,
        description_params=description_params,
        formula_general="(a/b) · (c/d) = (a·c)/(b·d)",
        formula_calculation=f"({left.numerator}·{flipped.numerator})/({left.denominator}·{flipped.denominator}) = {simplified_expr}",
        calculation_result=simplified_expr,
    )

    raw_num = num_factors[0] * num_factors[1]
    raw_den = den_factors[0] * den_factors[1]
    result = Fraction(raw_num, raw_den)

    builder.add(
        description_key="DIVISION_FINAL_RESULT",
        description_params={"context": final_context},
        formula_calculation=f"{simplified_expr} = {raw_num}/{raw_den}",
        calculation_result=_format_fraction(result),
    )

    return result


def _add_final_step(
    task_data: Dict[str, Any],
    builder: StepBuilder,
    fraction: Fraction,
    requested_part: Optional[str],
    pattern: Optional[str],
) -> None:
    """Добавляет финальный шаг преобразования к требуемому формату ответа."""

    answer_type = task_data.get("answer_type", "decimal")

    if pattern == "multiplication_division" and answer_type == "integer" and not requested_part:
        return

    if answer_type == "integer":
        if requested_part == "denominator":
            builder.add(
                description_key="EXTRACT_DENOMINATOR",
                description_params={
                    "num": fraction.numerator,
                    "den": fraction.denominator,
                },
                formula_representation=_format_fraction(fraction),
                calculation_result=str(fraction.denominator),
            )
        else:
            builder.add(
                description_key="EXTRACT_NUMERATOR",
                description_params={
                    "num": fraction.numerator,
                    "den": fraction.denominator,
                },
                formula_representation=_format_fraction(fraction),
                calculation_result=str(fraction.numerator),
            )
    else:  # decimal
        decimal_value = float(fraction)
        builder.add(
            description_key="CONVERT_TO_DECIMAL",
            description_params={
                "num": fraction.numerator,
                "den": fraction.denominator,
                "decimal": decimal_value,
            },
            formula_representation=_format_fraction(fraction),
            formula_calculation=f"{_format_fraction(fraction)} = {decimal_value}",
            calculation_result=str(decimal_value),
        )


def _extract_fraction(node: Dict[str, Any]) -> Fraction:
    """Извлекает Fraction из узла expression_tree."""

    node_type = node.get("type")
    if node_type == "common":
        numerator, denominator = node["value"]
        return Fraction(numerator, denominator)
    if node_type == "integer":
        value = node.get("value") or node.get("text")
        if isinstance(value, str):
            value = int(value)
        return Fraction(int(value), 1)
    if "operation" in node:
        # Рекурсивное вычисление для вложенных операций
        operation = node["operation"]
        operands = node.get("operands", [])
        if operation == "add":
            return _extract_fraction(operands[0]) + _extract_fraction(operands[1])
        if operation == "subtract":
            return _extract_fraction(operands[0]) - _extract_fraction(operands[1])
        if operation == "multiply":
            return _extract_fraction(operands[0]) * _extract_fraction(operands[1])
        if operation == "divide":
            return _extract_fraction(operands[0]) / _extract_fraction(operands[1])

    raise ValueError(f"Не удалось преобразовать узел в Fraction: {node}")


def _convert_possible_mixed(node: Dict[str, Any]) -> Tuple[Fraction, Optional[Dict[str, Any]]]:
    """Преобразует смешанное число в неправильную дробь (если требуется)."""

    fraction = _extract_fraction(node)
    conversion_info: Optional[Dict[str, Any]] = None
    text = node.get("text", "")
    if isinstance(text, str) and " " in text:
        parts = text.split()
        if len(parts) == 2 and "/" in parts[1]:
            whole = int(parts[0])
            num, den = map(int, parts[1].split("/"))
            converted = Fraction(whole * den + num, den)

            conversion_info = {
                "mixed_text": text,
                "whole": whole,
                "num": num,
                "den": den,
                "result_num": converted.numerator,
                "result_den": converted.denominator,
            }
            fraction = converted

    return fraction, conversion_info


def _format_fraction(frac: Fraction) -> str:
    """Форматирует дробь для отображения."""
    return str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"


def _lcm(a: int, b: int) -> int:
    """Вычисляет наименьшее общее кратное."""
    return abs(a * b) // math.gcd(a, b)


def _render_expression(node: Dict[str, Any]) -> str:
    """Рендерит expression_tree в читаемую строку."""

    def helper(cur: Dict[str, Any]) -> Tuple[str, int]:
        node_type = cur.get("type")
        if node_type == "common":
            n, d = cur["value"]
            return f"{n}/{d}", 3
        if node_type == "integer":
            value = cur.get("value", cur.get("text", "0"))
            return str(value), 3

        operation = cur.get("operation")
        operands = cur.get("operands", [])
        if not operation or len(operands) != 2:
            return "", 3

        op_precedence = {"add": 1, "subtract": 1, "multiply": 2, "divide": 2}
        symbols = {"add": " + ", "subtract": " − ", "multiply": " · ", "divide": " : "}
        prec = op_precedence.get(operation, 3)
        symbol = symbols.get(operation, " ? ")

        left_str, left_prec = helper(operands[0])
        right_str, right_prec = helper(operands[1])

        if left_prec < prec:
            left_str = f"({left_str})"
        if right_prec < prec or (operation == "subtract" and right_prec == prec):
            right_str = f"({right_str})"

        return f"{left_str}{symbol}{right_str}", prec

    expression, _ = helper(node)
    return expression or ""


def _detect_requested_part(task_data: Dict[str, Any]) -> Optional[str]:
    """Определяет, какую часть дроби нужно записать в ответе."""
    text = (task_data.get("question_text") or "").lower()
    if "знаменател" in text:
        return "denominator"
    if "числител" in text:
        return "numerator"
    return None
