"""Пошаговый решатель для подтипа powers (Задание 6).

АРХИТЕКТУРНЫЙ ПРИНЦИП:
Решатель генерирует ТОЛЬКО структурированные данные (solution_core).
Вся текстовая логика вынесена в humanizer через систему ключей-шаблонов.

Решение формируется по педагогическим рекомендациям ФИПИ:
- отдельные ветки для каждого паттерна;
- для powers_with_fractions с повторяющейся дробью - два способа решения;
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
    "powers_with_fractions_standard": ("POWERS_FRACTIONS_STANDARD_IDEA", {}),
    "powers_with_fractions_rational": ("POWERS_FRACTIONS_RATIONAL_IDEA", {}),
    "powers_of_ten": ("POWERS_OF_TEN_IDEA", {}),
}

HINTS_KEY_MAP: Dict[str, List[str]] = {
    "powers_with_fractions": [
        "HINT_ORDER_OF_OPERATIONS",
        "HINT_POWER_OF_FRACTION",
        "HINT_COMMON_FACTOR",
    ],
    "powers_of_ten": [
        "HINT_POWER_PROPERTIES",
        "HINT_GROUP_FACTORS",
        "HINT_ADD_EXPONENTS",
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
        """Добавляет шаг в соответствии с ГОСТ-2025."""
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

    if pattern == "powers_with_fractions":
        return _solve_powers_with_fractions(task_data, expression_tree)
    elif pattern == "powers_of_ten":
        return _solve_powers_of_ten(task_data, expression_tree)
    else:
        raise ValueError(f"Неизвестный паттерн: {pattern}")


# ---------------------------------------------------------------------------
# Решатели для отдельных паттернов
# ---------------------------------------------------------------------------

def _solve_powers_with_fractions(
    task_data: Dict[str, Any],
    expression_tree: Dict[str, Any]
) -> Dict[str, Any]:
    """Решает задачи типа: a · (b/c)^n + b/c или a · (b/c)^n + d."""

    # Извлекаем исходное выражение
    expression_preview = _extract_expression_from_question(task_data) or _render_expression(expression_tree)
    has_division = ':' in expression_preview or '/' in expression_preview

    # Проверяем наличие общего множителя (дробь встречается дважды)
    common_fraction = _find_common_fraction(expression_tree)

    if common_fraction:
        # Генерируем ДВА способа решения
        return _generate_two_paths_solution(task_data, expression_tree, expression_preview, common_fraction)
    else:
        # Генерируем ОДИН стандартный способ
        return _generate_standard_solution(task_data, expression_tree, expression_preview)


def _solve_powers_of_ten(
    task_data: Dict[str, Any],
    expression_tree: Dict[str, Any]
) -> Dict[str, Any]:
    """Решает задачи типа: (a · 10^n)^m · (b · 10^k)."""

    expression_preview = _extract_expression_from_question(task_data) or _render_expression(expression_tree)
    builder = StepBuilder()

    # Шаг 0: Рассмотрим выражение
    builder.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": expression_preview},
        formula_representation=expression_preview,
    )

    # Решаем выражение
    has_division = (':' in expression_preview) or ('/' in expression_preview)
    result = _solve_powers_of_ten_steps(expression_tree, builder, keep_division=has_division)

    # Формируем solution_core
    idea_key, idea_params = IDEA_KEY_MAP["powers_of_ten"]
    hints_keys = HINTS_KEY_MAP["powers_of_ten"]

    return {
        "question_id": task_data.get("id", "task_6_powers"),
        "question_group": "TASK6_POWERS",
        "explanation_idea": "",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": idea_params,
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": result,
            "value_display": _format_decimal(result),
        },
        "hints": [],
        "hints_keys": hints_keys,
    }


# ---------------------------------------------------------------------------
# Генерация решений для powers_with_fractions
# ---------------------------------------------------------------------------

def _generate_standard_solution(
    task_data: Dict[str, Any],
    expression_tree: Dict[str, Any],
    expression_preview: str
) -> Dict[str, Any]:
    """Генерирует одно стандартное решение (без общего множителя)."""

    builder = StepBuilder()

    # Шаг 0: Рассмотрим выражение
    builder.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": expression_preview},
        formula_representation=expression_preview,
    )

    # Решаем по стандартному алгоритму
    result = _solve_standard_path(expression_tree, builder)

    # Формируем solution_core
    idea_key, idea_params = IDEA_KEY_MAP["powers_with_fractions_standard"]
    hints_keys = HINTS_KEY_MAP["powers_with_fractions"]

    return {
        "question_id": task_data.get("id", "task_6_powers"),
        "question_group": "TASK6_POWERS",
        "explanation_idea": "",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": idea_params,
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": result,
            "value_display": _format_answer(result),
        },
        "hints": [],
        "hints_keys": hints_keys,
    }


def _generate_two_paths_solution(
    task_data: Dict[str, Any],
    expression_tree: Dict[str, Any],
    expression_preview: str,
    common_fraction: Tuple[int, int]
) -> Dict[str, Any]:
    """Генерирует ДВА способа решения (с общим множителем)."""

    # === Способ 1: Стандартный ===
    builder1 = StepBuilder()
    builder1.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": expression_preview},
        formula_representation=expression_preview,
    )
    result1 = _solve_standard_path(expression_tree, builder1)

    # === Способ 2: Рациональный ===
    builder2 = StepBuilder()
    builder2.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": expression_preview},
        formula_representation=expression_preview,
    )
    result2 = _solve_rational_path(expression_tree, builder2, common_fraction)

    # Формируем solution_core с calculation_paths
    hints_keys = HINTS_KEY_MAP["powers_with_fractions"]

    return {
        "question_id": task_data.get("id", "task_6_powers"),
        "question_group": "TASK6_POWERS",
        "explanation_idea": "",
        "explanation_idea_key": "POWERS_FRACTIONS_TWO_WAYS_IDEA",
        "explanation_idea_params": {},
        "calculation_paths": [
            {
                "path_title": "Способ 1: Стандартный (по порядку действий)",
                "steps": builder1.steps,
            },
            {
                "path_title": "Способ 2: Рациональный (вынесение общего множителя)",
                "is_recommended": True,
                "steps": builder2.steps,
            }
        ],
        "final_answer": {
            "value_machine": result1,
            "value_display": _format_answer(result1),
        },
        "hints": [],
        "hints_keys": hints_keys,
    }


# ---------------------------------------------------------------------------
# Алгоритмы решения для powers_with_fractions
# ---------------------------------------------------------------------------

def _solve_standard_path(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
    """Стандартный путь: возведение в степень → умножение → сложение/вычитание."""

    operation = node.get("operation")

    if operation in {"add", "subtract"}:
        left_node, right_node = node["operands"]

        # Вычисляем левую часть (обычно содержит степень)
        left_result = _evaluate_node_standard(left_node, builder)

        # Вычисляем правую часть
        right_result = _evaluate_node_standard(right_node, builder)

        # Выполняем финальную операцию
        if operation == "add":
            result = _add_fractions(left_result, right_result, builder)
        else:
            result = _subtract_fractions(left_result, right_result, builder)

        return result
    else:
        # Если нет сложения/вычитания, просто вычисляем
        return _evaluate_node_standard(node, builder)


def _evaluate_node_standard(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
    """Вычисляет узел дерева по стандартному алгоритму."""

    node_type = node.get("type")
    operation = node.get("operation")

    # Базовые типы
    if node_type == "integer":
        return Fraction(node["value"], 1)

    if node_type == "common":
        num, den = node["value"]
        return Fraction(num, den)

    # Операции
    if operation == "power":
        base_node, exp_node = node["operands"]
        base = _evaluate_node_standard(base_node, builder)
        exponent = _extract_integer(exp_node)

        return _power_of_fraction(base, exponent, builder)

    if operation == "multiply":
        left_node, right_node = node["operands"]
        left = _evaluate_node_standard(left_node, builder)
        right = _evaluate_node_standard(right_node, builder)

        return _multiply_fractions(left, right, builder)

    if operation == "divide":
        num_node, den_node = node["operands"]
        numerator = _evaluate_node_standard(num_node, builder)
        denominator = _evaluate_node_standard(den_node, builder)

        return numerator / denominator

    raise ValueError(f"Неизвестный тип узла: {node}")


def _solve_rational_path(
    node: Dict[str, Any],
    builder: StepBuilder,
    common_fraction: Tuple[int, int]
) -> Fraction:
    """Рациональный путь: вынесение общего множителя за скобки."""

    num, den = common_fraction
    common_frac = Fraction(num, den)

    # Шаг 1: Представим степень как произведение
    power_node = _find_power_node(node)
    if power_node:
        exponent = _extract_integer(power_node["operands"][1])
        builder.add(
            description_key="POWERS_REPRESENT_AS_PRODUCT",
            description_params={
                "num": num,
                "den": den,
                "exponent": exponent,
            },
            formula_general="(a/b)^n = a/b · a/b · ... · a/b (n раз)",
            formula_calculation=f"({num}/{den})^{exponent} = " + " · ".join([f"{num}/{den}"] * exponent),
            calculation_result=" · ".join([f"{num}/{den}"] * exponent),
        )

    # Шаг 2: Вынесем общий множитель за скобку
    # Определяем, что останется в скобках
    expression_in_brackets = _extract_expression_after_factoring(node, common_frac)

    builder.add(
        description_key="POWERS_FACTOR_OUT",
        description_params={
            "num": num,
            "den": den,
            "expression": expression_in_brackets,
        },
        formula_representation=f"{num}/{den} · ({expression_in_brackets})",
        calculation_result=f"{num}/{den} · ({expression_in_brackets})",
    )

    # Шаг 3-N: Вычисляем выражение в скобках
    result_in_brackets = _evaluate_expression_in_brackets(node, common_frac, builder)

    # Финальный шаг: Умножаем
    result = common_frac * result_in_brackets

    builder.add(
        description_key="POWERS_FINAL_MULTIPLY",
        description_params={
            "num": num,
            "den": den,
            "value": _format_answer(result_in_brackets),
        },
        formula_calculation=f"{num}/{den} · {_format_answer(result_in_brackets)} = {_format_answer(result)}",
        calculation_result=_format_answer(result),
    )

    return result


def _is_ten_power_only(node: Dict[str, Any]) -> bool:
    if node.get("type") == "integer":
        return node.get("value") == 10
    if node.get("operation") == "power":
        base = node["operands"][0]
        return base.get("type") == "integer" and base.get("value") == 10
    if node.get("operation") == "multiply":
        operands = node.get("operands", [])
        return bool(operands) and all(_is_ten_power_only(child) for child in operands)
    return False


def _convert_denominator_to_negative_powers(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    if node.get("type") == "integer":
        if node.get("value") == 10:
            return [_make_ten_power_node(-1)]
        return []
    if node.get("operation") == "power":
        base = node["operands"][0]
        if base.get("type") == "integer" and base.get("value") == 10:
            exp_value = _extract_integer(node["operands"][1])
            return [_make_ten_power_node(-exp_value)]
        return []
    if node.get("operation") == "multiply":
        result: List[Dict[str, Any]] = []
        for child in node.get("operands", []):
            result.extend(_convert_denominator_to_negative_powers(child))
        return result
    return []


def _make_ten_power_node(exp_value: int) -> Dict[str, Any]:
    base = {"type": "integer", "value": 10, "text": "10"}
    exponent = {"type": "integer", "value": exp_value, "text": str(exp_value)}
    return {"operation": "power", "operands": [base, exponent], "text": f"10^{exp_value}"}


# ---------------------------------------------------------------------------
# Алгоритм решения для powers_of_ten
# ---------------------------------------------------------------------------

def _solve_powers_of_ten_steps(
    node: Dict[str, Any],
    builder: StepBuilder,
    keep_division: bool = False
) -> float:
    """Решает выражение с степенями десяти."""

    operation = node.get("operation")

    if operation == "divide":
        if not keep_division and _is_ten_power_only(node["operands"][1]):
            transformed = {
                "operation": "multiply",
                "operands": _flatten_multiply(node["operands"][0]) + _convert_denominator_to_negative_powers(node["operands"][1]),
            }
            return _solve_powers_of_ten_steps(transformed, builder, keep_division=False)

        num_node, den_node = node["operands"]

        # Раскрываем числитель
        num_coef, num_exp = _extract_ten_power_form(num_node, builder, is_numerator=True)

        # Раскрываем знаменатель
        den_coef, den_exp = _extract_ten_power_form(den_node, builder, is_numerator=False)

        # Группируем
        builder.add(
            description_key="POWERS_TEN_GROUP",
            description_params={
                "num_coef": num_coef,
                "num_exp": num_exp,
                "den_coef": den_coef,
                "den_exp": den_exp,
            },
            formula_representation=f"({num_coef} · 10^{num_exp}) : ({den_coef} · 10^{den_exp})",
            formula_calculation=f"({num_coef} : {den_coef}) · (10^{num_exp} : 10^{den_exp})",
            calculation_result=f"({num_coef} : {den_coef}) · (10^{num_exp} : 10^{den_exp})",
        )

        # Вычисляем коэффициенты
        coef_result = num_coef / den_coef

        # Вычисляем степени
        exp_result = num_exp - den_exp

        builder.add(
            description_key="POWERS_TEN_CALCULATE",
            description_params={
                "num_coef": num_coef,
                "den_coef": den_coef,
                "coef_result": _format_decimal(coef_result),
                "num_exp": num_exp,
                "den_exp": den_exp,
                "exp_result": exp_result,
            },
            formula_general="a^n : a^m = a^(n-m)",
            formula_calculation=f"{_format_decimal(coef_result)} · 10^({num_exp}-({den_exp})) = {_format_decimal(coef_result)} · 10^{exp_result}",
            calculation_result=f"{_format_decimal(coef_result)} · 10^{exp_result}",
        )

        # Финальный результат
        result = coef_result * (10 ** exp_result)

        builder.add(
            description_key="POWERS_TEN_FINAL",
            description_params={
                "coef": _format_decimal(coef_result),
                "exp": exp_result,
                "result": _format_decimal(result),
            },
            formula_calculation=f"{_format_decimal(coef_result)} · 10^{exp_result} = {_format_decimal(result)}",
            calculation_result=_format_decimal(result),
        )

        return result

    elif operation == "multiply":
        # Обрабатываем произведение
        factors = _flatten_multiply(node)

        total_coef = 1.0
        total_exp = 0

        for factor in factors:
            coef, exp = _extract_ten_power_form(factor, builder, show_expansion=True)
            total_coef *= coef
            total_exp += exp

        # Группируем
        builder.add(
            description_key="POWERS_TEN_GROUP_MULTIPLY",
            description_params={
                "coef": _format_decimal(total_coef),
                "exp": total_exp,
            },
            formula_calculation=f"({_format_decimal(total_coef)}) · (10^{total_exp})",
            calculation_result=f"{_format_decimal(total_coef)} · 10^{total_exp}",
        )

        # Финальный результат
        result = total_coef * (10 ** total_exp)

        builder.add(
            description_key="POWERS_TEN_FINAL",
            description_params={
                "coef": _format_decimal(total_coef),
                "exp": total_exp,
                "result": _format_decimal(result),
            },
            formula_calculation=f"{_format_decimal(total_coef)} · 10^{total_exp} = {_format_decimal(result)}",
            calculation_result=_format_decimal(result),
        )

        return result

    else:
        raise ValueError(f"Неподдерживаемая операция для powers_of_ten: {operation}")


# ---------------------------------------------------------------------------
# Вспомогательные функции для операций с дробями
# ---------------------------------------------------------------------------

def _power_of_fraction(base: Fraction, exponent: int, builder: StepBuilder) -> Fraction:
    """Возводит дробь в степень."""

    result = Fraction(base.numerator ** exponent, base.denominator ** exponent)

    builder.add(
        description_key="POWERS_FRACTION_POWER",
        description_params={
            "num": base.numerator,
            "den": base.denominator,
            "exponent": exponent,
            "result_num": result.numerator,
            "result_den": result.denominator,
        },
        formula_general="(a/b)^n = a^n / b^n",
        formula_calculation=f"({base.numerator}/{base.denominator})^{exponent} = {base.numerator}^{exponent}/{base.denominator}^{exponent} = {result.numerator}/{result.denominator}",
        calculation_result=_format_answer(result),
    )

    return result


def _multiply_fractions(left: Fraction, right: Fraction, builder: StepBuilder) -> Fraction:
    """Умножает две дроби с сокращением."""

    # Перекрестное сокращение
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

    raw_num = num_factors[0] * num_factors[1]
    raw_den = den_factors[0] * den_factors[1]
    result = Fraction(raw_num, raw_den)

    if cancellations:
        builder.add(
            description_key="POWERS_MULTIPLY_WITH_CANCEL",
            description_params={
                "left_num": left.numerator,
                "left_den": left.denominator,
                "right_num": right.numerator,
                "right_den": right.denominator,
                "result_num": result.numerator,
                "result_den": result.denominator,
                "cancellations": cancellations,
            },
            formula_general="(a/b) · (c/d) = (a·c)/(b·d)",
            formula_calculation=f"{_format_answer(left)} · {_format_answer(right)} = {_format_answer(result)}",
            calculation_result=_format_answer(result),
        )
    else:
        builder.add(
            description_key="POWERS_MULTIPLY",
            description_params={
                "left_num": left.numerator,
                "left_den": left.denominator,
                "right_num": right.numerator,
                "right_den": right.denominator,
                "result_num": result.numerator,
                "result_den": result.denominator,
            },
            formula_general="(a/b) · (c/d) = (a·c)/(b·d)",
            formula_calculation=f"({left.numerator}·{right.numerator})/({left.denominator}·{right.denominator}) = {raw_num}/{raw_den}",
            calculation_result=_format_answer(result),
        )

    return result


def _add_fractions(left: Fraction, right: Fraction, builder: StepBuilder) -> Fraction:
    """Складывает две дроби."""

    lcm_value = (left.denominator * right.denominator) // math.gcd(left.denominator, right.denominator)

    left_mult = lcm_value // left.denominator
    right_mult = lcm_value // right.denominator

    left_scaled = left.numerator * left_mult
    right_scaled = right.numerator * right_mult

    result_num = left_scaled + right_scaled
    result = Fraction(result_num, lcm_value)

    if left.denominator == right.denominator:
        # Одинаковые знаменатели
        builder.add(
            description_key="POWERS_ADD_SAME_DENOM",
            description_params={
                "left_num": left.numerator,
                "right_num": right.numerator,
                "den": left.denominator,
                "result_num": result_num,
            },
            formula_calculation=f"{left.numerator}/{left.denominator} + {right.numerator}/{right.denominator} = {result_num}/{left.denominator}",
            calculation_result=_format_answer(result),
        )
    else:
        # Разные знаменатели
        builder.add(
            description_key="POWERS_ADD_DIFFERENT_DENOM",
            description_params={
                "left_num": left.numerator,
                "left_den": left.denominator,
                "right_num": right.numerator,
                "right_den": right.denominator,
                "lcm": lcm_value,
                "left_scaled": left_scaled,
                "right_scaled": right_scaled,
                "result_num": result_num,
            },
            formula_calculation=f"{left_scaled}/{lcm_value} + {right_scaled}/{lcm_value} = {result_num}/{lcm_value}",
            calculation_result=_format_answer(result),
        )

    return result


def _subtract_fractions(left: Fraction, right: Fraction, builder: StepBuilder) -> Fraction:
    """Вычитает две дроби."""

    lcm_value = (left.denominator * right.denominator) // math.gcd(left.denominator, right.denominator)

    left_mult = lcm_value // left.denominator
    right_mult = lcm_value // right.denominator

    left_scaled = left.numerator * left_mult
    right_scaled = right.numerator * right_mult

    result_num = left_scaled - right_scaled
    result = Fraction(result_num, lcm_value)

    if left.denominator == right.denominator:
        builder.add(
            description_key="POWERS_SUBTRACT_SAME_DENOM",
            description_params={
                "left_num": left.numerator,
                "right_num": right.numerator,
                "den": left.denominator,
                "result_num": result_num,
            },
            formula_calculation=f"{left.numerator}/{left.denominator} − {right.numerator}/{right.denominator} = {result_num}/{left.denominator}",
            calculation_result=_format_answer(result),
        )
    else:
        builder.add(
            description_key="POWERS_SUBTRACT_DIFFERENT_DENOM",
            description_params={
                "left_num": left.numerator,
                "left_den": left.denominator,
                "right_num": right.numerator,
                "right_den": right.denominator,
                "lcm": lcm_value,
                "left_scaled": left_scaled,
                "right_scaled": right_scaled,
                "result_num": result_num,
            },
            formula_calculation=f"{left_scaled}/{lcm_value} − {right_scaled}/{lcm_value} = {result_num}/{lcm_value}",
            calculation_result=_format_answer(result),
        )

    return result


# ---------------------------------------------------------------------------
# Вспомогательные функции для работы с деревом выражений
# ---------------------------------------------------------------------------

def _find_common_fraction(node: Dict[str, Any]) -> Optional[Tuple[int, int]]:
    """Проверяет, встречается ли одна и та же дробь дважды в дереве."""

    fractions: List[Tuple[int, int]] = []

    def collect_fractions(n: Dict[str, Any]) -> None:
        if n.get("type") == "common":
            num, den = n["value"]
            fractions.append((num, den))

        if "operands" in n:
            for operand in n["operands"]:
                collect_fractions(operand)

    collect_fractions(node)

    # Ищем дроби, встречающиеся более одного раза
    for frac in fractions:
        if fractions.count(frac) >= 2:
            return frac

    return None


def _find_power_node(node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Находит узел со степенью в дереве выражений."""

    if node.get("operation") == "power":
        return node

    if "operands" in node:
        for operand in node["operands"]:
            result = _find_power_node(operand)
            if result:
                return result

    return None


