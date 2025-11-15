"""
ФИНАЛЬНАЯ, СИНХРОНИЗИРОВАННАЯ ВЕРСИЯ. Решатель для common_fractions.
Архитектура: "Умный Рекурсивный Диспетчер", говорящий на языке существующего Humanizer'а.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple
import math
import re

# ---------------------------------------------------------------------------
# Конструктор Шагов (ГОСТ-2025)
# ---------------------------------------------------------------------------
@dataclass
class StepBuilder:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    counter: int = 1

    def add(self, description_key: str, description_params: Optional[Dict[str, Any]] = None, formula_calculation: Optional[str] = None) -> None:
        step = {
            "step_number": self.counter,
            "description_key": description_key,
            "description_params": description_params or {},
        }
        if formula_calculation:
            step["formula_calculation"] = f"<b>{str(formula_calculation).strip()}</b>"
        self.steps.append(step)
        self.counter += 1

# ---------------------------------------------------------------------------
# Главная точка входа ("Дирижер")
# ---------------------------------------------------------------------------
def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    builder = StepBuilder()
    expression_tree = task_data["variables"]["expression_tree"]

    # Шаг 1: Исходное выражение
    expression_preview = _render_expression(expression_tree, task_data)
    builder.add("INITIAL_EXPRESSION", {"expression": expression_preview})

    # === ПРОХОД №1: ПОДГОТОВКА И КОНВЕРТАЦИЯ ===
    conversions = []
    cleaned_tree = _collect_conversions_and_clean_tree(expression_tree, conversions)

    for i, info in enumerate(conversions):
        key = "CONVERT_MIXED_FIRST" if i == 0 else "CONVERT_MIXED_NEXT"
        builder.add(key, {
            "mixed_text": info["mixed_text"], "whole": info["whole"], "num": info["num"], "den": info["den"],
            "result_num": info["result_num"], "result_den": info["result_den"], "ctx": ""
        }, f"{info['mixed_text']} = ({info['whole']}·{info['den']} + {info['num']})/{info['den']} = {info['result_num']}/{info['result_den']}")

    if conversions:
        cleaned_expr_str = _render_expression(cleaned_tree, {})
        builder.add("SHOW_CONVERTED_EXPRESSION", {"expression": cleaned_expr_str, "ctx": ""})

    # === ПРОХОД №2: РЕШЕНИЕ ОЧИЩЕННОГО ВЫРАЖЕНИЯ ===
    final_fraction = _evaluate_node(cleaned_tree, builder, "")

    # Финальный ответ
    answer_type = task_data.get("answer_type", "decimal")
    value_display = f"{float(final_fraction):g}".replace(".", ",") if answer_type == "decimal" else _format_fraction(final_fraction)
    #builder.add("FIND_FINAL_ANSWER", {"value": value_display})

    return {
        "question_id": task_data.get("id"), "question_group": "TASK6_COMMON",
        "explanation_idea_key": _get_idea_key(expression_tree),
        "calculation_steps": builder.steps,
        "final_answer": {"value_machine": float(final_fraction), "value_display": value_display},
        "hints_keys": _get_hints_keys(expression_tree, task_data)
    }

# ---------------------------------------------------------------------------
# Сердце Решателя: Рекурсивный Диспетчер
# ---------------------------------------------------------------------------
def _evaluate_node(node: Dict[str, Any], builder: StepBuilder, context: str) -> Fraction:
    if node.get("type") in ("common", "integer"):
        return _extract_fraction(node)

    operation = node["operation"]
    operands = node["operands"]

    child_context = context
    if not context:
        if _is_complex_fraction(node): child_context = "в числителе"
        elif _has_parentheses(node): child_context = "в скобках"

    left_val = _evaluate_node(operands[0], builder, child_context)
    right_val = _evaluate_node(operands[1], builder, child_context)

    if operation in ("add", "subtract"):
        return _explain_add_subtract_chained(left_val, right_val, operation, builder, context)
    if operation == "multiply":
        return _explain_multiply_chained(left_val, right_val, builder, context)
    if operation == "divide":
        # Используем наш старый, но теперь уместный одношаговый исполнитель
        return _explain_divide(left_val, right_val, builder, context)

    raise ValueError(f"Неизвестная операция: {operation}")

# ---------------------------------------------------------------------------
# Новые "Цепочечные" Исполнители (по твоему эталону)
# ---------------------------------------------------------------------------
def _explain_add_subtract_chained(left: Fraction, right: Fraction, op: str, builder: StepBuilder, context: str) -> Fraction:
    op_symbol = "+" if op == "add" else "−"
    result = left + right if op == "add" else left - right

    common_den = _lcm(left.denominator, right.denominator)
    left_mult = common_den // left.denominator
    right_mult = common_den // right.denominator
    left_scaled_num = left.numerator * left_mult
    right_scaled_num = right.numerator * right_mult

    formula = (
        f"{_format_fraction(left)} {op_symbol} {_format_fraction(right)} = "
        f"({left.numerator}·{left_mult})/({left.denominator}·{left_mult}) {op_symbol} ({right.numerator}·{right_mult})/({right.denominator}·{right_mult}) = "
        f"{left_scaled_num}/{common_den} {op_symbol} {right_scaled_num}/{common_den} = "
        f"{_format_fraction(result)}"
    )

    builder.add("CF_FIND_LCM",
                {"den1": left.denominator, "den2": right.denominator, "lcm": common_den, "ctx": (context + ": ") if context else ""},
                formula)
    return result

def _explain_multiply_chained(left: Fraction, right: Fraction, builder: StepBuilder, context: str) -> Fraction:
    result = left * right
    formula = f"{_format_fraction(left)} · {_format_fraction(right)} = {_format_fraction(result)}"
    builder.add("CALCULATE_MULTIPLICATION_DEFAULT",
                {"left": _format_fraction(left), "right": _format_fraction(right), "ctx": ""},
                formula)
    return result

def _explain_divide(left: Fraction, right: Fraction, builder: StepBuilder, context: str) -> Fraction:
    flipped = Fraction(right.denominator, right.numerator)
    result = left / right
    after_cancel = Fraction((left.numerator*flipped.numerator)//math.gcd(left.numerator*flipped.numerator, left.denominator*flipped.denominator), (left.denominator*flipped.denominator)//math.gcd(left.numerator*flipped.numerator, left.denominator*flipped.denominator))

    formula_parts = [f"{_format_fraction(left)} : {_format_fraction(right)}", f"{_format_fraction(left)} · {_format_fraction(flipped)}"]
    if after_cancel != result and after_cancel.denominator != 1: formula_parts.append(_format_fraction(after_cancel))
    formula_parts.append(_format_fraction(result))

    builder.add("MIXED_DIVIDE",
        {"left": _format_fraction(left), "right": _format_fraction(right), "flipped": _format_fraction(flipped),
         "left_num": left.numerator, "left_den": left.denominator, "right_num": right.numerator, "right_den": right.denominator,
         "result": _format_fraction(result), "context": (context + " ") if context else ""},
        " = ".join(formula_parts))
    return result

# ---------------------------------------------------------------------------
# Проход №1: Пре-процессор
# ---------------------------------------------------------------------------
def _collect_conversions_and_clean_tree(node: Dict, conversions: List) -> Dict:
    # Рекурсивно обходит дерево, собирает информацию о смешанных числах и возвращает новое, чистое дерево.
    is_mixed, info = _check_if_mixed(node)
    if is_mixed:
        conversions.append(info)
        return {"type": "common", "value": [info["result_num"], info["result_den"]]}

    if "operands" in node:
        cleaned_operands = [_collect_conversions_and_clean_tree(op, conversions) for op in node["operands"]]
        return {**node, "operands": cleaned_operands}

    return node # Возвращаем узел без изменений, если это простое число

# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------
def _add_final_conversion_step(task_data: Dict, builder: StepBuilder, fraction: Fraction):
    if task_data.get("answer_type") == "decimal" and fraction.denominator != 1:
        decimal_str = f"{float(fraction):g}".replace(".", ",")
        builder.add("CONVERT_TO_DECIMAL", {"num": fraction.numerator, "den": fraction.denominator, "decimal": decimal_str},
                    f"{_format_fraction(fraction)} = {decimal_str}")

def _check_if_mixed(node: Dict) -> Tuple[bool, Dict]:
    text = node.get("text", "")
    if text and " " in text and "/" in text:
        try:
            whole_str, frac_str = text.split(" ", 1)
            num_str, den_str = frac_str.split("/", 1)
            whole, num, den = int(whole_str), int(num_str), int(den_str)
            result_num = whole * den + num
            return True, {"mixed_text": text, "whole": whole, "num": num, "den": den, "result_num": result_num, "result_den": den}
        except (ValueError, TypeError): pass
    return False, {}

def _lcm(a: int, b: int) -> int: return abs(a * b) // math.gcd(a, b) if a != 0 and b != 0 else 0

def _extract_fraction(node: Dict) -> Fraction:
    if node.get("type") == "common": return Fraction(*node["value"])
    if node.get("type") == "integer": return Fraction(node["value"])
    raise ValueError(f"Не удалось извлечь дробь из: {node}")

def _format_fraction(frac: Fraction) -> str: return str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"

def _is_complex_fraction(node: Dict) -> bool: return node.get("operation") == "divide" and "operation" in node.get("operands", [{}])[0]

def _has_parentheses(node: Dict) -> bool:
    op = node.get("operation")
    if op in ("multiply", "divide"): return any("operation" in operand for operand in node.get("operands", []))
    return False

def _get_idea_key(tree: Dict) -> str:
    """
    Определяет основную идею решения, выставляя правильный приоритет:
    1. Сначала проверяем на наличие скобок.
    2. Только потом - на сложную дробь.
    """
    # ПРИОРИТЕТ №1: Если есть явные скобки, это всегда "parentheses_operations"
    if _has_parentheses(tree):
        return "PARENTHESES_OPERATIONS_IDEA"

    # ПРИОРИТЕТ №2: Если скобок нет, но это деление со сложным числителем - это "complex_fraction"
    if _is_complex_fraction(tree):
        return "COMPLEX_FRACTION_IDEA"

    # Стандартные случаи, если нет ни скобок, ни сложной структуры
    op = tree.get("operation")
    if op in ("add", "subtract"):
        return "ADD_SUB_FRACTIONS_IDEA"

    return "MULTIPLY_DIVIDE_FRACTIONS_IDEA"

def _get_hints_keys(tree: Dict, task_data: Dict) -> List[str]:
    hints = set()
    if " " in task_data.get("question_text", ""): hints.add("HINT_CONVERT_MIXED")
    if tree.get("operation") == "divide": hints.add("HINT_DIVIDE_AS_MULTIPLY")
    if tree.get("operation") == "multiply": hints.add("HINT_CROSS_CANCEL")
    if tree.get("operation") in ("add", "subtract"): hints.add("HINT_FIND_LCM")
    if not hints: hints.add("HINT_ORDER_OF_OPERATIONS")
    return list(hints)

def _render_expression(node: Dict, task_data: Dict) -> str:
    text = task_data.get("question_text", "")
    for line in text.splitlines():
        line = line.strip()
        if re.search(r'\d', line) and re.search(r'[:·/()−]', line) and not line.lower().startswith(("ответ", "вычисли", "найди")):
            return line
    return "Выражение не найдено"
