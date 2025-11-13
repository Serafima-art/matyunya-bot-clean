"""
ФИНАЛЬНАЯ ВЕРСИЯ: Простой, надежный решатель для 'mixed_fractions'.
Архитектура: Внутренний роутер и линейные, предсказуемые алгоритмы.
"""
from __future__ import annotations
from fractions import Fraction
from decimal import Decimal
from typing import Any, Dict, List, Optional
from math import gcd

# ---------------------------------------------------------------------------
# ★★★ Класс StepBuilder (стандартный) ★★★
# ---------------------------------------------------------------------------
from dataclasses import dataclass, field

@dataclass
class StepBuilder:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1

    def add(self, description_key: str, description_params: Optional[Dict[str, Any]] = None,
            formula_calculation: Optional[str] = None):
        step = { "step_number": self.counter, "description_key": description_key, "description_params": description_params or {} }
        if formula_calculation:
            step["formula_calculation"] = formula_calculation
        self.steps.append(step)
        self.counter += 1

# ---------------------------------------------------------------------------
# ★★★ Главная функция-роутер ★★★
# ---------------------------------------------------------------------------

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Главный роутер. Анализирует pattern и вызывает нужный обработчик."""
    pattern = task_data.get("pattern")
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    expression_preview = (
        task_data.get("variables", {})
        .get("expression_tree", {})
        .get("text", "")
        .strip()
    )

    if not pattern or not expression_tree:
        raise ValueError("Отсутствует pattern или expression_tree.")

    builder = StepBuilder()

    builder.add(description_key="INITIAL_EXPRESSION", description_params={"expression": expression_preview})

    # Определяем, какой обработчик вызывать, и получаем результат
    if pattern == "mixed_types_operations":
        result = _solve_mixed_types(expression_tree, builder)
        # определяем точный порядок действий
        first_op = _get_operation_order(expression_tree)["first_op_node"]["operation"]
        second_op = expression_tree["operation"]

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
        result = _solve_fraction_structure(expression_tree, builder)
        idea_key = "DF_FRACTION_STRUCT_IDEA"
        hints = ["HINT_ORDER_OF_OPERATIONS"]
    else:
        raise ValueError(f"Неизвестный паттерн: {pattern}")

    # ★★★ НОВАЯ УМНАЯ ЛОГИКА ФОРМАТИРОВАНИЯ ОТВЕТА ★★★
    # Проверяем тип результата и вызываем соответствующий форматтер
    if isinstance(result, Fraction):
        final_display_value = _format_answer(result)
        # Конвертируем в float для value_machine
        result_float = float(result)
    elif isinstance(result, Decimal):
        final_display_value = _format_decimal(result)
        result_float = float(result)
    else:
        # На всякий случай, если результат пришел в другом формате
        final_display_value = str(result)
        result_float = float(result)

    # Собираем финальный solution_core
    return {
        "question_id": task_data.get("id"),
        "question_group": "TASK6_MIXED",
        "explanation_idea_key": idea_key,
        "explanation_idea_params": locals().get("idea_params", {}),
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": result_float,
            "value_display": final_display_value,
        },
        "hints_keys": hints,
    }

# ---------------------------------------------------------------------------
# ★★★ Обработчик для `mixed_types_operations` (Стратегия: всё в дроби) ★★★
# ---------------------------------------------------------------------------

def _solve_mixed_types(expression_tree: Dict[str, Any], builder: StepBuilder) -> Fraction:
    """Решает пример, конвертируя все числа в обыкновенные дроби."""

    # --- Шаг 2: Конвертация ---
    conversion_formulas = []
    _collect_conversion_formulas(expression_tree, conversion_formulas)
    builder.add(
        description_key="MIXED_CONVERT_ALL",
        description_params={"formulas": "\n".join([f"➡️ <b>{f}</b>" for f in conversion_formulas])}
    )

    # --- Шаг 3: Первое действие (умножение/деление) ---
    op_order = _get_operation_order(expression_tree)
    first_op_node = op_order["first_op_node"]

    left_frac = _node_to_fraction(first_op_node["operands"][0])
    right_frac = _node_to_fraction(first_op_node["operands"][1])
    first_op_result = _perform_fraction_op(left_frac, right_frac, builder, first_op_node["operation"])

    # --- Шаг 4: Второе действие (сложение/вычитание) ---
    second_op_val = op_order["second_op_value"]

    # Определяем порядок для финальной операции
    final_op = expression_tree["operation"]

    if expression_tree["operands"][0] == first_op_node:
        # Случай: (A op B) op C
        final_result = _perform_fraction_op(first_op_result, second_op_val, builder, final_op)
    else:
        # Случай: C op (A op B)
        final_result = _perform_fraction_op(second_op_val, first_op_result, builder, final_op)

    return final_result

# ---------------------------------------------------------------------------
# ★★★ Обработчик для `fraction_structure` (Стратегия: решаем в десятичных) ★★★
# ---------------------------------------------------------------------------

def _solve_fraction_structure(expression_tree: Dict[str, Any], builder: StepBuilder) -> Decimal:
    """Решает пример вида a / (b - c), a / (b + c), a / (b * c), a / (b : c) — пошагово."""

    # -----------------------
    # ШАГ 1. Исходное выражение
    # -----------------------
    expr_text = expression_tree.get("text") or ""
    builder.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": expr_text}
    )

    # -----------------------
    # Рекурсивный движок
    # -----------------------
    def _evaluate_decimal_tree(node: Dict[str, Any], context: str = "") -> Decimal:
        """Рекурсивно вычисляет decimal-дерево и создаёт шаги для знаменателя."""

        node_type = node.get("type")

        # Числовой литерал
        if node_type in ("decimal", "integer"):
            return Decimal(str(node["value"]).replace(",", "."))

        # Операция (+, -, *, /)
        if "operation" in node:
            op = node["operation"]
            left_node = node["operands"][0]
            right_node = node["operands"][1]

            # --- ШАГ 2: если мы в знаменателе — формируем отдельный шаг ---
            if context == "в знаменателе":
                left_text = left_node["text"]
                right_text = right_node["text"]

                # вычисляем числовое значение операндов
                left_value = _evaluate_decimal_tree(left_node, context="в знаменателе")
                right_value = _evaluate_decimal_tree(right_node, context="в знаменателе")

                # вычисляем результат операции
                if op == "add":
                    denom_result = left_value + right_value
                    op_symbol = "+"
                elif op == "subtract":
                    denom_result = left_value - right_value
                    op_symbol = "−"
                elif op == "multiply":
                    denom_result = left_value * right_value
                    op_symbol = "·"
                else:
                    denom_result = left_value / right_value
                    op_symbol = ":"

                # добавляем шаг
                builder.add(
                    description_key="DECIMAL_IN_DENOMINATOR",
                    description_params={
                        "left": left_text,
                        "right": right_text,
                        "op_symbol": op_symbol,
                        "result": _format_decimal(denom_result),
                    },
                    formula_calculation=""
                )

                # возвращаем значение — важно!
                return denom_result

            # --- Обычная рекурсия ---
            left_val = _evaluate_decimal_tree(left_node, context="в числителе")
            right_val = _evaluate_decimal_tree(right_node, context="в знаменателе")

            # Выполняем операцию (и добавляем шаги)
            result = _perform_decimal_op(left_val, right_val, builder, op, context)
            return result

        raise ValueError(f"Неизвестный узел в fraction_structure: {node}")

    # -----------------------
    # Основной расчёт
    # -----------------------
    result = _evaluate_decimal_tree(expression_tree)

    # -----------------------
    # ШАГ 3. Финальное деление
    # -----------------------
    left_text = expression_tree["operands"][0]["text"]
    right_text = expression_tree["operands"][1]["text"]
    result_disp = _format_decimal(result)

    builder.add(
        description_key="DECIMAL_FINAL_DIVISION",
        formula_calculation=f"{left_text} / ({right_text}) = {result_disp}"
    )

    return result

# ---------------------------------------------------------------------------
# ★★★ Вспомогательные утилиты (простые и надежные) ★★★
# ---------------------------------------------------------------------------

def _collect_conversion_formulas(node: Dict[str, Any], formulas: List[str]):
    """Рекурсивно собирает формулы конвертации в обучающем виде."""

    if node.get("type") == "decimal":
        text = node["text"]
        # 4,8 → 4 целых и 8/10
        parts = text.split(",")
        if len(parts) == 2 and parts[1].strip("0"):
            whole = parts[0]
            frac_len = len(parts[1])
            num = parts[1]
            den = "1" + "0" * frac_len
            formula = (
                f"{text} = {whole} {num}/{den} = (({whole} ⋅ {den}) + {num}) / {den} "
                f"= {int(whole)*int(den)+int(num)}/{den} = {_reduce_fraction_str(int(whole)*int(den)+int(num), int(den))}"
            )
        else:
            # если что-то не разобралось — упрощённо
            frac = Fraction(str(node["value"]).replace(",", "."))
            formula = f"{text} = {frac.numerator}/{frac.denominator}"

        formulas.append(formula)

    elif node.get("type") == "mixed":
        w, n, d = node["whole"], node["num"], node["den"]
        formula = (
            f"{w} {n}/{d} = (({w} ⋅ {d}) + {n}) / {d} = {w*d+n}/{d}"
        )
        formulas.append(formula)

    # рекурсивно обходим поддеревья
    for operand in node.get("operands", []):
        _collect_conversion_formulas(operand, formulas)

def _reduce_fraction_str(num: int, den: int) -> str:
    """Возвращает строку несократимой дроби, если можно — сокращает."""
    from math import gcd
    g = gcd(num, den)
    if g != 1:
        num //= g
        den //= g
    if den == 1:
        return str(num)
    return f"{num}/{den}"

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
    """Просто конвертирует узел в Decimal."""
    ntype = node.get("type")
    if ntype in ("integer", "decimal"): return Decimal(str(node["value"]).replace(",", "."))
    raise ValueError(f"Неизвестный тип узла для Decimal: {node}")

def _get_operation_order(tree: Dict[str, Any]) -> Dict:
    """Определяет порядок операций и СРАЗУ ВЫЧИСЛЯЕТ ЗНАЧЕНИЯ."""
    left, right = tree["operands"]
    if left.get("operation") in ("multiply", "divide"):
        return {
            "first_op_node": left,
            "second_op_value": _node_to_fraction(right)
        }
    else:
        return {
            "first_op_node": right,
            "second_op_value": _node_to_fraction(left)
        }

def _perform_fraction_op(left: Fraction, right: Fraction, builder: StepBuilder, op: str) -> Fraction:
    """Выполняет операцию с дробями и добавляет обучающий шаг."""

    if op == "add":
        result, key = left + right, "MIXED_ADD"

    elif op == "subtract":
        result, key = left - right, "MIXED_SUBTRACT"

        # общий знаменатель
        common_den = left.denominator * right.denominator // gcd(left.denominator, right.denominator)
        left_common = Fraction(left.numerator * (common_den // left.denominator), common_den)
        right_common = Fraction(right.numerator * (common_den // right.denominator), common_den)

        builder.add(
            description_key=key,
            description_params={
                "left": _format_answer(left),
                "right": _format_answer(right),
                "left_common": _format_answer(left_common),
                "right_common": _format_answer(right_common),
                "result": _format_answer(result),
            },
            formula_calculation=""
        )

        return result   # 🔥 ВАЖНО: ВЫХОДИМ, чтобы не добавить второй шаг

    elif op == "multiply":
        result, key = left * right, "MIXED_MULTIPLY"

    elif op == "divide":
        result, key = left / right, "MIXED_DIVIDE"

    else:
        raise ValueError(f"Неизвестная операция с дробями: {op}")

    # Для add/multiply/divide — обычный шаг
    builder.add(
        description_key=key,
        formula_calculation=f"{_format_answer(left)} {_op_symbol(op)} {_format_answer(right)} = {_format_answer(result)}",
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
    return { "add": "+", "subtract": "-", "multiply": "·", "divide": ":" }.get(op, "?")


def _perform_decimal_op(left: Decimal, right: Decimal, builder: StepBuilder, op: str, context: str) -> Decimal:
    """Выполняет операцию с Decimal и добавляет обучающий шаг."""

    # Защита от нуля
    if op == "divide" and right == Decimal(0):
        builder.add(description_key="ERROR_DIVISION_BY_ZERO")
        return Decimal("inf")

    # Выполняем саму операцию
    result = (
        left + right if op == "add" else
        left - right if op == "subtract" else
        left * right if op == "multiply" else
        left / right
    )

    # Определяем подходящий шаблон
    if op == "add":
        if left >= 0 and right >= 0:
            key = "DECIMAL_ADD_BOTH_POSITIVE"
        elif left < 0 and right < 0:
            key = "DECIMAL_ADD_BOTH_NEGATIVE"
        else:
            key = "DECIMAL_ADD_MIXED_SIGNS"

    elif op == "subtract":
        if right >= 0:
            key = "DECIMAL_SUBTRACT_POSITIVE"
        else:
            key = "DECIMAL_SUBTRACT_NEGATIVE"

    elif op == "multiply":
        if left >= 0 and right >= 0:
            key = "DECIMAL_MULTIPLY_BOTH_POSITIVE"
        elif left < 0 and right < 0:
            key = "DECIMAL_MULTIPLY_BOTH_NEGATIVE"
        else:
            key = "DECIMAL_MULTIPLY_MIXED_SIGNS"

    elif op == "divide":
        if left >= 0 and right >= 0:
            key = "DECIMAL_DIVIDE_BOTH_POSITIVE"
        elif left < 0 and right < 0:
            key = "DECIMAL_DIVIDE_BOTH_NEGATIVE"
        else:
            key = "DECIMAL_DIVIDE_MIXED_SIGNS"

    # Формула
    symbol = "+" if op == "add" else "-" if op == "subtract" else "·" if op == "multiply" else ":"
    formula = f"{_format_decimal(left)} {symbol} {_format_decimal(right)} = {_format_decimal(result)}"

    # Добавляем полноценный шаг
    builder.add(
        description_key=key,
        formula_calculation=formula,
        description_params={
            "left": _format_decimal(left),
            "right": _format_decimal(right),
            "result": _format_decimal(result),
            # Доп. параметры для DECIMAL_SUBTRACT_NEGATIVE:
            "converted_addend": _format_decimal(abs(right))
        }
    )

    return result

def _format_answer(value: Fraction) -> str:
    if value.denominator == 1: return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"

def _format_decimal(value: Decimal) -> str:
    if value == value.to_integral_value(): return str(int(value))
    return f"{value.normalize():g}".replace(".", ",")