def _extract_expression_after_factoring(
    node: Dict[str, Any],
    common_frac: Fraction
) -> str:
    """Формирует выражение, которое останется в скобках после вынесения множителя."""

    operation = node.get("operation")
    op_symbol = "+" if operation == "add" else "−"

    if operation in {"add", "subtract"}:
        left_node, right_node = node["operands"]

        # Левая часть: если есть произведение с общим множителем
        left_expr = _factor_out_from_node(left_node, common_frac)

        # Правая часть: обычно это сам общий множитель, он превращается в 1
        right_expr = _factor_out_from_node(right_node, common_frac)

        return f"{left_expr} {op_symbol} {right_expr}"

    return ""


def _factor_out_from_node(node: Dict[str, Any], common_frac: Fraction) -> str:
    """Вычисляет, что останется от узла после вынесения общего множителя."""

    # Если это сам общий множитель
    if node.get("type") == "common":
        num, den = node["value"]
        if Fraction(num, den) == common_frac:
            return "1"

    # Если это произведение, содержащее общий множитель
    if node.get("operation") == "multiply":
        factors = []
        for operand in node["operands"]:
            # Пропускаем общий множитель, остальное добавляем
            if operand.get("operation") == "power":
                base_node = operand["operands"][0]
                if base_node.get("type") == "common":
                    num, den = base_node["value"]
                    if Fraction(num, den) == common_frac:
                        # Это степень общего множителя - вычитаем 1 из показателя
                        exponent = _extract_integer(operand["operands"][1])
                        if exponent - 1 > 0:
                            factors.append(f"{num}/{den}")
                        continue

            # Если это обычный множитель (не общая дробь)
            if operand.get("type") == "integer":
                factors.append(str(operand["value"]))
            elif operand.get("type") == "common":
                num, den = operand["value"]
                if Fraction(num, den) != common_frac:
                    factors.append(f"{num}/{den}")

        return " · ".join(factors) if factors else "1"

    return "1"


