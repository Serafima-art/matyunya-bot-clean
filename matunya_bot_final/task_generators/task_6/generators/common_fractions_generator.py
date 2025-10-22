import random
import uuid
from fractions import Fraction
from typing import Dict, Any, List
import re

from matunya_bot_final.task_generators.task_6.generators.task6_text_formatter import prepare_expression, _fmt_answer  # TASK6_FORMATTER_IMPORT

def generate_common_fractions_tasks(count: int = 10) -> List[Dict[str, Any]]:
    """
    Генератор заданий №6 (Тема 1: действия с обыкновенными дробями).
    Поддерживает паттерны 1.1–1.4.
    """
    tasks: List[Dict[str, Any]] = []
    patterns = ["1.1", "1.2", "1.3", "1.4"]

    for _ in range(count):
        pattern_id = random.choice(patterns)
        if pattern_id == "1.1":
            task = _generate_cf_addition_subtraction(pattern_id)
        elif pattern_id == "1.2":
            task = _generate_multiplication_division(pattern_id)
        elif pattern_id == "1.3":
            task = _generate_parentheses_operations(pattern_id)
        else:
            task = _generate_complex_fraction(pattern_id)
        tasks.append(task)

    return tasks


def _ensure_answer_field(question_text: str) -> str:
    text = question_text.strip()
    if "Ответ" not in text:
        text += "\n\nОтвет: ____________"
    return text


# ======================
# === ПАТТЕРН 1.1 ======
# ======================
def _generate_cf_addition_subtraction(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(80):
        a, b = _rand_frac(), _rand_frac()
        op = random.choice(["add", "sub"])
        result = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])

        attempts = 0
        while not _is_pretty_decimal(result) and attempts < 100:
            a, b = _rand_frac(), _rand_frac()
            op = random.choice(["add", "sub"])
            result = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])
            attempts += 1

        text_op = "+" if op == "add" else "−"
        expr_line = f"{a[0]}/{a[1]} {text_op} {b[0]}/{b[1]}"
        formatted_expr = prepare_expression(expr_line)
        if formatted_expr is None:
            continue
        if re.search(r'(^|[^0-9])0[.,]?\d*', formatted_expr) or "/0" in formatted_expr:
            continue

        question_text = _ensure_answer_field(
            f"Вычисли результат:\n{formatted_expr}"
        )

        return {
            "id": f"6_cf_addition_subtraction_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "topic": "common_fractions",
            "subtype": "cf_addition_subtraction",
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": op,
                    "operands": [
                        {"type": "common", "value": [a[0], a[1]], "text": f"{a[0]}/{a[1]}"},
                        {"type": "common", "value": [b[0], b[1]], "text": f"{b[0]}/{b[1]}"},
                    ],
                }
            },
            "meta": {"difficulty": "easy", "pattern_id": pattern_id},
        }

    return __safe_fallback_for_this_subtype(pattern_id)


def _generate_multiplication_division(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(80):
        a, b = _rand_mixed(), _rand_frac()
        op = random.choice(["mul", "div"])
        a_val = Fraction(a[0] * a[2] + a[1], a[2])
        result = a_val * Fraction(b[0], b[1]) if op == "mul" else a_val / Fraction(b[0], b[1])

        attempts = 0
        while not _is_pretty_decimal(result) and attempts < 100:
            a, b = _rand_mixed(), _rand_frac()
            op = random.choice(["mul", "div"])
            a_val = Fraction(a[0] * a[2] + a[1], a[2])
            result = a_val * Fraction(b[0], b[1]) if op == "mul" else a_val / Fraction(b[0], b[1])
            attempts += 1

        text_op = "·" if op == "mul" else ":"
        text_a = f"{a[0]} {a[1]}/{a[2]}"
        text_b = f"{b[0]}/{b[1]}"
        expr_line = f"{text_a} {text_op} {text_b}"
        formatted_expr = prepare_expression(expr_line)
        if formatted_expr is None:
            continue
        if re.search(r'(^|[^0-9])0[.,]?\d*', formatted_expr) or "/0" in formatted_expr:
            continue

        question_text = _ensure_answer_field(
            f"Выполни действия:\n{formatted_expr}"
        )

        return {
            "id": f"6_multiplication_division_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "topic": "common_fractions",
            "subtype": "multiplication_division",
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": op,
                    "operands": [
                        {"type": "mixed", "value": [a[0], a[1], a[2]], "text": text_a},
                        {"type": "common", "value": [b[0], b[1]], "text": text_b},
                    ],
                }
            },
            "meta": {"difficulty": "medium", "pattern_id": pattern_id},
        }

    return __safe_fallback_for_this_subtype(pattern_id)


