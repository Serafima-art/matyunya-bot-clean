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
    patterns = ["p_powers_with_fractions", "p_powers_of_ten"]
    for _ in range(count):
        pattern_id = random.choice(patterns)
        if pattern_id == "p_powers_with_fractions":
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
        op = random.choice(["add", "subtract"])

        frac = Fraction(a, b)
        power_val = frac ** 2
        result = n * power_val + k * frac if op == "add" else n * power_val - k * frac

        attempts = 0
        while not _is_pretty_decimal(result) and attempts < 100:
            n, a, b = random.randint(3, 30), random.randint(1, 5), random.choice([2, 4, 5, 7, 8, 10])
            k = random.randint(1, 25)
            op = random.choice(["add", "subtract"])
            frac = Fraction(a, b)
            power_val = frac ** 2
            result = n * power_val + k * frac if op == "add" else n * power_val - k * frac
            attempts += 1

        text_op = "+" if op == "add" else "−"
        expression = f"{n}·({a}/{b})² {text_op} {k}·{a}/{b}"
        question_text = _ensure_answer_field(f"Вычисли значение выражения:\n{expression}")

        return {
            "id": f"6_{pattern_id}_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "subtype": "powers",
            "pattern": pattern_id,
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": op,
                    "operands": [
                        {
                            "operation": "multiply",
                            "operands": [
                                {"type": "common", "value": [n, 1], "text": str(n)},
                                {
                                    "operation": "power",
                                    "operands": [
                                        {"type": "common", "value": [a, b], "text": f"{a}/{b}"},
                                        {"type": "common", "value": [2, 1], "text": "2"},
                                    ],
                                },
                            ],
                        },
                        {
                            "operation": "multiply",
                            "operands": [
                                {"type": "common", "value": [k, 1], "text": str(k)},
                                {"type": "common", "value": [a, b], "text": f"{a}/{b}"},
                            ],
                        },
                    ],
                }
            },
            "meta": {"difficulty": "medium", "pattern_id": "4.1"},
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

        # 🧩 анти-дубликат — проверяем, чтобы не повторялись одинаковые комбинации
        if hasattr(_generate_powers_of_ten, "_used_combos"):
            prev = _generate_powers_of_ten._used_combos
        else:
            prev = set()
            _generate_powers_of_ten._used_combos = prev

        combo = (base1, exp1, outer_pow, base2, exp2)
        if combo in prev:
            continue  # повтор — пробуем заново
        prev.add(combo)
        # 🧩 конец анти-дубликата

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

        # --- Формируем красивое выражение со степенями ---
        def _to_superscript(n: int) -> str:
            """Преобразует число в надстрочную запись: 2 → ², -3 → ⁻³"""
            n = int(n)
            mapping = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
            return str(n).translate(mapping)

        exp1_sup = _to_superscript(exp1)
        exp2_sup = _to_superscript(exp2)

        # стало красиво: (4·10⁵)³·(2·10⁻¹)
        outer_pow_sup = _to_superscript(outer_pow)
        expression = f"({base1}·10{exp1_sup}){outer_pow_sup}·({base2}·10{exp2_sup})"
        expression = expression.replace("10¹", "10")  # 10¹ → 10

        # fallback, если по какой-то причине строка пустая
        if not expression:
            expression = "(10²)·(10⁻³)"

        # форматирование (если prepare_expression вернет None — берём сырую строку)
        formatted_expr = prepare_expression(expression) or expression

        question_text = _ensure_answer_field(f"Вычисли выражение:\n{formatted_expr}")

        return {
            "id": f"6_{pattern_id}_{uuid.uuid4().hex[:6]}",
            "task_number": 6,
            "subtype": "powers",
            "pattern": pattern_id,
            "question_text": question_text,
            "answer": _fmt_answer(float(result)),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": "multiply",
                    "operands": [
                        {
                            "operation": "power",
                            "operands": [
                                {
                                    "operation": "multiply",
                                    "operands": [
                                        {"type": "decimal", "value": float(base1), "text": str(base1)},
                                        {
                                            "operation": "power",
                                            "operands": [
                                                {"type": "decimal", "value": 10.0, "text": "10"},
                                                {"type": "decimal", "value": float(exp1), "text": str(exp1)}
                                            ]
                                        },
                                    ],
                                },
                                {"type": "decimal", "value": float(outer_pow), "text": str(outer_pow)},
                            ],
                        },
                        {
                            "operation": "multiply",
                            "operands": [
                                {"type": "decimal", "value": float(base2), "text": str(base2)},
                                {
                                    "operation": "power",
                                    "operands": [
                                        {"type": "decimal", "value": 10.0, "text": "10"},
                                        {"type": "decimal", "value": float(exp2), "text": str(exp2)}
                                    ]
                                },
                            ],
                        },
                    ],
                }
            },
            "meta": {"difficulty": "hard", "pattern_id": "4.2"},
        }

    # --- fallback если 80 попыток не дали красивое число ---
    fallback_examples = [
        ("(5·10²)²·(2·10⁻³)", 500),
        ("(3·10³)·(4·10⁻⁴)", 1.2),
        ("(8·10²)·(6·10⁻³)", 4.8),
        ("(2·10³)·(7·10⁻²)", 140),
        ("(6·10²)²·(5·10⁻³)", 10800),
        ("(9·10²)·(2·10⁻³)", 1.8),
        ("(4·10³)·(3·10⁻²)", 120),
        ("(7·10²)²·(2·10⁻³)", 19600),
        ("(3·10³)·(5·10⁻³)", 15),
        ("(2·10²)³·(8·10⁻³)", 6400),
        ("(9·10²)·(6·10⁻³)", 5.4),
        ("(4·10³)·(3·10⁻³)", 12),
        ("(8·10²)²·(2·10⁻³)", 25600),
        ("(6·10³)·(5·10⁻³)", 30),
        ("(2·10²)³·(4·10⁻³)", 3200),
    ]

    expr, result = random.choice(fallback_examples)
    question_text = _ensure_answer_field(f"Вычисли выражение:\n{expr}")

    return {
        "id": f"6_{pattern_id}_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "subtype": "powers",
        "pattern": pattern_id,
        "question_text": question_text,
        "answer": _fmt_answer(float(result)),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": "multiply",
                "operands": [
                    {"type": "decimal", "value": 1.0, "text": "1"},  # фиктивный узел
                ],
            },
        },
        "meta": {"difficulty": "medium", "pattern_id": "4.2"},
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