def _evaluate_expression_in_brackets(
    node: Dict[str, Any],
    common_frac: Fraction,
    builder: StepBuilder
) -> Fraction:
    """Вычисляет выражение в скобках после вынесения общего множителя."""

    operation = node.get("operation")

    if operation in {"add", "subtract"}:
        left_node, right_node = node["operands"]

        # Вычисляем левую часть (обычно произведение)
        left_result = _evaluate_factored_node(left_node, common_frac, builder)

        # Правая часть обычно становится 1
        right_result = Fraction(1, 1)

        # Складываем или вычитаем
        if operation == "add":
            result = left_result + right_result
            builder.add(
                description_key="POWERS_ADD_IN_BRACKETS",
                description_params={
                    "left": _format_answer(left_result),
                    "right": _format_answer(right_result),
                    "result": _format_answer(result),
                },
                formula_calculation=f"{_format_answer(left_result)} + {_format_answer(right_result)} = {_format_answer(result)}",
                calculation_result=_format_answer(result),
            )
        else:
            result = left_result - right_result
            builder.add(
                description_key="POWERS_SUBTRACT_IN_BRACKETS",
                description_params={
                    "left": _format_answer(left_result),
                    "right": _format_answer(right_result),
                    "result": _format_answer(result),
                },
                formula_calculation=f"{_format_answer(left_result)} − {_format_answer(right_result)} = {_format_answer(result)}",
                calculation_result=_format_answer(result),
            )

        return result

    return Fraction(1, 1)


