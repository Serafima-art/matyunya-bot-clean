import random
import uuid
from fractions import Fraction
from typing import Dict, Any, List
import math
import re

from matunya_bot_final.task_generators.task_6.generators.task6_text_formatter import (
    normalize_expression,
    prepare_expression,
    _fmt_answer,
)

def generate_common_fractions_tasks(count: int = 10) -> List[Dict[str, Any]]:
    """
    Генератор заданий №6 (Тема 1: действия с обыкновенными дробями).
    Поддерживает паттерны 1.1–1.4.
    """
    tasks: List[Dict[str, Any]] = []
    patterns = [
        "cf_addition_subtraction",
        "multiplication_division",
        "parentheses_operations",
        "complex_fraction",
    ]

    for _ in range(count):
        pattern_id = random.choice(patterns)
        if pattern_id == "cf_addition_subtraction":
            task = _generate_cf_addition_subtraction(pattern_id)
        elif pattern_id == "multiplication_division":
            task = _generate_multiplication_division(pattern_id)
        elif pattern_id == "parentheses_operations":
            task = _generate_parentheses_operations(pattern_id)
        elif pattern_id == "complex_fraction":
            task = _generate_complex_fraction(pattern_id)
        else:
            # На случай будущих расширений или опечаток — пробуем заново
            task = _generate_cf_addition_subtraction("cf_addition_subtraction")

        if task is not None:
            tasks.append(task)

    return [t for t in tasks if t is not None]


def _ensure_answer_field(question_text: str) -> str:
    text = question_text.strip()
    if "Ответ" not in text:
        text += "\n\nОтвет: ____________"
    return text


# ======================
# === ПАТТЕРН 1.1 ======
# ======================
def _generate_cf_addition_subtraction(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(500):
        a, b = _rand_frac(), _rand_frac()
        op = random.choice(["add", "sub"])
        f1, f2 = Fraction(a[0], a[1]), Fraction(b[0], b[1])
        result = f1 + f2 if op == "add" else f1 - f2

        # 🚫 исключаем нулевые, отрицательные и "единичные" случаи (5/8 + 5/8, 7/9 − 8/9 и т.п.)
        if result <= 0 or a[0] == a[1] or b[0] == b[1]:
            continue

        # 🔹 вычисляем несократимую дробь
        simplified = result.limit_denominator()
        num, den = simplified.numerator, simplified.denominator

        attempts = 0
        while not _is_pretty_decimal(result) and attempts < 100:
            a, b = _rand_frac(), _rand_frac()
            op = random.choice(["add", "sub"])
            result = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])
            attempts += 1

        text_op = "+" if op == "add" else "−"
        expr_line = f"{a[0]}/{a[1]} {text_op} {b[0]}/{b[1]}"
        formatted_expr = prepare_expression(expr_line)
        if formatted_expr is None or re.search(r'(?<!\d)/0(?!\d)', formatted_expr):
            print("[⚠️ skip: деление на ноль]", expr_line)
            continue
        formatted_expr = normalize_expression(formatted_expr)
        # ⛔ отбрасываем пустые и бессодержательные выражения
        if (not formatted_expr
            or not re.search(r"\d", formatted_expr)
            or not re.search(r"[/:·+\-−()]", formatted_expr)):
            print("[⚠️ skip: пустое выражение]", expr_line)
            continue

        if re.search(r'(^|[^0-9])0[.,]?\d*', formatted_expr) or "/0" in formatted_expr:
            continue

        question_text = _ensure_answer_field(
        f"Найди значение выражения:\n{formatted_expr}\n\n"
        f"Получи результат в виде обыкновенной дроби, которую нельзя сократить, "
        f"в ответ запиши только числитель."
        )

        assert ":\n" in question_text and len(question_text.splitlines()) >= 2, (
            "Пустой question_text — отсутствует выражение."
        )
        return {
            "id": f"6_cf_addition_subtraction_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "subtype": "common_fractions",
            "pattern": "cf_addition_subtraction",
            "question_text": question_text,
            "answer": str(num),  # только числитель
            "answer_type": "integer",
            "variables": {
                "expression_tree": {
                    "operation": op.replace("sub", "subtract"),
                    "operands": [
                        {"type": "common", "value": [a[0], a[1]], "text": f"{a[0]}/{a[1]}"},
                        {"type": "common", "value": [b[0], b[1]], "text": f"{b[0]}/{b[1]}"},
                    ],
                }
            },
            "meta": {"difficulty": "easy", "pattern_id": pattern_id},
        }

    # Если после всех попыток не удалось создать валидную задачу — пропускаем
    return None

