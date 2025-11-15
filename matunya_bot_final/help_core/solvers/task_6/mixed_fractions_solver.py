"""
ФИНАЛЬНАЯ ВЕРСИЯ: Простой, надежный решатель для 'mixed_fractions'.
Архитектура: Внутренний роутер и линейные, предсказуемые алгоритмы.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from math import gcd
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# ★★★ Класс StepBuilder (стандартный) ★★★
# ---------------------------------------------------------------------------

@dataclass
class StepBuilder:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1

    def add(
        self,
        description_key: str,
        description_params: Optional[Dict[str, Any]] = None,
        formula_calculation: Optional[str] = None,
    ):
        step = {
            "step_number": self.counter,
            "description_key": description_key,
            "description_params": description_params or {},
        }
        if formula_calculation:
            step["formula_calculation"] = formula_calculation
        self.steps.append(step)
        self.counter += 1


# ---------------------------------------------------------------------------
# ★★★ Главная функция-роутер ★★★
# ---------------------------------------------------------------------------

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Главный роутер для подтипа mixed_fractions (task 6).

    Работает строго по pattern из БД:
    - pattern == "mixed_types_operations"  → _solve_mixed_types(...)
    - pattern == "fraction_structure"      → _solve_fraction_structure(...)
    """
    pattern = task_data.get("pattern")
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    # На всякий случай берём превью из text, если meta.source_expression нет
    expression_preview = (
        task_data.get("meta", {}).get("source_expression")
        or (expression_tree or {}).get("text", "")
        or ""
    )

    if not pattern or not expression_tree:
        raise ValueError("Отсутствует pattern или expression_tree.")

    builder = StepBuilder()

    # INITIAL_EXPRESSION добавляем только для mixed_types_operations.
    # Для fraction_structure первый шаг делает сам _solve_fraction_structure.
    if pattern != "fraction_structure":
        builder.add(
            description_key="INITIAL_EXPRESSION",
            description_params={"expression": expression_preview},
        )

    if pattern == "mixed_types_operations":
        # Решаем через обыкновенные дроби
        fraction_result = _solve_mixed_types(expression_tree, builder)

        # Если в итоге получилась дробь с знаменателем != 1 — переводим в десятичную
        if fraction_result.denominator != 1:
            decimal_result = _fraction_to_decimal(fraction_result)
            decimal_display = _format_decimal(decimal_result)
            builder.add(
                description_key="CONVERT_TO_DECIMAL",
                description_params={
                    "num": fraction_result.numerator,
                    "den": fraction_result.denominator,
                    "decimal": decimal_display,
                },
                formula_calculation=(
                    f"<b>{fraction_result.numerator}/"
                    f"{fraction_result.denominator} = {decimal_display}</b>"
                ),
            )
            result = decimal_result
        else:
            result = Decimal(fraction_result.numerator)

        # ---------------------------------------------------------
        # Определяем порядок действий (для идеи решения)
        # ---------------------------------------------------------
        order_info = _get_operation_order(expression_tree)

        first_node = order_info["first_op_node"]
        second_op = expression_tree.get("operation")

        # Безопасно извлекаем операцию из first_node
        first_op = first_node.get("operation", second_op)

        op_map = {
            "add": "сложение",
            "subtract": "вычитание",
            "multiply": "умножение",
            "divide": "деление",
        }

        first_text = op_map.get(first_op, first_op)
        second_text = op_map.get(second_op, second_op)

        idea_key = "MIXED_FRACTIONS_IDEA"
        idea_params = {"first": first_text, "second": second_text}
        hints = ["HINT_MIXED_ORDER_AND_CONVERSION"]

    elif pattern == "fraction_structure":
        # Аккуратное деление с вычислением числителя/знаменателя в десятичных
        result = _solve_fraction_structure(expression_tree, builder)
        idea_key = "DF_FRACTION_STRUCT_IDEA"
        idea_params = {}
        hints = ["HINT_ORDER_OF_OPERATIONS"]

    else:
        raise ValueError(f"Неизвестный паттерн: {pattern}")

    # --- Финальное форматирование ответа ---
    if isinstance(result, Fraction):
        final_display_value = _format_answer(result)
        result_float = float(result)
    elif isinstance(result, Decimal):
        final_display_value = _format_decimal(result)
        result_float = float(result)
    else:
        final_display_value = str(result)
        result_float = float(result)

    return {
        "question_id": task_data.get("id"),
        "question_group": "TASK6_MIXED",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": idea_params,
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": result_float,
            "value_display": final_display_value,
        },
        "hints_keys": hints,
    }


