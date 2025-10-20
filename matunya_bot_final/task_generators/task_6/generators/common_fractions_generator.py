import random
import uuid
from fractions import Fraction
from typing import Dict, Any, List
import re


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
    question_text = _ensure_answer_field(
        f"Вычисли результат:\n{a[0]}/{a[1]} {text_op} {b[0]}/{b[1]}"
    )
    expr_str = question_text
    if re.search(r'(^|[^0-9])0[.,]?\d*', expr_str) or '/0' in expr_str:
        return generate_common_fractions_tasks(1)[0]

    return {
        "id": f"6_cf_addition_subtraction_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "common_fractions",
        "subtype": "cf_addition_subtraction",
        "question_text": question_text,
        "answer": str(float(result)),
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


# ======================
# === ПАТТЕРН 1.2 ======
# ======================
def _generate_multiplication_division(pattern_id: str) -> Dict[str, Any]:
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
    question_text = _ensure_answer_field(
        f"Выполни действия:\n{text_a} {text_op} {text_b}"
    )
    expr_str = question_text
    if re.search(r'(^|[^0-9])0[.,]?\d*', expr_str) or '/0' in expr_str:
        return generate_common_fractions_tasks(1)[0]

    return {
        "id": f"6_multiplication_division_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "common_fractions",
        "subtype": "multiplication_division",
        "question_text": question_text,
        "answer": str(float(result)),
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


# ======================
# === ПАТТЕРН 1.3 ======
# ======================
def _generate_parentheses_operations(pattern_id: str) -> Dict[str, Any]:
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
    question_text = _ensure_answer_field(
        f"Раскрой скобки и выполни вычисления:\n({a[0]}/{a[1]} {op_symbols[inner_op]} {b[0]}/{b[1]}) {op_symbols[outer_op]} {c[0]}/{c[1]}"
    )
    expr_str = question_text
    if re.search(r'(^|[^0-9])0[.,]?\d*', expr_str) or '/0' in expr_str:
        return generate_common_fractions_tasks(1)[0]

    return {
        "id": f"6_parentheses_operations_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "common_fractions",
        "subtype": "parentheses_operations",
        "question_text": question_text,
        "answer": str(float(result)),
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


# ======================
# === ПАТТЕРН 1.4 ======
# ======================
def _generate_complex_fraction(pattern_id: str) -> Dict[str, Any]:
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
    question_text = _ensure_answer_field(
        f"Вычисли значение дроби:\n({a[0]}/{a[1]} {op_symbols[inner_op]} {b[0]}/{b[1]}) / ({c[0]}/{c[1]})"
    )
    expr_str = question_text
    if re.search(r'(^|[^0-9])0[.,]?\d*', expr_str) or '/0' in expr_str:
        return generate_common_fractions_tasks(1)[0]

    return {
        "id": f"6_complex_fraction_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "common_fractions",
        "subtype": "complex_fraction",
        "question_text": question_text,
        "answer": str(float(result)),
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


# ======================
# === ВСПОМОГАТЕЛЬНЫЕ ===
# ======================
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