# ======================
# === ПАТТЕРН 1.2 ======
# ======================

def _generate_multiplication_division(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(500):
        a, b = _rand_mixed(), _rand_frac()
        op = random.choice(["mul", "div"])
        a_val = Fraction(a[0] * a[2] + a[1], a[2])
        result = a_val * Fraction(b[0], b[1]) if op == "mul" else a_val / Fraction(b[0], b[1])

        # 🚫 исключаем нулевые результаты (например, 0 · 3/5 или 1 1/2 : ∞)
        if result == 0:
            continue
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
        if formatted_expr is None or re.search(r'(?<!\d)/0(?!\d)', formatted_expr):
            print("[⚠️ skip: деление на ноль]", expr_line)
            continue
        formatted_expr = normalize_expression(formatted_expr)
        # ⛔ отбрасываем пустые и бессодержательные выражения
        if (not formatted_expr
            or not re.search(r"\d", formatted_expr)
            or not re.search(r"[/:·+\-−()]", formatted_expr)):
            print("[⚠️ skip: пустое выражение]", expr_line)
            continue

        if re.search(r'(^|[^0-9])0[.,]?\d*', formatted_expr) or "/0" in formatted_expr:
            continue

        question_text = _ensure_answer_field(
            f"Выполни действия:\n{formatted_expr}"
        )

        improper_num = a[0] * a[2] + a[1]
        improper_den = a[2]
        assert ":\n" in question_text and len(question_text.splitlines()) >= 2, (
            "Пустой question_text — отсутствует выражение."
        )
        return {
            "id": f"6_multiplication_division_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "subtype": "common_fractions",
            "pattern": "multiplication_division",
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": op.replace("mul", "multiply").replace("div", "divide"),
                    "operands": [
                        {"type": "common", "value": [improper_num, improper_den], "text": text_a},
                        {"type": "common", "value": [b[0], b[1]], "text": text_b},
                    ],
                }
            },
            "meta": {"difficulty": "medium", "pattern_id": pattern_id},
        }

    # Если после всех попыток не удалось создать валидную задачу — пропускаем
    return None

# ======================
# === ПАТТЕРН 1.3 ======
# ======================