# ---------------------------------------------------------------------------
# ★★★ Обработчик для `mixed_types_operations` (всё приводим к дробям) ★★★
# ---------------------------------------------------------------------------

def _solve_mixed_types(expression_tree: Dict[str, Any], builder: StepBuilder) -> Fraction:
    """
    Решает пример, конвертируя все числа в обыкновенные дроби.
    Шаг 2: единый шаг с формулами конвертации.
    Далее — рекурсивное вычисление выражения.
    """

    # --- Шаг 2: конвертация всех чисел ---
    conversion_formulas: List[str] = []
    _collect_conversion_formulas(expression_tree, conversion_formulas)

    if conversion_formulas:
        builder.add(
            description_key="MIXED_CONVERT_ALL",
            description_params={
                "formulas": "\n".join([f"➡️ <b>{f}</b>" for f in conversion_formulas])
            },
        )

    # --- Последующие шаги: рекурсивное вычисление выражения ---
    return _evaluate_fraction_expression(expression_tree, builder)


# ---------------------------------------------------------------------------
# ★★★ Обработчик для `fraction_structure` (работаем в десятичных) ★★★
# ---------------------------------------------------------------------------

def _solve_fraction_structure(
    expression_tree: Dict[str, Any],
    builder: StepBuilder,
) -> Decimal:
    """
    Примеры вида:
      - a / (b ± c)
      - (a ± b) / c
      - a / b

    Работаем в десятичных дробях (Decimal), шаги строго по ФИПИ:
    1) показываем исходную дробь;
    2) считаем ту часть, где есть действие (числитель или знаменатель);
    3) выполняем деление.
    """
    # --- Разбор узлов числителя и знаменателя ---
    num_node = expression_tree["operands"][0]  # числитель
    den_node = expression_tree["operands"][1]  # знаменатель

    num_text = num_node.get("text", "")
    den_text = den_node.get("text", "")

    # Если знаменатель — выражение с операцией, красиво оборачиваем в скобки
    if isinstance(den_node, dict) and "operation" in den_node:
        den_text_display = f"({den_text})"
    else:
        den_text_display = den_text

    formatted_expr = f"{num_text} / {den_text_display}"

    # 🔹 Шаг 1 — исходная дробь
    builder.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": formatted_expr},
    )

    # --- Вспомогательная функция: вычисляет значение узла как Decimal ---
    def _node_to_decimal_local(node: Dict[str, Any]) -> Decimal:
        node_type = node.get("type")

        if node_type in ("decimal", "integer"):
            return Decimal(str(node["value"]).replace(",", "."))

        if "operation" in node:
            left_val = _node_to_decimal_local(node["operands"][0])
            right_val = _node_to_decimal_local(node["operands"][1])
            op = node["operation"]

            if op == "add":
                return left_val + right_val
            if op == "subtract":
                return left_val - right_val
            if op == "multiply":
                return left_val * right_val
            if op == "divide":
                if right_val == Decimal(0):
                    builder.add(description_key="ERROR_DIVISION_BY_ZERO")
                    return Decimal("inf")
                return left_val / right_val

        raise ValueError(f"Неизвестный узел в fraction_structure: {node}")

    # ---------------------------------------------------------
    # 1) СКОБКИ В ЧИСЛИТЕЛЕ: (a ◦ b) / c
    # ---------------------------------------------------------
    if (
        isinstance(num_node, dict)
        and "operation" in num_node
        and not ("operation" in den_node)
    ):
        op = num_node["operation"]
        left_node = num_node["operands"][0]
        right_node = num_node["operands"][1]

        left_text = left_node["text"]
        right_text = right_node["text"]

        left_val = _node_to_decimal_local(left_node)
        right_val = _node_to_decimal_local(right_node)

        if op == "add":
            num_result = left_val + right_val
            op_rus = "сложение"
            op_symbol = "+"
        elif op == "subtract":
            num_result = left_val - right_val
            op_rus = "вычитание"
            op_symbol = "−"
        elif op == "multiply":
            num_result = left_val * right_val
            op_rus = "умножение"
            op_symbol = "·"
        else:
            # Деления в числителе в наших паттернах нет, но на всякий случай:
            if right_val == Decimal(0):
                builder.add(description_key="ERROR_DIVISION_BY_ZERO")
                return Decimal("inf")
            num_result = left_val / right_val
            op_rus = "деление"
            op_symbol = ":"

        # 🔹 Шаг 2 — считаем числитель
        builder.add(
            description_key="DECIMAL_OPERATION_IN_PART",
            description_params={
                "part": "числитель",
                "operation": op_rus,
                "left": left_text,
                "right": right_text,
                "result": _format_decimal(num_result),
            },
            formula_calculation=(
                f"{left_text} {op_symbol} {right_text} = "
                f"{_format_decimal(num_result)}"
            ),
        )

        # Знаменатель считаем молча
        den_val = _node_to_decimal_local(den_node)
        if den_val == Decimal(0):
            builder.add(description_key="ERROR_DIVISION_BY_ZERO")
            return Decimal("inf")

        result = num_result / den_val

        # 🔹 Шаг 3 — финальное деление
        builder.add(
            description_key="DECIMAL_FINAL_DIVISION",
            description_params={
                "left": _format_decimal(num_result),
                "right": den_node.get("text", den_text),
                "result": _format_decimal(result),
            },
            formula_calculation="",
        )

        return result

    # ---------------------------------------------------------
    # 2) СКОБКИ В ЗНАМЕНАТЕЛЕ: a / (b ◦ c)
    # ---------------------------------------------------------
    if isinstance(den_node, dict) and "operation" in den_node:
        op = den_node["operation"]
        left_node = den_node["operands"][0]
        right_node = den_node["operands"][1]

        left_text = left_node["text"]
        right_text = right_node["text"]

        left_val = _node_to_decimal_local(left_node)
        right_val = _node_to_decimal_local(right_node)

        if op == "add":
            den_result = left_val + right_val
            op_symbol = "+"
        elif op == "subtract":
            den_result = left_val - right_val
            op_symbol = "−"
        elif op == "multiply":
            den_result = left_val * right_val
            op_symbol = "·"
        else:  # деление в знаменателе
            if right_val == Decimal(0):
                builder.add(description_key="ERROR_DIVISION_BY_ZERO")
                return Decimal("inf")
            den_result = left_val / right_val
            op_symbol = ":"

        # 🔹 Шаг 2 — считаем знаменатель
        builder.add(
            description_key="DECIMAL_IN_DENOMINATOR",
            description_params={
                "left": left_text,
                "right": right_text,
                "op_symbol": op_symbol,
                "result": _format_decimal(den_result),
            },
            formula_calculation="",
        )

        num_val = _node_to_decimal_local(num_node)

        if den_result == Decimal(0):
            builder.add(description_key="ERROR_DIVISION_BY_ZERO")
            return Decimal("inf")

        result = num_val / den_result

        # 🔹 Шаг 3 — финальное деление
        builder.add(
            description_key="DECIMAL_FINAL_DIVISION",
            description_params={
                "left": num_node.get("text", num_text),
                "right": _format_decimal(den_result),
                "result": _format_decimal(result),
            },
            formula_calculation="",
        )

        return result

    # ---------------------------------------------------------
    # 3) ПРОСТОЕ ДЕЛЕНИЕ: a / b
    # ---------------------------------------------------------
    num_val = _node_to_decimal_local(num_node)
    den_val = _node_to_decimal_local(den_node)

    if den_val == Decimal(0):
        builder.add(description_key="ERROR_DIVISION_BY_ZERO")
        return Decimal("inf")

    result = num_val / den_val

    builder.add(
        description_key="DECIMAL_FINAL_DIVISION",
        description_params={
            "left": num_text,
            "right": den_text,
            "result": _format_decimal(result),
        },
        formula_calculation="",
    )

    return result