def _generate_parentheses_operations(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(80):
        a, b, c = _rand_frac(), _rand_frac(), _rand_frac()
        inner_op = random.choice(["add", "sub"])
        outer_op = random.choice(["mul", "div"])

        inner_val = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if inner_op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])
        result = inner_val * Fraction(c[0], c[1]) if outer_op == "mul" else inner_val / Fraction(c[0], c[1])

        attempts = 0
        while not _is_pretty_decimal(result) and attempts < 100:
            a, b, c = _rand_frac(), _rand_frac(), _rand_frac()
            inner_op = random.choice(["add", "sub"])
            outer_op = random.choice(["mul", "div"])
            inner_val = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if inner_op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])
            result = inner_val * Fraction(c[0], c[1]) if outer_op == "mul" else inner_val / Fraction(c[0], c[1])
            attempts += 1

        op_symbols = {"add": "+", "sub": "−", "mul": "·", "div": ":"}
        expr_line = f"({a[0]}/{a[1]} {op_symbols[inner_op]} {b[0]}/{b[1]}) {op_symbols[outer_op]} {c[0]}/{c[1]}"
        formatted_expr = prepare_expression(expr_line)
        if formatted_expr is None:
            continue
        if re.search(r'(^|[^0-9])0[.,]?\d*', formatted_expr) or "/0" in formatted_expr:
            continue

        question_text = _ensure_answer_field(
            f"Раскрой скобки и выполни вычисления:\n{formatted_expr}"
        )

        return {
            "id": f"6_parentheses_operations_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "topic": "common_fractions",
            "subtype": "parentheses_operations",
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": outer_op,
                    "operands": [
                        {
                            "operation": inner_op,
                            "operands": [
                                {"type": "common", "value": [a[0], a[1]], "text": f"{a[0]}/{a[1]}"},
                                {"type": "common", "value": [b[0], b[1]], "text": f"{b[0]}/{b[1]}"},
                            ],
                        },
                        {"type": "common", "value": [c[0], c[1]], "text": f"{c[0]}/{c[1]}"},
                    ],
                }
            },
            "meta": {"difficulty": "medium", "pattern_id": pattern_id},
        }

    return __safe_fallback_for_this_subtype(pattern_id)


def _generate_complex_fraction(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(80):
        a, b, c = _rand_frac(), _rand_frac(), _rand_frac()
        inner_op = random.choice(["add", "sub"])
        inner_val = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if inner_op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])
        result = inner_val / Fraction(c[0], c[1])

        attempts = 0
        while not _is_pretty_decimal(result) and attempts < 100:
            a, b, c = _rand_frac(), _rand_frac(), _rand_frac()
            inner_op = random.choice(["add", "sub"])
            inner_val = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if inner_op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])
            result = inner_val / Fraction(c[0], c[1])
            attempts += 1

        op_symbols = {"add": "+", "sub": "−"}
        expr_line = f"({a[0]}/{a[1]} {op_symbols[inner_op]} {b[0]}/{b[1]}) / ({c[0]}/{c[1]})"
        formatted_expr = prepare_expression(expr_line)
        if formatted_expr is None:
            continue
        if re.search(r'(^|[^0-9])0[.,]?\d*', formatted_expr) or "/0" in formatted_expr:
            continue

        question_text = _ensure_answer_field(
            f"Вычисли значение дроби:\n{formatted_expr}"
        )

        return {
            "id": f"6_complex_fraction_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "topic": "common_fractions",
            "subtype": "complex_fraction",
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": "div",
                    "operands": [
                        {
                            "operation": inner_op,
                            "operands": [
                                {"type": "common", "value": [a[0], a[1]], "text": f"{a[0]}/{a[1]}"},
                                {"type": "common", "value": [b[0], b[1]], "text": f"{b[0]}/{b[1]}"},
                            ],
                        },
                        {"type": "common", "value": [c[0], c[1]], "text": f"{c[0]}/{c[1]}"},
                    ],
                }
            },
            "meta": {"difficulty": "hard", "pattern_id": pattern_id},
        }

    return __safe_fallback_for_this_subtype(pattern_id)


