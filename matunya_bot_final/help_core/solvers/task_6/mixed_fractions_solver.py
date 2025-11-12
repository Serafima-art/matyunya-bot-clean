"""
ФИНАЛЬНАЯ ВЕРСИЯ: Простой, надежный решатель для 'mixed_fractions'.
Архитектура: Внутренний роутер и линейные, предсказуемые алгоритмы.
"""
from __future__ import annotations
from fractions import Fraction
from decimal import Decimal
from typing import Any, Dict, List, Optional

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
    expression_preview = task_data.get("meta", {}).get("source_expression", "")

    if not pattern or not expression_tree:
        raise ValueError("Отсутствует pattern или expression_tree.")

    builder = StepBuilder()

    builder.add(description_key="INITIAL_EXPRESSION", description_params={"expression": expression_preview})

    # Определяем, какой обработчик вызывать, и получаем результат
    if pattern == "mixed_types_operations":
        result = _solve_mixed_types(expression_tree, builder)
        idea_key = "MIXED_FRACTIONS_IDEA"
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
    """Решает пример с дробной структурой, используя рекурсивный движок."""

    # Рекурсивный движок, который сам определяет порядок действий
    def _evaluate_decimal_tree(node: Dict[str, Any], context: str = "") -> Decimal:
        node_type = node.get("type")
        if node_type in ("decimal", "integer"):
            return Decimal(str(node["value"]).replace(",", "."))

        if "operation" in node:
            op = node["operation"]

            # Сначала рекурсивно вычисляем операнды
            # Для знаменателя передаем контекст
            left_val = _evaluate_decimal_tree(node["operands"][0], context="в числителе")
            right_val = _evaluate_decimal_tree(node["operands"][1], context="в знаменателе")

            # Выполняем операцию и добавляем шаг
            return _perform_decimal_op(left_val, right_val, builder, op, context="финальное деление")

        raise ValueError(f"Неизвестный узел в fraction_structure: {node}")

    return _evaluate_decimal_tree(expression_tree)

# ---------------------------------------------------------------------------
# ★★★ Вспомогательные утилиты (простые и надежные) ★★★
# ---------------------------------------------------------------------------

def _collect_conversion_formulas(node: Dict[str, Any], formulas: List[str]):
    """Рекурсивно собирает формулы конвертации, избегая дубликатов."""
    if node.get("type") in ("decimal", "mixed"):
        formula = ""
        if node["type"] == "decimal":
            frac = Fraction(str(node["value"]).replace(",", "."))
            formula = f"{node['text']} = {frac.numerator}/{frac.denominator}"
        elif node["type"] == "mixed":
            w, n, d = node["whole"], node["num"], node["den"]
            formula = f"{node['text']} = {w*d+n}/{d}"
        if formula and formula not in formulas:
            formulas.append(formula)

    for operand in node.get("operands", []):
        _collect_conversion_formulas(operand, formulas)

def _node_to_fraction(node: Dict[str, Any]) -> Fraction:
    """Просто конвертирует узел в Fraction без добавления шагов."""
    ntype = node.get("type")
    if ntype == "integer": return Fraction(node["value"])
    if ntype == "decimal": return Fraction(str(node["value"]).replace(",", "."))
    if ntype == "mixed": return Fraction(node["whole"] * node["den"] + node["num"], node["den"])
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
    """Выполняет операцию с дробями и добавляет шаг."""
    if op == "add": result, key, symbol = left + right, "MIXED_ADD", "+"
    elif op == "subtract": result, key, symbol = left - right, "MIXED_SUBTRACT", "-"
    elif op == "multiply": result, key, symbol = left * right, "MIXED_MULTIPLY", "·"
    elif op == "divide": result, key, symbol = left / right, "MIXED_DIVIDE", ":"
    else: raise ValueError(f"Неизвестная операция с дробями: {op}")

    formula = f"{_format_answer(left)} {symbol} {_format_answer(right)} = {_format_answer(result)}"
    builder.add(description_key=key, formula_calculation=formula)
    return result

def _perform_decimal_op(left: Decimal, right: Decimal, builder: StepBuilder, op: str, context: str) -> Decimal:
    """Выполняет операцию с Decimal и добавляет шаг."""
    key_map = { "add": "ADD", "subtract": "SUBTRACT", "multiply": "MULTIPLY", "divide": "DIVIDE" }
    symbol_map = { "add": "+", "subtract": "-", "multiply": "·", "divide": ":" }

    if op not in key_map: raise ValueError(f"Неизвестная операция с Decimal: {op}")

    if op == "divide" and right == Decimal(0):
        builder.add(description_key="ERROR_DIVISION_BY_ZERO")
        return Decimal('inf')

    result = left + right if op == "add" else left - right if op == "subtract" else left * right if op == "multiply" else left / right

    key = f"DECIMAL_{key_map[op]}_CONTEXT" # Ключ будет вида "DECIMAL_SUBTRACT_CONTEXT"
    formula = f"{_format_decimal(left)} {symbol_map[op]} {_format_decimal(right)} = {_format_decimal(result)}"
    builder.add(description_key=key, description_params={"context": context}, formula_calculation=formula)
    return result

def _format_answer(value: Fraction) -> str:
    if value.denominator == 1: return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"

def _format_decimal(value: Decimal) -> str:
    if value == value.to_integral_value(): return str(int(value))
    return f"{value.normalize():g}".replace(".", ",")