def _evaluate_factored_node(
    node: Dict[str, Any],
    common_frac: Fraction,
    builder: StepBuilder
) -> Fraction:
    """Вычисляет узел после вынесения из него общего множителя."""

    if node.get("operation") == "multiply":
        result = Fraction(1, 1)

        for operand in node["operands"]:
            # Пропускаем один экземпляр общего множителя
            if operand.get("operation") == "power":
                base_node = operand["operands"][0]
                if base_node.get("type") == "common":
                    num, den = base_node["value"]
                    if Fraction(num, den) == common_frac:
                        exponent = _extract_integer(operand["operands"][1])
                        # Уменьшаем показатель на 1
                        remaining_power = exponent - 1
                        if remaining_power > 0:
                            result *= Fraction(num, den) ** remaining_power
                        continue

            # Умножаем на остальные множители
            if operand.get("type") == "integer":
                value = operand["value"]
                result *= Fraction(value, 1)

                # Показываем умножение с сокращением если возможно
                if result.denominator != 1:
                    builder.add(
                        description_key="POWERS_MULTIPLY_IN_BRACKETS",
                        description_params={
                            "value": value,
                            "frac_num": common_frac.numerator,
                            "frac_den": common_frac.denominator,
                            "result": _format_answer(result),
                        },
                        formula_calculation=f"{value} · {common_frac.numerator}/{common_frac.denominator} = {_format_answer(result)}",
                        calculation_result=_format_answer(result),
                    )

        return result

    return Fraction(1, 1)


