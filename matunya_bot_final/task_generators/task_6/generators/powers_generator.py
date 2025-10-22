import random
import uuid
from fractions import Fraction
from typing import Dict, Any, List
import re

from matunya_bot_final.task_generators.task_6.generators.task6_text_formatter import prepare_expression, _fmt_answer  # TASK6_FORMATTER_IMPORT

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
    for __retry in range(80):
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
        expression = f"{n}·({a}/{b})² {text_op} {k}·{a}/{b}"
        question_text = _ensure_answer_field(f"Вычисли значение выражения:\n{expression}")

        return {
            "id": f"6_powers_with_fractions_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "topic": "powers",
            "subtype": "powers_with_fractions",
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
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

    return __safe_fallback_for_this_subtype(pattern_id)


# ======================
# === ПАТТЕРН 4.2 ======
# ======================
def _generate_powers_of_ten(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(80):
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

        expression = f"({base1}·10^{exp1})^{outer_pow}·({base2}·10^{exp2})"
        expression = expression.replace("10^1", "10")
        question_text = _ensure_answer_field(f"Вычисли выражение:\n{expression}")

        return {
            "id": f"6_powers_of_ten_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "topic": "powers",
            "subtype": "powers_of_ten",
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
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

    return __safe_fallback_for_this_subtype(pattern_id)


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


def __safe_fallback_for_this_subtype(pattern_id: str) -> Dict[str, Any]:
    if pattern_id == "4.1":
        question_text = _ensure_answer_field("Выполни вычисление:\n2·(1/2)^2 · 3·1/2")
        result = 0.75
        return {
            "id": "6_powers_with_fractions_fallback",
            "task_number": 6,
            "topic": "powers",
            "subtype": "powers_with_fractions",
            "question_text": question_text,
            "answer": _fmt_answer(result),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": "mul",
                    "operands": [
                        {
                            "operation": "mul",
                            "operands": [
                                {"type": "integer", "value": 2, "text": "2"},
                                {"type": "power", "value": None, "text": "(1/2)^2"},
                            ],
                        },
                        {
                            "operation": "mul",
                            "operands": [
                                {"type": "integer", "value": 3, "text": "3"},
                                {"type": "common", "value": [1, 2], "text": "1/2"},
                            ],
                        },
                    ],
                }
            },
            "meta": {"difficulty": "medium", "pattern_id": pattern_id},
        }
    question_text = _ensure_answer_field("Вычисли:\n(10^2 · 0,03) : 10")
    result = 0.3
    return {
        "id": "6_powers_of_ten_fallback",
        "task_number": 6,
        "topic": "powers",
        "subtype": "powers_of_ten",
        "question_text": question_text,
        "answer": _fmt_answer(result),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": "div",
                "operands": [
                    {
                        "operation": "mul",
                        "operands": [
                            {"type": "power10", "value": 2, "text": "10^2"},
                            {"type": "decimal", "value": 0.03, "text": "0,03"},
                        ],
                    },
                    {"type": "power10", "value": 1, "text": "10"},
                ],
            }
        },
        "meta": {"difficulty": "easy", "pattern_id": pattern_id},
    }