def __safe_fallback_for_this_subtype(pattern_id: str) -> Dict[str, Any]:
    if pattern_id == "p_powers_with_fractions":
        question_text = _ensure_answer_field("Выполни вычисление:\n2·(1/2)^2 · 3·1/2")
        result = 0.75
        return {
            "id": "6_p_powers_with_fractions_fallback",
            "task_number": 6,
            "subtype": "powers",
            "pattern": "p_powers_with_fractions",
            "question_text": question_text,
            "answer": _fmt_answer(result),
            "answer_type": "decimal",
            "variables": {
                "expression_tree": {
                    "operation": "multiply",
                    "operands": [
                        {
                            "operation": "multiply",
                            "operands": [
                                {"type": "common", "value": [2, 1], "text": "2"},
                                {
                                    "operation": "power",
                                    "operands": [
                                        {"type": "common", "value": [1, 2], "text": "1/2"},
                                        {"type": "common", "value": [2, 1], "text": "2"},
                                    ],
                                },
                            ],
                        },
                        {
                            "operation": "multiply",
                            "operands": [
                                {"type": "common", "value": [3, 1], "text": "3"},
                                {"type": "common", "value": [1, 2], "text": "1/2"},
                            ],
                        },
                    ],
                }
            },
            "meta": {"difficulty": "medium", "pattern_id": "4.1"},
        }
    question_text = _ensure_answer_field("Вычисли:\n(10^2 · 0,03) : 10")
    result = 0.3
    return {
        "id": "6_p_powers_of_ten_fallback",
        "task_number": 6,
        "subtype": "powers",
        "pattern": "p_powers_of_ten",
        "question_text": question_text,
        "answer": _fmt_answer(result),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": "divide",
                "operands": [
                    {
                        "operation": "multiply",
                        "operands": [
                            {
                                "operation": "power",
                                "operands": [
                                    {"type": "decimal", "value": 10.0, "text": "10"},
                                    {"type": "decimal", "value": 2.0, "text": "2"}
                                ]
                            },
                            {"type": "decimal", "value": 0.03, "text": "0,03"},
                        ],
                    },
                    {
                        "operation": "power",
                        "operands": [
                            {"type": "decimal", "value": 10.0, "text": "10"},
                            {"type": "decimal", "value": 1.0, "text": "1"}
                        ]
                    },
                ],
            }
        },
        "meta": {"difficulty": "easy", "pattern_id": "4.2"},
    }