def _extract_ten_power_form(
    node: Dict[str, Any],
    builder: StepBuilder,
    is_numerator: bool = True,
    show_expansion: bool = False
) -> Tuple[float, int]:
    """Возвращает пару (коэффициент, показатель степени) для 10^n."""

    if node.get("operation") == "multiply":
        coef = 1.0
        exponent = 0

        for operand in node["operands"]:
            if operand.get("operation") == "power":
                base = operand["operands"][0]
                exp_node = operand["operands"][1]
                if base.get("type") == "integer" and base.get("value") == 10:
                    exponent += _extract_integer(exp_node)
                    continue
            if operand.get("type") == "integer":
                coef *= float(operand["value"])
            elif operand.get("type") == "decimal":
                value = float(str(operand["value"]).replace(",", "."))
                coef *= value

        return coef, exponent

    elif node.get("operation") == "power":
        base_node = node["operands"][0]
        outer_exp = _extract_integer(node["operands"][1])

        if base_node.get("operation") == "multiply":
            inner_coef = 1.0
            inner_exp = 0

            for operand in base_node["operands"]:
                if operand.get("operation") == "power":
                    base = operand["operands"][0]
                    if base.get("type") == "integer" and base.get("value") == 10:
                        inner_exp = _extract_integer(operand["operands"][1])
                elif operand.get("type") == "integer":
                    inner_coef = float(operand["value"])
                elif operand.get("type") == "decimal":
                    inner_coef = float(str(operand["value"]).replace(",", "."))

            result_coef = inner_coef ** outer_exp
            result_exp = inner_exp * outer_exp

            location = "числителе" if is_numerator else "знаменателе"

            builder.add(
                description_key="POWERS_TEN_EXPAND_POWER",
                description_params={
                    "coef": int(inner_coef),
                    "inner_exp": inner_exp,
                    "outer_exp": outer_exp,
                    "result_coef": int(result_coef),
                    "result_exp": result_exp,
                    "location": location,
                },
                formula_general="(a · b)^n = a^n · b^n, (a^n)^m = a^(n·m)",
                formula_calculation=f"({int(inner_coef)} · 10^{inner_exp})^{outer_exp} = {int(inner_coef)}^{outer_exp} · (10^{inner_exp})^{outer_exp} = {int(result_coef)} · 10^{result_exp}",
                calculation_result=f"{int(result_coef)} · 10^{result_exp}",
            )

            return result_coef, result_exp

        if base_node.get("type") == "integer" and base_node.get("value") == 10:
            return 1.0, outer_exp

    elif node.get("type") == "integer":
        return float(node["value"]), 0
    elif node.get("type") == "decimal":
        return float(str(node["value"]).replace(",", ".")), 0

    return 1.0, 0


