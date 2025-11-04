"""Solver for decimal_fractions (task 6, ОГЭ 2025).
Формирует решение и шаги по шаблонам ФИПИ-2025, без LaTeX, с запятыми и длинным минусом."""

from decimal import Decimal, getcontext
from typing import Any, Dict, List
from matunya_bot_final.help_core.solvers.task_6.task6_text_formatter import (
    normalize_for_display,
    fix_unary_minus_spacing,
    wrap_negative_after_plus_minus,
)

EXPLANATION_IDEA_KEY = "DECIMAL_OPERATIONS_IDEA"
DF_BRACKETS_FIRST_IDEA = "DF_BRACKETS_FIRST_IDEA"
HINT_KEYS = [
    "HINT_DECIMAL_ALIGN_POINTS",
    "HINT_DECIMAL_SIGN_RULES",
    "HINT_DECIMAL_ORDER_OF_OPERATIONS",
    "HINT_DECIMAL_SUBTRACT_NEGATIVES",
]


def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point for the decimal fractions solver."""
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    if not expression_tree:
        raise ValueError("Missing 'expression_tree' in task_data")

    # Keep numerical operations stable for chained decimal calculations.
    getcontext().prec = 10

    steps: List[Dict[str, Any]] = []
    step_counter = [1]

    # --- ФИПИ-режим: простое сложение/вычитание десятичных дробей (один шаг) ---
    if _is_simple_add_sub(expression_tree):
        op = expression_tree["operation"]
        left_raw = Decimal(str(expression_tree["operands"][0]["value"]))
        right_raw = Decimal(str(expression_tree["operands"][1]["value"]))
        result = left_raw + right_raw if op == "add" else left_raw - right_raw

        left_s = _format_decimal_ru(left_raw)
        right_s = _format_decimal_ru(right_raw)
        result_s = _format_decimal_ru(result)

        if op == "add":
            description_key = "CALCULATE_ADDITION_SIMPLE"
            formula_repr = f"{left_s} + {right_s}"
            formula_calc = f"{left_s} + {right_s} = {result_s}"
        else:
            description_key = "CALCULATE_SUBTRACTION_SIMPLE"
            formula_repr = f"{left_s} - {right_s}"
            formula_calc = f"{left_s} - {right_s} = {result_s}"

        steps.append({
            "step_number": step_counter[0],
            "description_key": description_key,
            "description_params": {"left": left_s, "right": right_s},
            "formula_representation": formula_repr,
            "formula_calculation": formula_calc,
            "calculation_result": result_s,
        })
        step_counter[0] += 1

        return {
            "question_id": task_data.get("id", "placeholder_id"),
            "question_group": "TASK6_DECIMAL",
            "explanation_idea": "",
            "explanation_idea_key": "DF_ADD_SUB_IDEA",
            "explanation_idea_params": {},
            "calculation_steps": steps,
            "final_answer": {
                "value_machine": float(result),
                "value_display": result_s,
            },
            "hints": [],
            "hints_keys": ["HINT_DECIMAL_ALIGNMENT"],
        }

    # --- иначе: общий режим (для выражений со скобками, делением, умножением и т.д.) ---
    final_result = _evaluate_tree(expression_tree, steps, step_counter)
    result_value = float(final_result)

    # 💡 Определяем идею решения автоматически
    if _has_brackets(expression_tree):
        explanation_idea_key = "DF_BRACKETS_FIRST_IDEA"
    else:
        explanation_idea_key = "DF_LINEAR_OP_IDEA"

    return {
        "question_id": task_data.get("id", "placeholder_id"),
        "question_group": "TASK6_DECIMAL",
        "explanation_idea": "",
        "explanation_idea_key": explanation_idea_key,
        "explanation_idea_params": {},
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": float(final_result),
            "value_display": _format_decimal(final_result),
        },
        "hints": [],
        "hints_keys": HINT_KEYS,
    }


def _evaluate_tree(node: Dict[str, Any], steps: List[Dict[str, Any]], step_counter: List[int]) -> Decimal:
    """Recursively evaluate the provided expression tree."""
    # Лист — десятичное число
    if node.get("type") == "decimal":
        return Decimal(str(node["value"]))

    operation = node["operation"]
    operands = node["operands"]

    # --- ФИПИ 2.3: числитель / (вычитание/сложение в знаменателе) ---
    if operation == "divide" and isinstance(operands[1], dict) and operands[1].get("operation") in ("add", "subtract"):
        # 1) Считаем числитель (без добавления особых шагов)
        left = _evaluate_tree(operands[0], steps, step_counter)

        # 2) Считаем знаменатель; последний шаг сейчас будет обычным DECIMAL_SUBTRACT_*
        before_len = len(steps)
        right = _evaluate_tree(operands[1], steps, step_counter)

        # 3) Переименовываем последний шаг вычитания в шаблон ФИПИ
        if len(steps) > before_len:
            last = steps[-1]
            if last.get("description_key") in ("DECIMAL_SUBTRACT_NEGATIVE", "DECIMAL_SUBTRACT_POSITIVE"):
                last["description_key"] = "CALCULATE_SUBTRACTION_IN_DENOMINATOR"
                # description_params у последнего шага уже содержат left/right в нужном виде
                # формулы (representation/calculation) тоже уже красивые — их не трогаем

        # 4) Финальный шаг: деление (строго по шаблону ФИПИ)
        result = left / right
        left_str = _format_decimal(left)
        right_str = _format_decimal(right)
        result_str = _format_decimal(result)

        formula_repr = normalize_for_display(f"{left_str} : {right_str}")
        formula_calc = normalize_for_display(f"{left_str} : {right_str} = {result_str}")

        step = {
            "step_number": step_counter[0],
            "description_key": "CALCULATE_DIVISION_FINAL",
            "description_params": {"left": left_str, "right": right_str},
            "formula_representation": formula_repr,
            "formula_calculation": formula_calc,
            "calculation_result": result_str,
        }
        steps.append(step)
        step_counter[0] += 1

        return result

    # --- Обычная рекурсия для остальных случаев ---
    left = _evaluate_tree(operands[0], steps, step_counter)
    right = _evaluate_tree(operands[1], steps, step_counter)
    return _perform_operation(operation, left, right, steps, step_counter)

def _perform_operation(
    operation: str,
    left: Decimal,
    right: Decimal,
    steps: List[Dict[str, Any]],
    step_counter: List[int],
) -> Decimal:
    """Dispatch arithmetic operation."""
    if operation == "add":
        return _perform_addition(left, right, steps, step_counter)
    if operation == "subtract":
        return _perform_subtraction(left, right, steps, step_counter)
    if operation == "multiply":
        return _perform_multiplication(left, right, steps, step_counter)
    if operation == "divide":
        return _perform_division(left, right, steps, step_counter)

    raise ValueError(f"Unsupported operation: {operation}")


def _perform_addition(
    left: Decimal,
    right: Decimal,
    steps: List[Dict[str, Any]],
    step_counter: List[int],
) -> Decimal:
    """Perform decimal addition and record the explanation step."""
    result = left + right

    if left >= 0 and right >= 0:
        description_key = "DECIMAL_ADD_BOTH_POSITIVE"
    elif left < 0 and right < 0:
        description_key = "DECIMAL_ADD_BOTH_NEGATIVE"
    else:
        description_key = "DECIMAL_ADD_MIXED_SIGNS"

    left_str = _format_decimal(left)
    right_str = _format_decimal(right)
    result_str = _format_decimal(result)

    description_params = {
        "left": left_str,
        "right": right_str,
        "result": result_str,
        "result_sign": _sign_label(result),
    }

    formula_repr = f"{left_str} + {right_str}"
    formula_calc = f"{left_str} + {right_str} = {result_str}"

    formula_repr = wrap_negative_after_plus_minus(fix_unary_minus_spacing(formula_repr))
    formula_calc = wrap_negative_after_plus_minus(fix_unary_minus_spacing(formula_calc))

    _append_operation_step(
        steps,
        step_counter,
        description_key,
        description_params,
        formula_repr,
        formula_calc,
        result_str,
    )
    return result


def _perform_subtraction(
    left: Decimal,
    right: Decimal,
    steps: List[Dict[str, Any]],
    step_counter: List[int],
) -> Decimal:
    """Perform decimal subtraction and record the explanation step."""
    result = left - right

    left_str = _format_decimal(left)
    right_str = _format_decimal(right)
    result_str = _format_decimal(result)

    if right < 0:
        description_key = "DECIMAL_SUBTRACT_NEGATIVE"
        description_params = {
            "left": left_str,
            "right": right_str,
            "result": result_str,
            "result_sign": _sign_label(result),
            "converted_addend": _format_decimal(-right),
        }
    else:
        description_key = "DECIMAL_SUBTRACT_POSITIVE"
        description_params = {
            "left": left_str,
            "right": right_str,
            "result": result_str,
            "result_sign": _sign_label(result),
        }

    formula_repr = f"{left_str} - {right_str}"
    formula_calc = f"{left_str} - {right_str} = {result_str}"

    formula_repr = wrap_negative_after_plus_minus(fix_unary_minus_spacing(formula_repr))
    formula_calc = wrap_negative_after_plus_minus(fix_unary_minus_spacing(formula_calc))

    _append_operation_step(
        steps,
        step_counter,
        description_key,
        description_params,
        formula_repr,
        formula_calc,
        result_str,
    )
    return result


def _perform_multiplication(
    left: Decimal,
    right: Decimal,
    steps: List[Dict[str, Any]],
    step_counter: List[int],
) -> Decimal:
    """Выполняет умножение десятичных дробей и добавляет пояснение шага."""
    result = left * right

    left_negative = left < 0
    right_negative = right < 0

    if left_negative and right_negative:
        description_key = "DECIMAL_MULTIPLY_BOTH_NEGATIVE"
    elif left_negative or right_negative:
        description_key = "DECIMAL_MULTIPLY_MIXED_SIGNS"
    else:
        description_key = "DECIMAL_MULTIPLY_BOTH_POSITIVE"

    left_str = _format_decimal(left)
    right_str = _format_decimal(right)
    result_str = _format_decimal(result)

    description_params = {
        "left": left_str,
        "right": right_str,
        "result": result_str,
        "result_sign": _sign_label(result),
    }

    formula_repr = normalize_for_display(f"{left_str} · {right_str}")
    formula_calc = normalize_for_display(f"{left_str} · {right_str} = {result_str}")

    # 💙 Финальная косметика: минус без пробелов и скобки после +/−
    formula_repr = wrap_negative_after_plus_minus(fix_unary_minus_spacing(formula_repr))
    formula_calc = wrap_negative_after_plus_minus(fix_unary_minus_spacing(formula_calc))

    _append_operation_step(
        steps,
        step_counter,
        description_key,
        description_params,
        formula_repr,
        formula_calc,
        result_str,
    )
    return result


def _perform_division(
    left: Decimal,
    right: Decimal,
    steps: List[Dict[str, Any]],
    step_counter: List[int],
) -> Decimal:
    """Выполняет деление десятичных дробей и добавляет пояснение шага."""
    result = left / right

    left_negative = left < 0
    right_negative = right < 0

    if left_negative and right_negative:
        description_key = "DECIMAL_DIVIDE_BOTH_NEGATIVE"
    elif left_negative or right_negative:
        description_key = "DECIMAL_DIVIDE_MIXED_SIGNS"
    else:
        description_key = "DECIMAL_DIVIDE_BOTH_POSITIVE"

    left_str = _format_decimal(left)
    right_str = _format_decimal(right)
    result_str = _format_decimal(result)

    description_params = {
        "left": left_str,
        "right": right_str,
        "result": result_str,
        "result_sign": _sign_label(result),
    }

    formula_repr = normalize_for_display(f"{left_str} : {right_str}")
    formula_calc = normalize_for_display(f"{left_str} : {right_str} = {result_str}")

    formula_repr = wrap_negative_after_plus_minus(fix_unary_minus_spacing(formula_repr))
    formula_calc = wrap_negative_after_plus_minus(fix_unary_minus_spacing(formula_calc))

    _append_operation_step(
        steps,
        step_counter,
        description_key,
        description_params,
        formula_repr,
        formula_calc,
        result_str,
    )
    return result

def _append_operation_step(
    steps: List[Dict[str, Any]],
    step_counter: List[int],
    description_key: str,
    description_params: Dict[str, Any],
    formula_repr: str,
    formula_calc: str,
    result_str: str,
) -> None:
    """Append a calculation step in the agreed solution_core format (beautified)."""
    # 🩵 Централизованное форматирование формул
    formula_repr = normalize_for_display(formula_repr)
    formula_calc = normalize_for_display(formula_calc)

    step = {
        "step_number": step_counter[0],
        "description_key": description_key,
        "description_params": description_params,
        "formula_representation": formula_repr,
        "formula_calculation": formula_calc,
        "calculation_result": result_str,
    }
    steps.append(step)
    step_counter[0] += 1


def _sign_label(value: Decimal) -> str:
    """Return a textual representation of the sign of a decimal value."""
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def _format_decimal(value: Decimal) -> str:
    """Render Decimal as localized string with comma separator for display."""
    # Приводим Decimal к строке и удаляем лишние нули
    result = str(value)
    if "." in result:
        result = result.rstrip("0").rstrip(".")
    # Меняем точку на запятую для отображения в стиле ОГЭ
    result = result.replace(".", ",")
    # Для отрицательных чисел — используем длинное тире (ГОСТ)
    if result.startswith("-"):
        result = "−" + result[1:]
    return result

# --- Дополнительные хелперы для упрощённых случаев ФИПИ (десятичные дроби) ---

def _format_decimal_ru(value: Decimal) -> str:
    """Форматирует десятичное число без хвостовых нулей и с запятой."""
    s = str(value)
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")

def _is_simple_add_sub(node: Dict[str, Any]) -> bool:
    """True, если это простое выражение: add/sub двух decimal-операндов."""
    if not isinstance(node, dict):
        return False
    if node.get("operation") not in ("add", "subtract"):
        return False
    ops = node.get("operands")
    if not (isinstance(ops, list) and len(ops) == 2):
        return False
    return all(isinstance(x, dict) and x.get("type") == "decimal" for x in ops)

def _has_brackets(node: dict) -> bool:
    """
    Возвращает True, если в expression_tree есть вложенные операции (скобки).
    Это значит, что выражение составное, как (8,5 − 1,5) : 2.
    """
    if not isinstance(node, dict):
        return False
    if node.get("operation") in ("add", "subtract", "multiply", "divide"):
        # если хотя бы один операнд — тоже операция, значит есть скобки
        return any(
            isinstance(child, dict) and child.get("operation") in ("add", "subtract", "multiply", "divide")
            for child in node.get("operands", [])
        )
    return False