def _generate_parentheses_operations(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(500):
        a, b, c = _rand_frac(), _rand_frac(), _rand_frac()

        # 🚫 защита от одинаковых дробей (иначе будет 0)
        if a == b:
            continue

        inner_op = random.choice(["add", "subtract"])
        outer_op = random.choice(["multiply", "divide"])

        inner_val = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if inner_op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])
        if inner_val == 0:
            continue  # 🚫 исключаем нулевой внутренний результат

        result = inner_val * Fraction(c[0], c[1]) if outer_op == "multiply" else inner_val / Fraction(c[0], c[1])

        # 🚫 исключаем случаи, когда выражение стало нулём
        if result == 0:
            continue

        if not _is_pretty_decimal(result):
            continue

        op_symbols = {"add": "+", "subtract": "−", "multiply": "·", "divide": ":"}
        expr_line = f"({a[0]}/{a[1]} {op_symbols[inner_op]} {b[0]}/{b[1]}) {op_symbols[outer_op]} {c[0]}/{c[1]}"
        formatted_expr = prepare_expression(expr_line)
        if formatted_expr is None or re.search(r'(?<!\d)/0(?!\d)', formatted_expr):
            print("[⚠️ skip: деление на ноль]", expr_line)
            continue
        formatted_expr = normalize_expression(formatted_expr)
        # ⛔ отбрасываем пустые и бессодержательные выражения
        if (not formatted_expr
            or not re.search(r"\d", formatted_expr)
            or not re.search(r"[/:·+\-−()]", formatted_expr)):
            print("[⚠️ skip: пустое выражение]", expr_line)
            continue


        question_text = _ensure_answer_field(
            f"Раскрой скобки и выполни вычисления:\n{formatted_expr}"
        )

        assert ":\n" in question_text and len(question_text.splitlines()) >= 2, (
            "Пустой question_text — отсутствует выражение."
        )
        return {
            "id": f"6_parentheses_operations_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "subtype": "common_fractions",
            "pattern": "parentheses_operations",
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

    # Если после всех попыток не удалось создать валидную задачу — пропускаем
    return None

# ======================
# === ПАТТЕРН 1.4 ======
# ======================

def _generate_complex_fraction(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(500):
        # --- защита от повторов (анти-дубликатор) ---
        if not hasattr(_generate_complex_fraction, "_used_combos"):
            _generate_complex_fraction._used_combos = set()
        used = _generate_complex_fraction._used_combos

        a, b, c = _rand_frac(), _rand_frac(), _rand_frac()
        inner_op = random.choice(["add", "subtract"])

        combo = (a, b, c, inner_op)
        if combo in used:
            continue
        used.add(combo)

        inner_val = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if inner_op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])
        result = inner_val / Fraction(c[0], c[1])

        attempts = 0
        while not _is_pretty_decimal(result) and attempts < 100:
            a, b, c = _rand_frac(), _rand_frac(), _rand_frac()
            inner_op = random.choice(["add", "subtract"])
            inner_val = Fraction(a[0], a[1]) + Fraction(b[0], b[1]) if inner_op == "add" else Fraction(a[0], a[1]) - Fraction(b[0], b[1])
            result = inner_val / Fraction(c[0], c[1])
            attempts += 1
            combo = (a, b, c, inner_op)
            if combo in used:
                continue
            used.add(combo)

        op_symbols = {"add": "+", "subtract": "−"}
        expr_line = f"({a[0]}/{a[1]} {op_symbols[inner_op]} {b[0]}/{b[1]}) / ({c[0]}/{c[1]})"
        formatted_expr = prepare_expression(expr_line)
        if formatted_expr is None or re.search(r'(?<!\d)/0(?!\d)', formatted_expr):
            print("[⚠️ skip: деление на ноль]", expr_line)
            continue
        formatted_expr = normalize_expression(formatted_expr)
        # ⛔ отбрасываем пустые и бессодержательные выражения
        if (not formatted_expr
            or not re.search(r"\d", formatted_expr)
            or not re.search(r"[/:·+\-−()]", formatted_expr)):
            print("[⚠️ skip: пустое выражение]", expr_line)
            continue

        if re.search(r'(^|[^0-9])0[.,]?\d*', formatted_expr) or "/0" in formatted_expr:
            continue

        question_text = _ensure_answer_field(
            f"Вычисли значение дроби:\n{formatted_expr}"
        )

        assert ":\n" in question_text and len(question_text.splitlines()) >= 2, (
            "Пустой question_text — отсутствует выражение."
        )
        return {
            "id": f"6_complex_fraction_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "subtype": "common_fractions",
            "pattern": "complex_fraction",
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": "divide",
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

    # Если после всех попыток не удалось создать валидную задачу — пропускаем
    return None


def _rand_frac() -> tuple[int, int]:
    """
    Генерирует случайную обыкновенную дробь a/b.
    - знаменатель: от 6 до 60 (исключая слишком «круглые» значения);
    - числитель: от 1 до (b−1);
    - дробь всегда правильная и несократимая.
    """
    denominators = [n for n in range(6, 61) if n not in (10, 20, 25, 30, 40, 50, 60)]
    denominator = random.choice(denominators)
    numerator = random.randint(1, denominator - 1)

    # Гарантируем несократимость
    while math.gcd(numerator, denominator) != 1:
        numerator = random.randint(1, denominator - 1)

    return numerator, denominator


def _rand_mixed() -> tuple[int, int, int]:
    whole = random.randint(1, 4)
    numerator, denominator = _rand_frac()
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