# ---------------------------------------------------------------------------
# ★★★ Вспомогательные утилиты ★★★
# ---------------------------------------------------------------------------

def _collect_conversion_formulas(node: Dict[str, Any], formulas: List[str]) -> None:
    """
    Рекурсивно собирает формулы конвертации в обучающем виде.

    Требование ФИПИ:
    - положительные десятичные: 4,8 = 4 + 8/10 = 48/10 = 24/5
    - отрицательные: -8,2 = -(8 + 2/10) = -82/10 = -41/5
    """
    node_type = node.get("type")

    # --- Десятичные дроби ---
    if node_type == "decimal":
        text = node["text"]  # например "-8,2" или "4,8"
        txt = text.strip()

        # Определяем знак
        has_minus = txt.startswith("-") or txt.startswith("−")
        abs_txt = txt.lstrip("−-")

        parts = abs_txt.split(",")

        if len(parts) == 2 and parts[1].strip("0"):
            whole_str = parts[0] or "0"
            frac_str = parts[1]
            den_int = 10 ** len(frac_str)

            whole = int(whole_str)
            num = int(frac_str)

            base_num = whole * den_int + num  # всегда положительный для формулы

            if has_minus:
                # Пример: -8,2 = -(8 + 2/10) = -82/10 = -41/5
                reduced = _reduce_fraction_str(-base_num, den_int)
                formula = (
                    f"{text} = -({abs(whole)} + {frac_str}/{den_int}) = "
                    f"-({base_num}/{den_int}) = {reduced}"
                )
            else:
                # Пример: 4,8 = 4 + 8/10 = 48/10 = 24/5
                reduced = _reduce_fraction_str(base_num, den_int)
                formula = (
                    f"{text} = {whole} + {frac_str}/{den_int} = "
                    f"{base_num}/{den_int} = {reduced}"
                )
        else:
            # На всякий случай fallback через Fraction
            frac = Fraction(str(node["value"]).replace(",", "."))
            formula = f"{text} = {frac.numerator}/{frac.denominator}"

        formulas.append(formula)

    # --- Смешанные дроби ---
    elif node_type == "mixed":
        w, n, d = node["whole"], node["num"], node["den"]
        # Пример: 4 2/3 = ((4 ⋅ 3) + 2) / 3 = 14/3
        formula = (
            f"{w} {n}/{d} = (({w} ⋅ {d}) + {n}) / {d} = {w * d + n}/{d}"
        )
        formulas.append(formula)

    # Рекурсивно обходим поддеревья
    for operand in node.get("operands", []):
        if isinstance(operand, dict):
            _collect_conversion_formulas(operand, formulas)


