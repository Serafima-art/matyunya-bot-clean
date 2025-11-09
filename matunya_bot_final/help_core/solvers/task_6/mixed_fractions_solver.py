# matunya_bot_final/help_core/solvers/task_6/mixed_fractions_solver.py
"""
Mixed fractions solver (task 6, subtype mixed_fractions).

Решатель формирует подробные шаги по методике ФИПИ:
1. Показываем исходное выражение.
2. Переводим все числа в обыкновенные дроби.
3. Выполняем действия (сложение/вычитание, умножение, деление).
4. Выводим финальный ответ.

Все шаги оформляются через StepBuilder с description_key и description_params,
чтобы humanizer мог отрисовать эталонный вывод.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple
import math

getcontext().prec = 28


# ---------------------------------------------------------------------------
# Step builder
# ---------------------------------------------------------------------------


@dataclass
class StepBuilder:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1

    def add_step(
        self,
        description_key: str,
        description_params: Optional[Dict[str, Any]] = None,
        formula_representation: Optional[str] = None,
        formula_general: Optional[str] = None,
        formula_calculation: Optional[str] = None,
        calculation_result: Optional[str] = None,
    ) -> None:
        step: Dict[str, Any] = {
            "step_number": self.counter,
            "description_key": description_key,
            "description_params": description_params or {},
        }
        if formula_representation:
            step["formula_representation"] = formula_representation
        if formula_general:
            step["formula_general"] = formula_general
        if formula_calculation:
            step["formula_calculation"] = formula_calculation
        if calculation_result:
            step["calculation_result"] = calculation_result
        self.steps.append(step)
        self.counter += 1


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    if not expression_tree:
        raise ValueError("Отсутствует expression_tree в task_data")

    source_expression = task_data.get("source_expression")
    if not source_expression:
        source_expression = _extract_raw_expr_from_question(task_data.get("question_text", ""))
    original_expr_display = _displayify_original(source_expression)

    builder = StepBuilder()

    builder.add_step(
        description_key="SEE_ORIGINAL_EXPRESSION",
        description_params={"expression": original_expr_display},
    )

    conversions = _collect_conversions(expression_tree)
    if conversions:
        conversion_block = "\n".join(f"➡️ {line}" for line in conversions)
        builder.add_step(
            description_key="CONVERT_ALL_NUMBERS_TO_FRACTIONS",
            description_params={"conversion_list": conversion_block},
        )

    final_fraction = _evaluate_tree(expression_tree, builder)
    value_display = _fraction_as_decimal_string(final_fraction)

    builder.add_step(
        description_key="FIND_FINAL_ANSWER",
        description_params={"value": value_display},
    )

    return {
        "question_id": task_data.get("id", "task6_mixed_placeholder"),
        "question_group": "TASK6_MIXED",
        "explanation_idea_key": "MULTIPLY_DIVIDE_FRACTIONS_IDEA",
        "explanation_idea_params": {},
        "explanation_idea": "",
        "calculation_steps": builder.steps,
        # убираем дублирующий текст, оставляем только данные
        "final_answer": {"value_machine": float(final_fraction)},
        "hints": [],
        "hints_keys": ["HINT_CONVERT_MIXED", "HINT_DIVIDE_AS_MULTIPLY"],
    }


# ---------------------------------------------------------------------------
# Tree traversal and conversions
# ---------------------------------------------------------------------------


def _collect_conversions(node: Dict[str, Any]) -> List[str]:
    conversions: List[str] = []
    seen: set[str] = set()

    def walk(current: Any):
        if not isinstance(current, dict):
            return
        node_type = current.get("type")
        if node_type in {"decimal", "mixed", "integer"}:
            text = current.get("text", "")
            if text not in seen:
                seen.add(text)
                formula = _conversion_formula(current)
                if formula:
                    conversions.append(formula)
            return
        for child in current.get("operands", []):
            walk(child)

    walk(node)
    return conversions


def _conversion_formula(node: Dict[str, Any]) -> Optional[str]:
    node_type = node.get("type")
    if node_type == "decimal":
        return _decimal_conversion_formula(node)
    if node_type == "mixed":
        return _mixed_conversion_formula(node)
    if node_type == "integer":
        text = node.get("text", "")
        return f"{text} = {text}/1"
    return None


def _decimal_conversion_formula(node: Dict[str, Any]) -> str:
    text = str(node.get("text", ""))
    normalized = text.replace(",", ".")
    sign = -1 if normalized.startswith("-") else 1
    raw = normalized.lstrip("-")

    if "." in raw:
        int_part, frac_part = raw.split(".")
    else:
        int_part, frac_part = raw, ""

    if not frac_part:
        frac = Fraction(sign * int(int_part or "0"), 1)
        return f"{text} = {_fraction_str(frac)}"

    base_den = 10 ** len(frac_part)
    base_num = int(int_part or "0") * base_den + int(frac_part)
    improper = Fraction(sign * base_num, base_den)

    sign_prefix = "−" if sign < 0 else ""
    text_clean = text.lstrip("-")

    # если нет целой части (0,5)
    if int_part == "0":
        # пример: −0,5 = −5/10
        line = (
            f"{sign_prefix}{text_clean} = {sign_prefix}{int(frac_part)}/{base_den}"
        )
    else:
        # пример: 3,1 = 3 1/10 = (3 · 10 + 1)/10 = 31/10
        line = (
            f"{sign_prefix}{text_clean} = {sign_prefix}{int_part} {int(frac_part)}/{base_den} = "
            f"{sign_prefix}({int_part} · {base_den} + {int(frac_part)}) / {base_den} = "
            f"{sign_prefix}{base_num}/{base_den}"
        )

    return line

def _mixed_conversion_formula(node: Dict[str, Any]) -> str:
    text = node.get("text", "")
    whole = int(node.get("whole", 0))
    num = int(node.get("num", 0))
    den = int(node.get("den", 1))
    if den == 0:
        raise ValueError("Неверный знаменатель смешанного числа")

    if whole >= 0:
        improper = whole * den + num
        inner = f"({whole} · {den} + {num}) / {den}"
    else:
        improper = whole * den - num
        inner = f"({whole} · {den} - {num}) / {den}"

    return f"{text} = {inner} = {improper} / {den}"


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------


def _evaluate_tree(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
    node_type = node.get("type")
    if node_type in {"decimal", "mixed", "integer", "common"}:
        return _node_to_fraction(node)

    operation = node.get("operation")
    operands = node.get("operands", [])
    if len(operands) != 2:
        raise ValueError("Ожидались бинарные операции в дереве.")

    left = _evaluate_tree(operands[0], builder)
    right = _evaluate_tree(operands[1], builder)

    if operation == "divide":
        result, formula = _describe_division(left, right)
        builder.add_step(
            description_key="DIVIDE_AS_MULTIPLY",
            description_params={
                "operation_name": "деление",
                "extra_explanation": "Для этого заменяем деление на умножение обратной дробью.",
                "formula": formula,
            },
        )
        return result

    if operation == "multiply":
        result, formula = _describe_multiplication(left, right)
        builder.add_step(
            description_key="PERFORM_MULTIPLICATION",
            description_params={
                "operation_name": "умножение",
                "extra_explanation": "Для этого перемножаем числители и знаменатели.",
            },
            formula_representation=formula,
        )
        return result

    if operation == "add":
        result, formula, lcm_den = _describe_add_sub(left, right, "+")
        extra_expl = (
            f"Для этого приводим дроби к общему знаменателю {lcm_den}."
            if lcm_den not in (1, 10, 100)
            else ""
        )
        builder.add_step(
            description_key="FINAL_OPERATION",
            description_params={"operation_name": "вычитание"},
            formula_representation=formula,
        )
        return result

    if operation == "subtract":
        result, formula, lcm_den = _describe_add_sub(left, right, "-")
        extra_text = f"Дроби приводим к общему знаменателю {lcm_den}."
        builder.add_step(
            description_key="FINAL_OPERATION",
            description_params={
                "operation_name": "вычитание",
                "extra_explanation": extra_text
            },
            formula_representation=formula,
        )
        return result

    raise ValueError(f"Неизвестная операция: {operation}")


def _node_to_fraction(node: Dict[str, Any]) -> Fraction:
    node_type = node.get("type")

    if node_type == "decimal":
        text = str(node.get("text", "0")).replace(",", ".").strip()
        if "." in text:
            int_part, frac_part = text.split(".")
            base_den = 10 ** len(frac_part)
            sign = -1 if text.startswith("-") else 1
            base_num = int(int_part or "0") * base_den + int(frac_part)
            base_num *= sign
            # Возвращаем десятичную дробь БЕЗ сокращения (с знаменателем 10/100/1000…)
            return Fraction(base_num, base_den, _normalize=True)  # создаём нормально...
            # Примечание: если твоя версия Python 3.13 поддерживает _normalize=False
            # и тебе нужно жёстко запретить сокращение уже здесь, замени строку выше на:
            # return Fraction(base_num, base_den, _normalize=False)
        else:
            return Fraction(int(text), 1)

    if node_type == "mixed":
        whole = int(node.get("whole", 0))
        num = int(node.get("num", 0))
        den = int(node.get("den", 1))
        if den == 0:
            raise ValueError("Неверный знаменатель смешанного числа")
        improper = whole * den + (num if whole >= 0 else -num)
        return Fraction(improper, den)  # нормальная дробь — так безопаснее для последующих шагов

    if node_type == "integer":
        value = int(node.get("value", 0))
        return Fraction(value, 1)

    if node_type == "common":
        num, den = node.get("value", [0, 1])
        return Fraction(int(num), int(den))

    raise ValueError(f"Неизвестный тип узла: {node_type}")

# ---------------------------------------------------------------------------
# Operation descriptions
# ---------------------------------------------------------------------------

def _describe_division(left: Fraction, right: Fraction) -> Tuple[Fraction, str]:
    # Защита от деления на ноль
    if right.numerator == 0:
        raise ZeroDivisionError("Деление на ноль.")

    # Сырые числители/знаменатели
    num_left, den_left = left.numerator, left.denominator
    num_right, den_right = right.numerator, right.denominator

    # «Переворот» правой дроби
    flipped_num, flipped_den = den_right, num_right

    # Несокращённая промежуточная дробь после замены деления на умножение
    interm_num = num_left * flipped_num
    interm_den = den_left * flipped_den

    # Отдельно: сокращённый результат для красивого финала и дальнейших вычислений
    simplified = Fraction(interm_num, interm_den)  # нормализация включена
    simplified_str = _fraction_str(simplified)

    # Формула с явной промежуточной несокращённой дробью
    formula = (
        f"{num_left}/{den_left} : {num_right}/{den_right} = "
        f"{num_left}/{den_left} · {flipped_num}/{flipped_den} = "
        f"({num_left} · {flipped_num}) / ({den_left} · {flipped_den}) = "
        f"{interm_num}/{interm_den} = {simplified_str}"
    )

    return simplified, formula

def _describe_multiplication(left: Fraction, right: Fraction) -> Tuple[Fraction, str]:
    # вычисляем произведение без потери промежуточной формы
    num = left.numerator * right.numerator
    den = left.denominator * right.denominator
    result = Fraction(num, den)

    # добавляем десятичную форму результата
    decimal_str = _fraction_as_decimal_string(result)

    formula = (
        f"{_fraction_str(left)} · {_fraction_str(right)} = "
        f"({left.numerator} · {right.numerator}) / ({left.denominator} · {right.denominator}) = "
        f"{num}/{den} = {_fraction_as_decimal_string(result)}"
    )

    return result, formula


def _describe_add_sub(left: Fraction, right: Fraction, sign_symbol: str) -> Tuple[Fraction, str, int]:
    # 1) Быстрый путь для целых и десятичных (деноминаторы 1, 10, 100):
    if left.denominator in (1, 10, 100) and right.denominator in (1, 10, 100):
        result = left + right if sign_symbol == "+" else left - right
        left_str = _fraction_as_decimal_string(left)
        right_str = _fraction_as_decimal_string(right)
        result_str = _fraction_as_decimal_string(result)
        formula = f"{left_str} {sign_symbol} {right_str} = {result_str}"
        return result, formula, 1  # lcm_den не нужен, возвращаем 1 как формальный маркер

    # 2) Стандартная логика для обыкновенных дробей (через НОЗ):
    lcm_den = _lcm(left.denominator, right.denominator)
    left_scaled = left.numerator * (lcm_den // left.denominator)
    right_scaled = right.numerator * (lcm_den // right.denominator)

    result_num = left_scaled + right_scaled if sign_symbol == "+" else left_scaled - right_scaled
    result = Fraction(result_num, lcm_den)

    # Если дробь уже несократима — не дублируем конечную запись " = a/b"
    tail = f" = {_fraction_str(result)}"
    if math.gcd(abs(result_num), lcm_den) == 1:
        tail = ""

    formula = (
        f"{_fraction_str(left)} {sign_symbol} {_fraction_str(right)} = "
        f"{left_scaled}/{lcm_den} {sign_symbol} {right_scaled}/{lcm_den} = "
        f"{result_num}/{lcm_den}{tail}"
    )
    return result, formula, lcm_den

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _fraction_str(frac: Fraction) -> str:
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def _fraction_as_decimal_string(frac: Fraction) -> str:
    decimal_value = Decimal(frac.numerator) / Decimal(frac.denominator)
    s = format(decimal_value.normalize(), "f").rstrip("0").rstrip(".")
    if s == "-0":
        s = "0"
    s = s or "0"
    return s.replace(".", ",")


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)


def _extract_raw_expr_from_question(question_text: str) -> str:
    if not question_text:
        return ""
    lines = [ln.strip() for ln in question_text.splitlines()]
    buffer: List[str] = []
    for line in lines:
        if line.lower().startswith("ответ"):
            break
        if line:
            buffer.append(line)
    return buffer[-1] if buffer else ""


def _displayify_original(expr: str) -> str:
    if not expr:
        return ""
    # Для подтипа mixed_fractions не меняем двоеточие на слеш
    return (
        expr
        .replace(".", ",")
        .replace("-", "−")
    )
