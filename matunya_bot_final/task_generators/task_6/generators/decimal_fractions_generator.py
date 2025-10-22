import random
import uuid
from typing import Dict, Any, List

from matunya_bot_final.task_generators.task_6.generators.task6_text_formatter import _fmt, _fmt_answer


def generate_decimal_fractions_tasks(count: int = 10) -> List[Dict[str, Any]]:
    """
    Генератор заданий №6 — Тема 2: действия с десятичными дробями.
    Паттерны:
      2.1 — df_addition_subtraction
      2.2 — linear_operations
      2.3 — fraction_structure
    """
    tasks: List[Dict[str, Any]] = []
    patterns = ["2.1", "2.2", "2.3"]

    for _ in range(count):
        pattern_id = random.choice(patterns)
        if pattern_id == "2.1":
            tasks.append(_generate_df_addition_subtraction(pattern_id))
        elif pattern_id == "2.2":
            tasks.append(_generate_linear_operations(pattern_id))
        else:
            tasks.append(_generate_fraction_structure(pattern_id))
    return tasks


# ===============================
# === ПАТТЕРН 2.1 ===============
# ===============================
def _generate_df_addition_subtraction(pattern_id: str) -> Dict[str, Any]:
    a = _nice_decimal(1, 20)
    b = _nice_decimal(1, 20)
    op = random.choice(["add", "sub"])
    result = a + b if op == "add" else a - b
    symbol = "+" if op == "add" else "−"

    question_text = f"Посчитай значение:\n{_fmt(a)} {symbol} {_fmt(b)}\n\nОтвет: ____________"

    return {
    "id": f"6_df_addition_subtraction_{uuid.uuid4().hex[:6]}",
    "task_number": 6,
    "topic": "decimal_fractions",
    "subtype": "df_addition_subtraction",
    "question_text": question_text,
    "answer": _fmt_answer(result, use_comma=True).replace(",", "."),   # для валидатора (точка)
    "display_answer": _fmt_answer(result, use_comma=True),             # для бота (запятая)
    "answer_type": "decimal",
    "variables": {
        "expression_tree": {
            "type": "operation",
            "value": None,
            "text": f"{_fmt(a)} {symbol} {_fmt(b)}",
            "operation": op,
            "operands": [
                {"type": "decimal", "value": a, "text": _fmt(a)},
                {"type": "decimal", "value": b, "text": _fmt(b)},
            ],
        }
    },
    "meta": {"difficulty": "easy", "pattern_id": pattern_id},
}


# ===============================
# === ПАТТЕРН 2.2 ===============
# ===============================
def _generate_linear_operations(pattern_id: str) -> Dict[str, Any]:
    a = random.randint(-6, 6)
    while a == 0:
        a = random.randint(-6, 6)
    b = _nice_decimal(-10, 10)
    c = _nice_decimal(-10, 10)
    op = random.choice(["add", "sub"])

    result = a * b + c if op == "add" else a * b - c
    symbol = "+" if op == "add" else "−"

    # --- форматируем красиво ---
    def _wrap(x: float) -> str:
        """Возвращает число с запятой, обёрнутое в скобки только если отрицательное."""
        fx = _fmt(x)
        return f"({fx})" if x < 0 else fx

    a_fmt = _wrap(a)
    b_fmt = _wrap(b)
    c_fmt = _wrap(c)

    expr = f"{a_fmt}·{b_fmt} {symbol} {c_fmt}"
    question_text = f"Вычисли выражение:\n{expr}\n\nОтвет: ____________"

    return {
        "id": f"6_linear_operations_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "decimal_fractions",
        "subtype": "linear_operations",
        "question_text": question_text,
        "answer": _fmt_answer(result, use_comma=True).replace(",", "."),
        "display_answer": _fmt_answer(result, use_comma=True),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": op,
                "operands": [
                    {
                        "type": "operation",
                        "value": None,
                        "text": f"{a_fmt}·{b_fmt}",
                        "operation": "mul",
                        "operands": [
                            {"type": "integer", "value": a, "text": a_fmt},
                            {"type": "decimal", "value": b, "text": b_fmt},
                        ],
                    },
                    {"type": "decimal", "value": c, "text": c_fmt},
                ],
            }
        },
        "meta": {"difficulty": "medium", "pattern_id": pattern_id},
    }


# ===============================
# === ПАТТЕРН 2.3 ===============
# ===============================
def _generate_fraction_structure(pattern_id: str) -> Dict[str, Any]:
    a = _nice_decimal(2, 20)
    b = _nice_decimal(1, 15)
    c = _nice_decimal(1, 15)
    mode = random.choice(["add_sub", "mul"])

    if mode == "add_sub":
        inner_op = random.choice(["add", "sub"])
        inner_symbol = "+" if inner_op == "add" else "−"
        denominator = b + c if inner_op == "add" else b - c
        if abs(denominator) < 1e-6:
            denominator = _nice_decimal(1, 5)
        result = a / denominator
        inner_expr = {
            "operation": inner_op,
            "operands": [
                {"type": "decimal", "value": b, "text": _fmt(b)},
                {"type": "decimal", "value": c, "text": _fmt(c)},
            ],
        }
        inner_text = f"{_fmt(b)} {inner_symbol} {_fmt(c)}"
    else:
        denominator = b * c
        if abs(denominator) < 1e-6:
            denominator = _nice_decimal(1, 5)
        result = a / denominator
        inner_expr = {
            "operation": "mul",
            "operands": [
                {"type": "decimal", "value": b, "text": _fmt(b)},
                {"type": "decimal", "value": c, "text": _fmt(c)},
            ],
        }
        inner_text = f"{_fmt(b)} · {_fmt(c)}"

    question_text = f"Посчитай значение дроби:\n{_fmt(a)} / ({inner_text})\n\nОтвет: ____________"

    return {
    "id": f"6_fraction_structure_{uuid.uuid4().hex[:6]}",
    "task_number": 6,
    "topic": "decimal_fractions",
    "subtype": "fraction_structure",
    "question_text": question_text,
    "answer": _fmt_answer(result, use_comma=True).replace(",", "."),   # для валидатора (точка)
    "display_answer": _fmt_answer(result, use_comma=True),             # для бота (запятая)
    "answer_type": "decimal",
    "variables": {
        "expression_tree": {
            "operation": "div",
            "operands": [
                {"type": "decimal", "value": a, "text": _fmt(a)},
                {
                    "type": "operation",
                    "value": None,
                    "text": (
                        f"{_fmt(b)} {'+' if mode == 'add_sub' and inner_op == 'add' else '−' if mode == 'add_sub' and inner_op == 'sub' else '·'} {_fmt(c)}"
                    ),
                    "operation": (
                        inner_op if mode == "add_sub" else "mul"
                    ),
                    "operands": [
                        {"type": "decimal", "value": b, "text": _fmt(b)},
                        {"type": "decimal", "value": c, "text": _fmt(c)},
                    ],
                },
            ],
        }
    },
    "meta": {"difficulty": "hard", "pattern_id": pattern_id},
}

# ===============================
# === ВСПОМОГАТЕЛЬНЫЕ ===========
# ===============================

def _nice_decimal(min_val: float, max_val: float) -> float:
    """Генерирует «красивые» конечные десятичные дроби с максимум 2 знаками."""
    # 0.1–0.9 шагом 0.1, чтобы всегда было конечное представление
    val = random.randint(int(min_val * 10), int(max_val * 10)) / 10
    # избегаем периодических, всегда 1 знак после запятой
    return round(val, 1)
