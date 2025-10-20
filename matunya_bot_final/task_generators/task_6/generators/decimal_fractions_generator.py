import random
import uuid
from typing import Dict, Any, List
import re


def generate_decimal_fractions_tasks(count: int = 10) -> List[Dict[str, Any]]:
    """
    Генератор заданий №6 (Тема 2: действия с десятичными дробями).
    Паттерны: 2.1 – сумма/разность десятичных дробей,
              2.2 – линейные выражения,
              2.3 – структура вида A / (B ± C) или A / (B·C).
    """
    tasks: List[Dict[str, Any]] = []
    patterns = ["2.1", "2.2", "2.3"]

    for _ in range(count):
        pattern_id = random.choice(patterns)
        if pattern_id == "2.1":
            task = _generate_df_addition_subtraction(pattern_id)
        elif pattern_id == "2.2":
            task = _generate_linear_operations(pattern_id)
        else:
            task = _generate_fraction_structure(pattern_id)
        tasks.append(task)

    return tasks


def _ensure_answer_field(question_text: str) -> str:
    text = question_text.strip()
    if "Ответ" not in text:
        text += "\n\nОтвет: ____________"
    return text


# ======================
# === ПАТТЕРН 2.1 ======
# ======================
def _generate_df_addition_subtraction(pattern_id: str) -> Dict[str, Any]:
    a = round(random.uniform(1, 20), 1)
    b = round(random.uniform(1, 20), 1)
    op = random.choice(["add", "sub"])
    result = a + b if op == "add" else a - b

    attempts = 0
    while not _is_pretty_decimal(result) and attempts < 100:
        a = round(random.uniform(1, 20), 1)
        b = round(random.uniform(1, 20), 1)
        op = random.choice(["add", "sub"])
        result = a + b if op == "add" else a - b
        attempts += 1

    symbol = "+" if op == "add" else "−"
    question_text = _ensure_answer_field(
        f"Посчитай значение:\n{a} {symbol} {b}"
    )
    expr_str = question_text
    if re.search(r'(^|[^0-9])0[.,]?\d*', expr_str) or '/0' in expr_str:
        return generate_decimal_fractions_tasks(1)[0]

    return {
        "id": f"6_df_addition_subtraction_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "decimal_fractions",
        "subtype": "df_addition_subtraction",
        "question_text": question_text,
        "answer": str(round(result, 3)),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": op,
                "operands": [
                    {"type": "decimal", "value": a, "text": str(a)},
                    {"type": "decimal", "value": b, "text": str(b)},
                ],
            }
        },
        "meta": {"difficulty": "easy", "pattern_id": pattern_id},
    }


# ======================
# === ПАТТЕРН 2.2 ======
# ======================
def _generate_linear_operations(pattern_id: str) -> Dict[str, Any]:
    a = random.randint(-6, 6)
    b = round(random.uniform(-10, 10), 1)
    c = round(random.uniform(-10, 10), 1)
    op = random.choice(["add", "sub"])

    result = a * b + c if op == "add" else a * b - c

    attempts = 0
    while not _is_pretty_decimal(result) and attempts < 100:
        a = random.randint(-6, 6)
        b = round(random.uniform(-10, 10), 1)
        c = round(random.uniform(-10, 10), 1)
        result = a * b + c if op == "add" else a * b - c
        attempts += 1

    symbol = "+" if op == "add" else "−"
    question_text = _ensure_answer_field(
        f"Вычисли выражение:\n{a}·({b}) {symbol} {c}"
    )
    expr_str = question_text
    if re.search(r'(^|[^0-9])0[.,]?\d*', expr_str) or '/0' in expr_str:
        return generate_decimal_fractions_tasks(1)[0]

    return {
        "id": f"6_linear_operations_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "decimal_fractions",
        "subtype": "linear_operations",
        "question_text": question_text,
        "answer": str(round(result, 3)),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": op,
                "operands": [
                    {
                        "operation": "mul",
                        "operands": [
                            {"type": "integer", "value": a, "text": str(a)},
                            {"type": "decimal", "value": b, "text": str(b)},
                        ],
                    },
                    {"type": "decimal", "value": c, "text": str(c)},
                ],
            }
        },
        "meta": {"difficulty": "medium", "pattern_id": pattern_id},
    }


# ======================
# === ПАТТЕРН 2.3 ======
# ======================
def _generate_fraction_structure(pattern_id: str) -> Dict[str, Any]:
    a = round(random.uniform(2, 20), 1)
    b = round(random.uniform(1, 10), 1)
    c = round(random.uniform(1, 10), 1)
    mode = random.choice(["add_sub", "mul"])

    if mode == "add_sub":
        inner_op = random.choice(["add", "sub"])
        inner_val = b + c if inner_op == "add" else b - c
        if inner_val == 0:
            inner_val += 1
        result = a / inner_val
    else:
        inner_val = b * c
        result = a / inner_val

    attempts = 0
    while not _is_pretty_decimal(result) and attempts < 100:
        a = round(random.uniform(2, 20), 1)
        b = round(random.uniform(1, 10), 1)
        c = round(random.uniform(1, 10), 1)
        if mode == "add_sub":
            inner_op = random.choice(["add", "sub"])
            inner_val = b + c if inner_op == "add" else b - c
            if inner_val == 0:
                inner_val += 1
            result = a / inner_val
        else:
            inner_val = b * c
            result = a / inner_val
        attempts += 1

    if mode == "add_sub":
        op_symbol = "+" if inner_op == "add" else "−"
        inner_text = f"{b} {op_symbol} {c}"
        inner_expr = {"operation": inner_op, "operands": [
            {"type": "decimal", "value": b, "text": str(b)},
            {"type": "decimal", "value": c, "text": str(c)}
        ]}
    else:
        op_symbol = "·"
        inner_text = f"{b} {op_symbol} {c}"
        inner_expr = {"operation": "mul", "operands": [
            {"type": "decimal", "value": b, "text": str(b)},
            {"type": "decimal", "value": c, "text": str(c)}
        ]}

    question_text = _ensure_answer_field(
        f"Посчитай значение дроби:\n{a} / ({inner_text})"
    )
    expr_str = question_text
    if re.search(r'(^|[^0-9])0[.,]?\d*', expr_str) or '/0' in expr_str:
        return generate_decimal_fractions_tasks(1)[0]

    return {
        "id": f"6_fraction_structure_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "decimal_fractions",
        "subtype": "fraction_structure",
        "question_text": question_text,
        "answer": str(round(result, 3)),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": "div",
                "operands": [
                    {"type": "decimal", "value": a, "text": str(a)},
                    inner_expr,
                ],
            }
        },
        "meta": {"difficulty": "hard", "pattern_id": pattern_id},
    }


def _is_pretty_decimal(value: float) -> bool:
    try:
        s = f"{abs(value):.6f}".rstrip("0").rstrip(".")
        if "." in s:
            decimals = len(s.split(".")[1])
            if decimals > 3:
                return False
        return abs(value) <= 1_000
    except Exception:
        return False