def _rand_frac() -> tuple[int, int]:
    pretty_denominators = [2, 4, 5, 8, 10, 16, 20, 25]
    numerator = random.randint(1, 20)
    denominator = random.choice(pretty_denominators)
    while numerator == denominator:
        numerator = random.randint(1, 20)
    return numerator, denominator


def _rand_mixed() -> tuple[int, int, int]:
    pretty_denominators = [2, 4, 5, 8, 10, 16, 20, 25]
    whole = random.randint(1, 5)
    numerator = random.randint(1, 9)
    denominator = random.choice(pretty_denominators)
    while numerator == denominator:
        numerator = random.randint(1, 9)
    return whole, numerator, denominator


def _is_pretty_decimal(value: float) -> bool:
    """
    Проверяет, что число представимо конечной десятичной дробью с ≤2 знаками после запятой.
    """
    try:
        frac = Fraction(value).limit_denominator()
        den = frac.denominator

        while den % 2 == 0:
            den //= 2
        while den % 5 == 0:
            den //= 5
        if den != 1:
            return False

        s = f"{float(value):.10f}".rstrip("0").rstrip(".")
        if "." in s:
            decimals = len(s.split(".")[1])
            if decimals > 2:
                return False
        return True
    except Exception:
        return False


def __safe_fallback_for_this_subtype(pattern_id: str) -> Dict[str, Any]:
    if pattern_id == "1.1":  # cf_addition_subtraction
        expression = "1 / 2 + 1 / 4"
        question_text = _ensure_answer_field(f"Вычисли результат:\n{expression}")
        result = 0.75
        return {
            "id": "6_cf_addition_subtraction_fallback",
            "task_number": 6,
            "topic": "common_fractions",
            "subtype": "cf_addition_subtraction",
            "question_text": question_text,
            "answer": _fmt_answer(result),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": "add",
                    "operands": [
                        {"type": "common", "value": [1, 2], "text": "1/2"},
                        {"type": "common", "value": [1, 4], "text": "1/4"},
                    ],
                }
            },
            "meta": {"difficulty": "easy", "pattern_id": pattern_id},
        }
    if pattern_id == "1.2":  # multiplication_division
        expression = "1 1/2 · 2/5"
        question_text = _ensure_answer_field(f"Выполни действия:\n{expression}")
        result = 0.6
        return {
            "id": "6_multiplication_division_fallback",
            "task_number": 6,
            "topic": "common_fractions",
            "subtype": "multiplication_division",
            "question_text": question_text,
            "answer": _fmt_answer(result),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": "mul",
                    "operands": [
                        {"type": "mixed", "value": [1, 1, 2], "text": "1 1/2"},
                        {"type": "common", "value": [2, 5], "text": "2/5"},
                    ],
                }
            },
            "meta": {"difficulty": "medium", "pattern_id": pattern_id},
        }
    if pattern_id == "1.3":  # parentheses_operations
        expression = "(1/2 + 1/4) · 2/5"
        question_text = _ensure_answer_field(f"Раскрой скобки и выполни вычисления:\n{expression}")
        result = 0.3
        return {
            "id": "6_parentheses_operations_fallback",
            "task_number": 6,
            "topic": "common_fractions",
            "subtype": "parentheses_operations",
            "question_text": question_text,
            "answer": _fmt_answer(result),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": "mul",
                    "operands": [
                        {
                            "operation": "add",
                            "operands": [
                                {"type": "common", "value": [1, 2], "text": "1/2"},
                                {"type": "common", "value": [1, 4], "text": "1/4"},
                            ],
                        },
                        {"type": "common", "value": [2, 5], "text": "2/5"},
                    ],
                }
            },
            "meta": {"difficulty": "medium", "pattern_id": pattern_id},
        }
    expression = "(1/2 + 1/4) / (3/5)"
    question_text = _ensure_answer_field(f"Вычисли значение дроби:\n{expression}")
    result = 1.25
    return {
        "id": "6_complex_fraction_fallback",
        "task_number": 6,
        "topic": "common_fractions",
        "subtype": "complex_fraction",
        "question_text": question_text,
        "answer": _fmt_answer(result),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": "div",
                "operands": [
                    {
                        "operation": "add",
                        "operands": [
                            {"type": "common", "value": [1, 2], "text": "1/2"},
                            {"type": "common", "value": [1, 4], "text": "1/4"},
                        ],
                    },
                    {"type": "common", "value": [3, 5], "text": "3/5"},
                ],
            }
        },
        "meta": {"difficulty": "hard", "pattern_id": pattern_id},
    }
