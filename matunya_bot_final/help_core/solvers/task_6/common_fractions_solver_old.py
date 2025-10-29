"""Пошаговый решатель для подтипа common_fractions (Задание 6).

Решение формируется по педагогическим рекомендациям ФИПИ:
- отдельные ветки для каждого паттерна;
- подробные пояснения на каждом шаге;
- соблюдение порядка действий и явное отображение всех преобразований.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Optional, Tuple
import math

# ---------------------------------------------------------------------------
# Вспомогательные структуры
# ---------------------------------------------------------------------------


@dataclass
class Step:
    step_number: int
    description: str
    formula_representation: str
    formula_calculation: str
    calculation_result: str


@dataclass
class StepBuilder:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1

    def add(
        self,
        description: str,
        formula_representation: str,
        formula_calculation: str,
        calculation_result: str,
    ) -> None:
        self.steps.append(
            {
                "step_number": self.counter,
                "description": description,
                "formula_representation": formula_representation,
                "formula_calculation": formula_calculation,
                "calculation_result": calculation_result,
            }
        )
        self.counter += 1


# ---------------------------------------------------------------------------
# Публичный интерфейс
# ---------------------------------------------------------------------------

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    pattern = task_data.get("pattern")
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    if not pattern or not expression_tree:
        raise ValueError("Некорректные данные задачи: отсутствует pattern или expression_tree.")

    builder = StepBuilder()
    expression_preview = _render_expression(expression_tree)
    builder.add(
        description="Рассмотрим исходное выражение и определим порядок действий.",
        formula_representation=expression_preview,
        formula_calculation=expression_preview,
        calculation_result="",
    )

    if pattern == "cf_addition_subtraction":
        result_fraction = _solve_addition_subtraction(expression_tree, builder)
        explanation_idea = "Чтобы сложить или вычесть дроби, приведём их к общему знаменателю, затем выполним действие и упростим результат."
    elif pattern == "multiplication_division":
        result_fraction = _solve_multiplication_division(expression_tree, builder)
        explanation_idea = "Для операций умножения и деления дробей важно сначала перевести смешанные числа в неправильные дроби и строго следовать алгоритму умножения или деления."
    elif pattern == "parentheses_operations":
        result_fraction = _solve_parentheses_operations(expression_tree, builder)
        explanation_idea = "Сначала выполняем действие в скобках, затем оставшиеся операции. Каждый этап подробно расписываем и приводим результат к простейшему виду."
    elif pattern == "complex_fraction":
        result_fraction = _solve_complex_fraction(expression_tree, builder)
        explanation_idea = "В сложной дроби сначала вычисляем числитель, затем делим результат на знаменатель, превращая деление в умножение на обратную дробь."
    else:
        raise ValueError(f"Неизвестный паттерн: {pattern}")

    _add_final_step(task_data, builder, result_fraction)

    answer_type = task_data.get("answer_type", "decimal")
    if answer_type == "decimal":
        display_value = str(float(result_fraction))
    else:
        display_value = str(result_fraction.numerator if result_fraction.denominator == 1 else result_fraction.numerator)

    return {
        "question_id": task_data.get("id", "task_6_common"),
        "question_group": "TASK6_COMMON",
        "explanation_idea": explanation_idea,
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": float(result_fraction),
            "value_display": display_value,
        },
        "hints": [
            "Следите за порядком действий: сначала скобки, затем умножение и деление, в конце сложение или вычитание.",
            "При сложении и вычитании дробей обязательно приводите их к общему знаменателю.",
            "Чтобы разделить на дробь, умножьте на обратную (перевёрнутую) дробь.",
            "Проверьте, можно ли сократить результат, и приводите ответ к требуемому формату.",
        ],
    }


# ---------------------------------------------------------------------------
# Решатели для отдельных паттернов
# ---------------------------------------------------------------------------

def _solve_addition_subtraction(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
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
    left_node, right_node = node["operands"]
    operation = node["operation"]

    left_frac, left_note = _convert_possible_mixed(left_node)
    right_frac, right_note = _convert_possible_mixed(right_node)

    for description, formula in left_note + right_note:
        builder.add(
            description=description,
            formula_representation=formula,
            formula_calculation=formula,
            calculation_result=formula.split("=")[-1].strip(),
        )

    if operation == "divide":
        result = _explain_division(builder, left_frac, right_frac)
    else:  # multiply
        result = _explain_multiplication(builder, left_frac, right_frac)

    return result


def _solve_parentheses_operations(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
    left_node, right_node = node["operands"]
    outer_operation = node["operation"]

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

    if outer_operation == "multiply":
        result = _explain_multiplication(builder, inner_result, other_operand, context="После вычисления выражения в скобках умножаем полученную дробь на второй множитель.")
    else:
        result = _explain_division(builder, inner_result, other_operand, context="После вычисления выражения в скобках делим результат на оставшуюся дробь.")

    return result


def _solve_complex_fraction(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
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

    denominator = _extract_fraction(denominator_node)

    result = _explain_division(
        builder,
        numerator,
        denominator,
        context="Теперь делим найденный числитель на знаменатель.",
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
    verb = "сложить" if operation == "add" else "вычесть"
    action_word = "Складываем" if operation == "add" else "Вычитаем"

    prefix = f"{context}. " if context else ""
    builder.add(
        description=f"{prefix}Найдём наименьшее общее кратное (НОК) знаменателей {left.denominator} и {right.denominator}, чтобы {verb} дроби.",
        formula_representation=f"{_format_fraction(left)} {'+' if operation == 'add' else '−'} {_format_fraction(right)}",
        formula_calculation=f"НОК({left.denominator}, {right.denominator}) = {_lcm(left.denominator, right.denominator)}",
        calculation_result=str(_lcm(left.denominator, right.denominator)),
    )

    lcm_value = _lcm(left.denominator, right.denominator)
    left_multiplier = lcm_value // left.denominator
    right_multiplier = lcm_value // right.denominator
    left_scaled_num = left.numerator * left_multiplier
    right_scaled_num = right.numerator * right_multiplier

    builder.add(
        description=f"{prefix}Приведём дроби к общему знаменателю {lcm_value}. Умножаем числители и знаменатели на {left_multiplier} и {right_multiplier} соответственно.",
        formula_representation=f"{_format_fraction(left)} {'+' if operation == 'add' else '−'} {_format_fraction(right)}",
        formula_calculation=(
            f"{left.numerator}·{left_multiplier}/{left.denominator}·{left_multiplier} = {left_scaled_num}/{lcm_value}, "
            f"{right.numerator}·{right_multiplier}/{right.denominator}·{right_multiplier} = {right_scaled_num}/{lcm_value}"
        ),
        calculation_result=f"{left_scaled_num}/{lcm_value} {'+' if operation == 'add' else '−'} {right_scaled_num}/{lcm_value}",
    )

    raw_numerator = left_scaled_num + (right_scaled_num if operation == "add" else -right_scaled_num)
    builder.add(
        description=f"{prefix}{action_word} числители, так как знаменатели теперь одинаковые.",
        formula_representation=f"{left_scaled_num}/{lcm_value} {'+' if operation == 'add' else '−'} {right_scaled_num}/{lcm_value}",
        formula_calculation=f"{left_scaled_num} {'+' if operation == 'add' else '−'} {right_scaled_num} = {raw_numerator}",
        calculation_result=f"{raw_numerator}/{lcm_value}",
    )

    result_fraction = Fraction(raw_numerator, lcm_value)
    gcd_value = math.gcd(abs(result_fraction.numerator), result_fraction.denominator)

    if gcd_value > 1:
        builder.add(
            description=f"{prefix}Сократим дробь {raw_numerator}/{lcm_value}. Числитель и знаменатель делятся на {gcd_value}, поэтому делим оба на {gcd_value}.",
            formula_representation=f"{raw_numerator}/{lcm_value}",
            formula_calculation=f"{raw_numerator}:{gcd_value} = {result_fraction.numerator}, {lcm_value}:{gcd_value} = {result_fraction.denominator}",
            calculation_result=_format_fraction(result_fraction),
        )
    else:
        builder.add(
            description=f"{prefix}Числитель и знаменатель не имеют общих делителей больше 1, дробь уже несократима.",
            formula_representation=f"{raw_numerator}/{lcm_value}",
            formula_calculation=f"{raw_numerator}/{lcm_value} = {_format_fraction(result_fraction)}",
            calculation_result=_format_fraction(result_fraction),
        )

    return result_fraction


def _explain_multiplication(
    builder: StepBuilder,
    left: Fraction,
    right: Fraction,
    context: Optional[str] = None,
) -> Fraction:
    prefix = f"{context} " if context else ""
    builder.add(
        description=f"{prefix}Представим произведение дробей под общей дробной чертой.",
        formula_representation=f"{_format_fraction(left)} · {_format_fraction(right)}",
        formula_calculation=f"{_format_fraction(left)} · {_format_fraction(right)} = ({left.numerator}·{right.numerator})/({left.denominator}·{right.denominator})",
        calculation_result=f"({left.numerator}·{right.numerator})/({left.denominator}·{right.denominator})",
    )

    num_factors = [left.numerator, right.numerator]
    den_factors = [left.denominator, right.denominator]
    cancellations: List[str] = []

    for i in range(len(num_factors)):
        for j in range(len(den_factors)):
            g = math.gcd(num_factors[i], den_factors[j])
            if g > 1:
                original_num = num_factors[i]
                original_den = den_factors[j]
                num_factors[i] //= g
                den_factors[j] //= g
                cancellations.append(f"{original_num} и {original_den} делим на {g}")

    if cancellations:
        description = f"{prefix}Сократим общие множители: " + "; ".join(cancellations) + "."
        simplified_expr = f"({num_factors[0]}·{num_factors[1]})/({den_factors[0]}·{den_factors[1]})"
    else:
        description = f"{prefix}Общие множители отсутствуют, сокращать нечего."
        simplified_expr = f"({num_factors[0]}·{num_factors[1]})/({den_factors[0]}·{den_factors[1]})"

    builder.add(
        description=description,
        formula_representation=f"{_format_fraction(left)} · {_format_fraction(right)}",
        formula_calculation=f"({left.numerator}·{right.numerator})/({left.denominator}·{right.denominator}) = {simplified_expr}",
        calculation_result=simplified_expr,
    )

    raw_num = num_factors[0] * num_factors[1]
    raw_den = den_factors[0] * den_factors[1]
    result = Fraction(raw_num, raw_den)
    builder.add(
        description=f"{prefix}Перемножим оставшиеся числители и знаменатели.",
        formula_representation=simplified_expr,
        formula_calculation=f"{simplified_expr} = {raw_num}/{raw_den}",
        calculation_result=_format_fraction(result),
    )
    return result


def _explain_division(
    builder: StepBuilder,
    left: Fraction,
    right: Fraction,
    context: Optional[str] = None,
) -> Fraction:
    prefix = f"{context} " if context else ""
    flipped = Fraction(right.denominator, right.numerator)
    builder.add(
        description=f"{prefix}Чтобы разделить дробь {_format_fraction(left)} на {_format_fraction(right)}, заменим деление умножением на обратную дробь.",
        formula_representation=f"{_format_fraction(left)} : {_format_fraction(right)}",
        formula_calculation=f"{_format_fraction(left)} · {flipped.numerator}/{flipped.denominator}",
        calculation_result="",
    )

    return _explain_multiplication(builder, left, flipped, context="После замены деления на умножение")


# ---------------------------------------------------------------------------
# Поддерживающие функции
# ---------------------------------------------------------------------------

def _add_final_step(task_data: Dict[str, Any], builder: StepBuilder, fraction: Fraction) -> None:
    answer_type = task_data.get("answer_type", "decimal")
    if answer_type == "integer":
        description = (
            "Задача требует указать целую часть результата (например, числитель полученной несократимой дроби). "
            "Фиксируем итоговое значение."
        )
        builder.add(
            description=description,
            formula_representation=_format_fraction(fraction),
            formula_calculation=_format_fraction(fraction),
            calculation_result=str(fraction.numerator if fraction.denominator == 1 else fraction.numerator),
        )
    else:
        decimal_value = float(fraction)
        builder.add(
            description="Так как ответ в бланке ОГЭ записывается десятичным числом, преобразуем полученную дробь.",
            formula_representation=_format_fraction(fraction),
            formula_calculation=f"{_format_fraction(fraction)} = {decimal_value}",
            calculation_result=str(decimal_value),
        )


def _extract_fraction(node: Dict[str, Any]) -> Fraction:
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
        builder = StepBuilder()  # временный, шаги здесь не нужны
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


def _convert_possible_mixed(node: Dict[str, Any]) -> Tuple[Fraction, List[Tuple[str, str]]]:
    fraction = _extract_fraction(node)
    notes: List[Tuple[str, str]] = []
    text = node.get("text", "")
    if isinstance(text, str) and " " in text:
        parts = text.split()
        if len(parts) == 2 and "/" in parts[1]:
            whole = int(parts[0])
            num, den = map(int, parts[1].split("/"))
            converted = Fraction(whole * den + num, den)
            notes.append(
                (
                    f"Преобразуем смешанное число {text} в неправильную дробь.",
                    f"{text} = ({whole}·{den} + {num})/{den} = {_format_fraction(converted)}",
                )
            )
    return fraction, notes


def _format_fraction(frac: Fraction) -> str:
    return str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)


def _render_expression(node: Dict[str, Any]) -> str:
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
        symbols = {"add": " + ", "subtract": " - ", "multiply": " · ", "divide": " : "}
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
