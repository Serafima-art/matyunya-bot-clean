import random
import uuid
from fractions import Fraction
from typing import Dict, Any, List
import re


def generate_powers_tasks(count: int = 10) -> List[Dict[str, Any]]:
    """
    Генератор заданий №6 (Тема 4: степени и степенные выражения).
    Поддерживаются подтипы:
        4.1 — powers_with_fractions
        4.2 — powers_of_ten
    """
    tasks: List[Dict[str, Any]] = []
    for _ in range(count):
        pattern_id = random.choice(["4.1", "4.2"])
        if pattern_id == "4.1":
            task = _generate_powers_with_fractions(pattern_id)
        else:
            task = _generate_powers_of_ten(pattern_id)
        tasks.append(task)
    return tasks


# ======================
# === ВСПОМОГАТЕЛЬНЫЕ ===
# ======================
def _rand_exp_for_scientific() -> int:
    """
    Возвращает показатель степени для записи 10^k,
    исключая случаи k ∈ {0, 1}.
    """
    candidates = [-6, -5, -4, -3, -2, -1, 2, 3, 4, 5, 6]
    return random.choice(candidates)


def _ensure_answer_field(question_text: str) -> str:
    stripped = question_text.strip()
    if "Ответ" not in stripped:
        stripped += "\n\nОтвет: ____________"
    return stripped


# ======================
# === ПАТТЕРН 4.1 ======
# ======================
def _generate_powers_with_fractions(pattern_id: str) -> Dict[str, Any]:
    # Пример вида: 21·(2/7)² + 2/7
    n, a, b = random.randint(3, 30), random.randint(1, 5), random.choice([2, 4, 5, 7, 8, 10])
    k = random.randint(1, 25)
    op = random.choice(["add", "sub"])

    frac = Fraction(a, b)
    power_val = frac ** 2
    result = n * power_val + k * frac if op == "add" else n * power_val - k * frac

    attempts = 0
    while not _is_pretty_decimal(result) and attempts < 100:
        n, a, b = random.randint(3, 30), random.randint(1, 5), random.choice([2, 4, 5, 7, 8, 10])
        k = random.randint(1, 25)
        op = random.choice(["add", "sub"])
        frac = Fraction(a, b)
        power_val = frac ** 2
        result = n * power_val + k * frac if op == "add" else n * power_val - k * frac
        attempts += 1

    text_op = "+" if op == "add" else "−"
    question_text = f"Вычисли значение выражения:\n{n}·({a}/{b})² {text_op} {k}·{a}/{b}"
    expr_str = question_text
    if re.search(r"(^|[^0-9])0[.,]?\d*", expr_str) or "/0" in expr_str:
        return generate_powers_tasks(1)[0]
    question_text = _ensure_answer_field(question_text)

    return {
        "id": f"6_powers_with_fractions_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "powers",
        "subtype": "powers_with_fractions",
        "question_text": question_text,
        "answer": str(float(result)),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": op,
                "operands": [
                    {
                        "operation": "mul",
                        "operands": [
                            {"type": "integer", "value": n, "text": str(n)},
                            {
                                "operation": "pow",
                                "operands": [
                                    {"type": "common", "value": [a, b], "text": f"{a}/{b}"},
                                    {"type": "integer", "value": 2, "text": "2"},
                                ],
                            },
                        ],
                    },
                    {
                        "operation": "mul",
                        "operands": [
                            {"type": "integer", "value": k, "text": str(k)},
                            {"type": "common", "value": [a, b], "text": f"{a}/{b}"},
                        ],
                    },
                ],
            }
        },
        "meta": {"difficulty": "medium", "pattern_id": pattern_id},
    }


# ======================
# === ПАТТЕРН 4.2 ======
# ======================
def _generate_powers_of_ten(pattern_id: str) -> Dict[str, Any]:
    # Пример: (5·10^2)^3·(9·10^-4)
    base1 = random.randint(2, 9)
    exp1 = abs(_rand_exp_for_scientific())
    outer_pow = random.randint(2, 3)
    base2 = random.randint(2, 9)
    exp2 = _rand_exp_for_scientific()
    if exp2 > 0:
        exp2 = -exp2

    # Вычисления для ответа
    val1 = (base1 * (10 ** exp1)) ** outer_pow
    val2 = base2 * (10 ** exp2)
    result = val1 * val2

    attempts = 0
    while not _is_pretty_decimal(result) and attempts < 100:
        base1 = random.randint(2, 9)
        exp1 = abs(_rand_exp_for_scientific())
        outer_pow = random.randint(2, 3)
        base2 = random.randint(2, 9)
        exp2 = _rand_exp_for_scientific()
        if exp2 > 0:
            exp2 = -exp2
        val1 = (base1 * (10 ** exp1)) ** outer_pow
        val2 = base2 * (10 ** exp2)
        result = val1 * val2
        attempts += 1

    question_text = f"Вычисли выражение:\n({base1}·10^{exp1})^{outer_pow}·({base2}·10^{exp2})"
    expr_str = question_text
    if re.search(r"(^|[^0-9])0[.,]?\d*", expr_str) or "/0" in expr_str:
        return generate_powers_tasks(1)[0]
    question_text = question_text.replace("10^1", "10")
    question_text = _ensure_answer_field(question_text)

    return {
        "id": f"6_powers_of_ten_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "powers",
        "subtype": "powers_of_ten",
        "question_text": question_text,
        "answer": str(round(float(result), 6)),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": "mul",
                "operands": [
                    {
                        "operation": "pow",
                        "operands": [
                            {
                                "operation": "mul",
                                "operands": [
                                    {"type": "integer", "value": base1, "text": str(base1)},
                                    {"type": "power_of_ten", "value": exp1, "text": f"10^{exp1}"},
                                ],
                            },
                            {"type": "integer", "value": outer_pow, "text": str(outer_pow)},
                        ],
                    },
                    {
                        "operation": "mul",
                        "operands": [
                            {"type": "integer", "value": base2, "text": str(base2)},
                            {"type": "power_of_ten", "value": exp2, "text": f"10^{exp2}"},
                        ],
                    },
                ],
            }
        },
        "meta": {"difficulty": "hard", "pattern_id": pattern_id},
    }


# ======================
# === ВСПОМОГАТЕЛЬНЫЕ ===
# ======================
def _is_pretty_decimal(value: float) -> bool:
    """
    Проверяет, является ли число «красивым»:
    - либо целое,
    - либо конечная десятичная дробь (не более 2 знаков после запятой),
    - знаменатель дроби имеет только множители 2 и 5.
    """
    try:
        frac = Fraction(value).limit_denominator()
        den = frac.denominator

        # Проверка на конечность (только множители 2 и 5)
        while den % 2 == 0:
            den //= 2
        while den % 5 == 0:
            den //= 5
        if den != 1:
            return False

        # Проверка длины десятичной части
        s = f"{float(value):.10f}".rstrip("0").rstrip(".")
        if "." in s:
            decimals = len(s.split(".")[1])
            if decimals > 2:
                return False
        return True
    except Exception:
        return False