def _reduce_fraction_str(num: int, den: int) -> str:
    """Возвращает строку несократимой дроби (сокращает, если возможно)."""
    g = gcd(num, den)
    if g != 1:
        num //= g
        den //= g
    if den == 1:
        return str(num)
    return f"{num}/{den}"


def _evaluate_fraction_expression(node: Dict[str, Any], builder: StepBuilder) -> Fraction:
    """Рекурсивно вычисляет expression_tree любого уровня вложенности."""
    if node.get("type"):
        return _node_to_fraction(node)

    op = node.get("operation")
    operands = node.get("operands", [])

    if not op or len(operands) != 2:
        raise ValueError(f"Некорректный узел для вычисления дробей: {node}")

    left_val = _evaluate_fraction_expression(operands[0], builder)
    right_val = _evaluate_fraction_expression(operands[1], builder)

    return _perform_fraction_op(left_val, right_val, builder, op)


def _node_to_fraction(node: Dict[str, Any]) -> Fraction:
    """Безопасно конвертирует узел (включая вложенные операции) в Fraction."""
    ntype = node.get("type")

    # --- Базовые типы ---
    if ntype == "integer":
        return Fraction(node["value"])
    if ntype == "decimal":
        return Fraction(str(node["value"]).replace(",", "."))
    if ntype == "mixed":
        return Fraction(node["whole"] * node["den"] + node["num"], node["den"])

    # --- Если это подвыражение ---
    if "operation" in node:
        op = node["operation"]
        left = _node_to_fraction(node["operands"][0])
        right = _node_to_fraction(node["operands"][1])

        if op == "add":
            return left + right
        elif op == "subtract":
            return left - right
        elif op == "multiply":
            return left * right
        elif op == "divide":
            return left / right
        else:
            raise ValueError(f"Неизвестная операция: {op}")

    raise ValueError(f"Неизвестный тип узла для Fraction: {node}")


