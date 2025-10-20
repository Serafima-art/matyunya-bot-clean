import random
import uuid
from fractions import Fraction
from typing import Dict, Any, List
import re


def generate_mixed_fractions_tasks(count: int = 10) -> List[Dict[str, Any]]:
    """
    Генератор заданий №6 (Тема 3: смешанные типы — обыкновенные и десятичные дроби).
    Поддерживает единственный подтип 3.1 (mixed_types_operations).
    """
    return [_generate_mixed_types_operations("3.1") for _ in range(count)]


def _ensure_answer_field(question_text: str) -> str:
    text = question_text.strip()
    if "Ответ" not in text:
        text += "\n\nОтвет: ____________"
    return text


def _generate_mixed_types_operations(pattern_id: str) -> Dict[str, Any]:
    for attempt in range(100):
        whole, num, den = _rand_mixed()
        frac_val = Fraction(whole * den + num, den)
        dec1 = round(random.uniform(1.0, 8.0), 1)
        dec2 = round(random.uniform(1.0, 8.0), 1)

        form = random.choice(["form1", "form2", "form3", "form4"])
        if form == "form1":
            result = (frac_val - dec1) * frac_val
            question_text = f"Вычисли выражение:\n({whole} {num}/{den} − {dec1}) · {whole} {num}/{den}"
            expr_str = question_text
            if re.search(r"(^|[^0-9])0[.,]?\d*", expr_str) or "/0" in expr_str:
                return generate_mixed_fractions_tasks(1)[0]
            expr_tree = {
                "operation": "mul",
                "operands": [
                    {
                        "operation": "sub",
                        "operands": [
                            {"type": "mixed", "value": [whole, num, den], "text": f"{whole} {num}/{den}"},
                            {"type": "decimal", "value": dec1, "text": str(dec1)},
                        ],
                    },
                    {"type": "mixed", "value": [whole, num, den], "text": f"{whole} {num}/{den}"},
                ],
            }
        elif form == "form2":
            result = dec1 / frac_val - dec2
            question_text = f"Выполни вычисления:\n{dec1} : {whole} {num}/{den} − {dec2}"
            expr_str = question_text
            if re.search(r"(^|[^0-9])0[.,]?\d*", expr_str) or "/0" in expr_str:
                return generate_mixed_fractions_tasks(1)[0]
            expr_tree = {
                "operation": "sub",
                "operands": [
                    {
                        "operation": "div",
                        "operands": [
                            {"type": "decimal", "value": dec1, "text": str(dec1)},
                            {"type": "mixed", "value": [whole, num, den], "text": f"{whole} {num}/{den}"},
                        ],
                    },
                    {"type": "decimal", "value": dec2, "text": str(dec2)},
                ],
            }
        elif form == "form3":
            result = dec1 - dec2 / frac_val
            question_text = f"Найди результат вычислений:\n{dec1} − {dec2} : {whole} {num}/{den}"
            expr_str = question_text
            if re.search(r"(^|[^0-9])0[.,]?\d*", expr_str) or "/0" in expr_str:
                return generate_mixed_fractions_tasks(1)[0]
            expr_tree = {
                "operation": "sub",
                "operands": [
                    {"type": "decimal", "value": dec1, "text": str(dec1)},
                    {
                        "operation": "div",
                        "operands": [
                            {"type": "decimal", "value": dec2, "text": str(dec2)},
                            {"type": "mixed", "value": [whole, num, den], "text": f"{whole} {num}/{den}"},
                        ],
                    },
                ],
            }
        else:
            result = dec1 / frac_val - dec2
            question_text = f"Посчитай значение выражения:\n{dec1} : {whole} {num}/{den} − {dec2}"
            expr_str = question_text
            if re.search(r"(^|[^0-9])0[.,]?\d*", expr_str) or "/0" in expr_str:
                return generate_mixed_fractions_tasks(1)[0]
            expr_tree = {
                "operation": "sub",
                "operands": [
                    {
                        "operation": "div",
                        "operands": [
                            {"type": "decimal", "value": dec1, "text": str(dec1)},
                            {"type": "mixed", "value": [whole, num, den], "text": f"{whole} {num}/{den}"},
                        ],
                    },
                    {"type": "decimal", "value": dec2, "text": str(dec2)},
                ],
            }

        if _is_pretty_decimal(float(result)):
            question_text = _ensure_answer_field(question_text)
            return {
                "id": f"6_mixed_types_operations_{uuid.uuid4().hex[:6]}",
                "task_number": 6,
                "topic": "mixed_fractions",
                "subtype": "mixed_types_operations",
                "question_text": question_text,
                "answer": str(round(float(result), 3)),
                "answer_type": "decimal",
                "variables": {"expression_tree": expr_tree},
                "meta": {"difficulty": "hard", "pattern_id": pattern_id},
            }

    # Fallback: возвращаем последнее с добавлением поля ответа
    question_text = _ensure_answer_field(question_text)
    return {
        "id": f"6_mixed_types_operations_{uuid.uuid4().hex[:6]}",
        "task_number": 6,
        "topic": "mixed_fractions",
        "subtype": "mixed_types_operations",
        "question_text": question_text,
        "answer": str(round(float(result), 3)),
        "answer_type": "decimal",
        "variables": {"expression_tree": expr_tree},
        "meta": {"difficulty": "hard", "pattern_id": pattern_id},
    }


def _rand_mixed() -> tuple[int, int, int]:
    pretty_denominators = [2, 4, 5, 8, 10, 20, 25]
    whole = random.randint(1, 4)
    numerator = random.randint(1, 9)
    denominator = random.choice(pretty_denominators)
    while numerator == denominator:
        numerator = random.randint(1, 9)
    return whole, numerator, denominator


def _is_pretty_decimal(value: float) -> bool:
    if value is None or abs(value) > 1_000:
        return False
    s = f"{abs(value):.6f}".rstrip("0").rstrip(".")
    return len(s.split(".")[-1]) <= 3