def _flatten_multiply(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Разворачивает вложенные умножения в плоский список множителей."""

    if node.get("operation") != "multiply":
        return [node]

    result = []
    for operand in node.get("operands", []):
        if operand.get("operation") == "multiply":
            result.extend(_flatten_multiply(operand))
        else:
            result.append(operand)

    return result


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------

def _extract_integer(node: Dict[str, Any]) -> int:
    """Извлекает целое число из узла."""
    if node.get("type") == "integer":
        return node["value"]
    raise ValueError(f"Ожидалось целое число, получено: {node}")


def _format_answer(value: Fraction) -> str:
    """Форматирует дробь для отображения в ответе."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _format_decimal(value: float) -> str:
    """Форматирует десятичное число, убирая лишние нули."""
    if value == int(value):
        return str(int(value))
    return str(value).rstrip('0').rstrip('.')


def _extract_expression_from_question(task_data: Dict[str, Any]) -> Optional[str]:
    """Извлекает исходное выражение из question_text."""
    import re

    txt = task_data.get("question_text") or ""
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    if not lines:
        return None

    header_prefixes = (
        "выполни", "вычисли", "найди", "запиши", "реши", "получи", "ответ"
    )

    for ln in lines:
        low = ln.lower()

        if any(low.startswith(prefix) for prefix in header_prefixes):
            continue
        if low.endswith(":"):
            continue

        if not re.search(r"\d", ln):
            continue

        if not re.search(r"[/:·+\-−()^]", ln):
            continue

        return ln

    return None


def _render_expression(node: Dict[str, Any]) -> str:
    """Рендерит expression_tree в читаемую строку."""

    def helper(cur: Dict[str, Any]) -> Tuple[str, int]:
        text = cur.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip(), 3

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

        op_precedence = {"add": 1, "subtract": 1, "multiply": 2, "divide": 2, "power": 3}
        symbols = {
            "add": " + ",
            "subtract": " − ",
            "multiply": " · ",
            "divide": " : ",
            "power": "^"
        }
        prec = op_precedence.get(operation, 3)
        symbol = symbols.get(operation, " ? ")

        left_str, left_prec = helper(operands[0])
        right_str, right_prec = helper(operands[1])

        if operation == "power":
            if left_prec < prec:
                left_str = f"({left_str})"
            return f"{left_str}^{right_str}", prec

        if left_prec < prec:
            left_str = f"({left_str})"
        if right_prec < prec or (operation in {"subtract", "divide"} and right_prec == prec):
            right_str = f"({right_str})"

        return f"{left_str}{symbol}{right_str}", prec

    expression, _ = helper(node)
    return expression or ""