def _node_to_decimal(node: Dict[str, Any]) -> Decimal:
    """Просто конвертирует узел в Decimal (глобальная утилита, если понадобится)."""
    ntype = node.get("type")
    if ntype in ("integer", "decimal"):
        return Decimal(str(node["value"]).replace(",", "."))
    raise ValueError(f"Неизвестный тип узла для Decimal: {node}")


def _get_operation_order(tree: Dict[str, Any]) -> Dict[str, Any]:
    """Определяет порядок операций (для 'идея решения')."""
    left, right = tree["operands"]
    if left.get("operation") in ("multiply", "divide"):
        return {
            "first_op_node": left,
            "second_op_value": _node_to_fraction(right),
        }
    else:
        return {
            "first_op_node": right,
            "second_op_value": _node_to_fraction(left),
        }


def _perform_fraction_op(
    left: Fraction,
    right: Fraction,
    builder: StepBuilder,
    op: str,
) -> Fraction:
    """Выполняет операцию с дробями и добавляет обучающий шаг."""

    if op == "add":
        result, key = left + right, "MIXED_ADD"

    elif op == "subtract":
        result, key = left - right, "MIXED_SUBTRACT"

        # Общий знаменатель для обучающего шага
        common_den = (
            left.denominator * right.denominator
            // gcd(left.denominator, right.denominator)
        )
        left_common = Fraction(
            left.numerator * (common_den // left.denominator), common_den
        )
        right_common = Fraction(
            right.numerator * (common_den // right.denominator), common_den
        )

        builder.add(
            description_key=key,
            description_params={
                "left": _format_answer(left),
                "right": _format_answer(right),
                "left_common": _format_answer(left_common),
                "right_common": _format_answer(right_common),
                "result": _format_answer(result),
            },
            formula_calculation="",
        )

        return result  # ВЫХОДИМ, чтобы не добавить второй шаг

    elif op == "multiply":
        result, key = left * right, "MIXED_MULTIPLY"

    elif op == "divide":
        result, key = left / right, "MIXED_DIVIDE"

    else:
        raise ValueError(f"Неизвестная операция с дробями: {op}")

    # Для add/multiply/divide — обычный шаг
    builder.add(
        description_key=key,
        formula_calculation=(
            f"{_format_answer(left)} {_op_symbol(op)} "
            f"{_format_answer(right)} = {_format_answer(result)}"
        ),
        description_params={
            "left": _format_answer(left),
            "right": _format_answer(right),
            "flipped": f"{right.denominator}/{right.numerator}",
            "left_num": left.numerator,
            "left_den": left.denominator,
            "right_num": right.numerator,
            "right_den": right.denominator,
            "result": _format_answer(result),
        },
    )

    return result


def _op_symbol(op: str) -> str:
    """Возвращает знак операции по ключу."""
    return {
        "add": "+",
        "subtract": "-",
        "multiply": "·",
        "divide": ":",
    }.get(op, "?")


def _fraction_to_decimal(value: Fraction) -> Decimal:
    """Конвертирует Fraction в Decimal без потери точности для наших задач."""
    return Decimal(value.numerator) / Decimal(value.denominator)


def _format_answer(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _format_decimal(value: Decimal) -> str:
    # Целые показываем без запятой
    if value == value.to_integral_value():
        return str(int(value))
    # Десятичные с запятой
    return f"{value.normalize():g}".replace(".", ",")
