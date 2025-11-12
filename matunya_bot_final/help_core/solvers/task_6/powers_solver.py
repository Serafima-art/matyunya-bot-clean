"""
НОВЫЙ, ПРОСТОЙ решатель для подтипа `powers`.
Архитектура: Линейная, предсказуемая, без сложной рекурсии.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal # <--- ДОБАВИТЬ ЭТУ СТРОКУ
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple
import math

# ---------------------------------------------------------------------------
# ★★★ Класс StepBuilder (остается без изменений, он идеален) ★★★
# ---------------------------------------------------------------------------
from dataclasses import dataclass, field

@dataclass
class StepBuilder:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1

    def add(self, description_key: str, description_params: Optional[Dict[str, Any]] = None,
            formula_calculation: Optional[str] = None):
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
    """Главный роутер. Анализирует pattern и вызывает нужный обработчик."""
    pattern = task_data.get("pattern")
    expression_tree = task_data.get("variables", {}).get("expression_tree")

    if not pattern or not expression_tree:
        raise ValueError("Отсутствует pattern или expression_tree.")

    if pattern == "powers_with_fractions":
        return _solve_powers_with_fractions(task_data, expression_tree)
    elif pattern == "powers_of_ten":
        # Логика для этого паттерна будет добавлена позже
        raise NotImplementedError("Решатель для powers_of_ten еще не реализован.")

    raise ValueError(f"Неизвестный паттерн: {pattern}")

# ---------------------------------------------------------------------------
# ★★★ Обработчик для powers_with_fractions ★★★
# ---------------------------------------------------------------------------

def _solve_powers_with_fractions(task_data: Dict[str, Any], expression_tree: Dict[str, Any]) -> Dict[str, Any]:
    """Диспетчер для powers_with_fractions. Определяет, сколько способов решения показывать."""

    expression_preview = _render_expression(expression_tree)
    # Используем "педагогический" флаг из нашего идеального валидатора
    has_common_factor = task_data.get("variables", {}).get("has_common_factor", False)

    # Пока реализуем только один, стандартный путь
    builder = StepBuilder()
    result = _solve_standard_path(expression_tree, builder, expression_preview)

    # Определяем финальную операцию для "Идеи решения"
    operation_name = "сложение" if expression_tree.get("operation") == "add" else "вычитание"

    return {
        "question_id": task_data.get("id"),
        "question_group": "TASK6_POWERS",
        "explanation_idea_key": "POWERS_FRACTIONS_STANDARD_IDEA",
        "explanation_idea_params": {"final_operation": operation_name},
        "calculation_steps": builder.steps,
        "final_answer": {
            "value_machine": float(result),
            "value_display": _format_answer(result),
        },
        "hints_keys": ["HINT_ORDER_OF_OPERATIONS", "HINT_POWER_OF_FRACTION"],
    }

# ---------------------------------------------------------------------------
# ★★★ Новый, Простой и Линейный Алгоритм ★★★
# ---------------------------------------------------------------------------

def _solve_standard_path(expression_tree: Dict[str, Any], builder: StepBuilder, expression_preview: str) -> Fraction:
    """Генерирует шаги для стандартного пути решения. ЛИНЕЙНЫЙ АЛГОРИТМ."""

    # --- Шаг 1: Обзор выражения ---
    builder.add(
        description_key="INITIAL_EXPRESSION",
        description_params={"expression": expression_preview}
    )

    # --- Извлекаем "запчасти" из дерева ---
    # ★★★ НОВАЯ УМНАЯ ФУНКЦИЯ-ПОМОЩНИК ★★★
    def _node_to_fraction(node: Dict[str, Any]) -> Fraction:
        """Рекурсивно вычисляет значение узла и возвращает Fraction."""
        if node.get("type") == "integer":
            return Fraction(node["value"])
        if node.get("type") == "common":
            return Fraction(node["value"][0], node["value"][1])
        if node.get("operation") == "divide":
            return _node_to_fraction(node["operands"][0]) / _node_to_fraction(node["operands"][1])
        # Добавьте другие операции, если они могут встретиться в основании
        return Fraction(1)

    op = expression_tree["operation"]
    left_node = expression_tree["operands"][0]
    right_node = expression_tree["operands"][1]

    # Разбираем левую часть (со степенью)
    left_coef = _node_to_fraction(left_node["operands"][0])
    power_node = left_node["operands"][1]
    base_frac = _node_to_fraction(power_node["operands"][0])
    exponent = power_node["operands"][1]["value"]

    # Разбираем правую часть
    right_coef = _node_to_fraction(right_node["operands"][0])
    right_frac = _node_to_fraction(right_node["operands"][1])

    # --- Шаг 2: Возведение в степень ---
    power_result = base_frac ** exponent
    builder.add(
        description_key="POWERS_FRACTION_POWER",
        description_params={"num": base_frac.numerator, "den": base_frac.denominator, "exponent": exponent},
        formula_calculation=f"({_format_answer(base_frac)})^{exponent} = {_format_answer(power_result)}"
    )

    # --- Шаг 3: Первое умножение ---
    left_result = left_coef * power_result
    builder.add(
        description_key="POWERS_MULTIPLY_WITH_CANCEL",
        description_params={
            "left_num": left_coef.numerator, "right_num": power_result.numerator, "right_den": power_result.denominator,
            "cancel_num": left_coef.numerator, "cancel_den": power_result.denominator, "cancel_gcd": math.gcd(left_coef.numerator, power_result.denominator)
        },
        formula_calculation=f"{_format_answer(left_coef)} · {_format_answer(power_result)} = {_format_answer(left_result)}"
    )

    # --- Шаг 4: Второе умножение ---
    right_result = right_coef * right_frac
    builder.add(
        description_key="POWERS_MULTIPLY_WITH_CANCEL",
        description_params={
            "left_num": right_coef.numerator, "right_num": right_frac.numerator, "right_den": right_frac.denominator,
            "cancel_num": right_coef.numerator, "cancel_den": right_frac.denominator, "cancel_gcd": math.gcd(right_coef.numerator, right_frac.denominator)
        },
        formula_calculation=f"{_format_answer(right_coef)} · {_format_answer(right_frac)} = {_format_answer(right_result)}"
    )

    # --- Шаг 5: Финальная операция ---
    if op == "add":
        final_result = left_result + right_result
        key = "POWERS_FINAL_ADD_INTEGERS"
    else:
        final_result = left_result - right_result
        key = "POWERS_FINAL_SUBTRACT_INTEGERS"

    builder.add(
        description_key=key,
        description_params={"left": _format_answer(left_result), "right": _format_answer(right_result), "result": _format_answer(final_result)},
        formula_calculation=f"{_format_answer(left_result)} {'+' if op == 'add' else '-'} {_format_answer(right_result)} = {_format_answer(final_result)}"
    )

    return final_result

# ---------------------------------------------------------------------------
# ★★★ Вспомогательные утилиты (простые и понятные) ★★★
# ---------------------------------------------------------------------------

def _format_answer(value: Fraction) -> str:
    """Форматирует дробь: 3/1 -> "3", 1/2 -> "1/2"."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"

def _format_decimal(value: float) -> str:
    """Форматирует float для финального ответа."""
    return f"{Decimal(str(value)):g}"

def _render_expression(node: Dict[str, Any]) -> str:
    """Простой рендер дерева в строку для Шага 1."""
    if "text" in node:
        return node["text"]

    op = node.get("operation")
    operands = node.get("operands", [])

    if op and len(operands) == 2:
        left = _render_expression(operands[0])
        right = _render_expression(operands[1])
        symbols = {"add": "+", "subtract": "-", "multiply": "·", "divide": ":", "power": "^"}

        # Добавляем скобки для степеней
        if op == "power" and "operation" in operands[0]:
            left = f"({left})"

        return f"{left} {symbols.get(op, '?')} {right}"

    return ""

def _extract_expression_from_question(task_data: Dict[str, Any]) -> Optional[str]:
    """Извлекает исходное выражение из question_text (на всякий случай)."""
    txt = task_data.get("source_expression")
    return txt if txt else None
