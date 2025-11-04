# matunya_bot_final/task_generators/task_6/generators/mixed_fractions_generator.py

import random
import uuid
from fractions import Fraction
from typing import Dict, Any, List
import re

from matunya_bot_final.help_core.solvers.task_6.task6_text_formatter import prepare_expression, _fmt, _fmt_answer

def generate_mixed_fractions_tasks(count: int = 10) -> List[Dict[str, Any]]:
    """
    Генератор заданий №6 (Тема 3: смешанные типы — обыкновенные и десятичные дроби).
    """
    # ★★★ ИСПРАВЛЕНО: Имя паттерна теперь соответствует нашей классификации ★★★
    return [_generate_mixed_types_operations("mf_mixed_types_operations") for _ in range(count)]


def _ensure_answer_field(question_text: str) -> str:
    text = question_text.strip()
    if "Ответ" not in text:
        text += "\n\nОтвет: ____________"
    return text


def _generate_mixed_types_operations(pattern_id: str) -> Dict[str, Any]:
    for __retry in range(80):
        for attempt in range(100):
            whole, num, den = _rand_mixed()

            # ★★★ ПРЕОБРАЗОВАНИЕ СМЕШАННОГО ЧИСЛА ★★★
            frac_text = f"{whole} {num}/{den}"
            improper_num = whole * den + num
            improper_den = den
            frac_val = Fraction(improper_num, improper_den)

            dec1 = round(random.uniform(1.0, 8.0), 1)
            dec2 = round(random.uniform(1.0, 8.0), 1)

            form = random.choice(["form1", "form2", "form3", "form4"])
            if form == "form1":
                result = (frac_val - dec1) * frac_val
                expression = f"({frac_text} − {dec1}) · {frac_text}"
                prompt = "Вычисли выражение"
                expr_tree = {
                    "operation": "multiply", # ИСПРАВЛЕНО
                    "operands": [
                        {
                            "operation": "subtract", # ИСПРАВЛЕНО
                            "operands": [
                                {"type": "common", "value": [improper_num, improper_den], "text": frac_text}, # ИСПРАВЛЕНО
                                {"type": "decimal", "value": dec1, "text": str(dec1)},
                            ],
                        },
                        {"type": "common", "value": [improper_num, improper_den], "text": frac_text}, # ИСПРАВЛЕНО
                    ],
                }
            elif form == "form2":
                result = dec1 / frac_val - dec2
                expression = f"{dec1} : {frac_text} − {dec2}"
                prompt = "Выполни вычисления"
                expr_tree = {
                    "operation": "subtract", # ИСПРАВЛЕНО
                    "operands": [
                        {
                            "operation": "divide", # ИСПРАВЛЕНО
                            "operands": [
                                {"type": "decimal", "value": dec1, "text": str(dec1)},
                                {"type": "common", "value": [improper_num, improper_den], "text": frac_text}, # ИСПРАВЛЕНО
                            ],
                        },
                        {"type": "decimal", "value": dec2, "text": str(dec2)},
                    ],
                }
            # ... (Аналогичные исправления для form3 и form4) ...
            else: # form3 и form4 были похожи, унифицируем
                result = dec1 - dec2 / frac_val
                expression = f"{dec1} − {dec2} : {frac_text}"
                prompt = "Найди результат вычислений"
                expr_tree = {
                    "operation": "subtract", # ИСПРАВЛЕНО
                    "operands": [
                        {"type": "decimal", "value": dec1, "text": str(dec1)},
                        {
                            "operation": "divide", # ИСПРАВЛЕНО
                            "operands": [
                                {"type": "decimal", "value": dec2, "text": str(dec2)},
                                {"type": "common", "value": [improper_num, improper_den], "text": frac_text}, # ИСПРАВЛЕНО
                            ],
                        },
                    ],
                }

            if _is_pretty_decimal(float(result)):
                question_text = _ensure_answer_field(f"{prompt}:\n{expression}")
                return {
                    "id": f"6_{pattern_id}_{uuid.uuid4().hex[:6]}",
                    "task_number": 6,
                    "subtype": "mixed_fractions", # ИСПРАВЛЕНО
                    "pattern": pattern_id,       # ИСПРАВЛЕНО
                    "question_text": question_text,
                    "answer": _fmt_answer(float(result)),
                    "answer_type": "decimal",
                    "variables": {"expression_tree": expr_tree},
                    "meta": {"difficulty": "hard", "pattern_id": "3.1"},
                }

    return __safe_fallback_for_this_subtype(pattern_id)


def _rand_mixed() -> tuple[int, int, int]:
    pretty_denominators = [2, 4, 5, 8, 10, 20, 25]
    whole = random.randint(1, 4)
    numerator = random.randint(1, 9)
    denominator = random.choice(pretty_denominators)
    while numerator >= denominator: # Улучшенная логика для правильных дробей
        numerator = random.randint(1, 9)
    return whole, numerator, denominator


def _is_pretty_decimal(value: float) -> bool:
    if value is None or abs(value) > 1_000:
        return False
    # Упрощенная и более надежная проверка
    return abs(value * 1000 - int(value * 1000)) < 1e-9


def __safe_fallback_for_this_subtype(pattern_id: str) -> Dict[str, Any]:
    question_text = _ensure_answer_field("Вычисли выражение:\n(1 1/2 − 1.0) · 1 1/2")
    result = 0.75
    return {
        "id": "6_mixed_types_operations_fallback",
        "task_number": 6,
        "subtype": "mixed_fractions", # ИСПРАВЛЕНО
        "pattern": pattern_id,       # ИСПРАВЛЕНО
        "question_text": question_text,
        "answer": _fmt_answer(result),
        "answer_type": "decimal",
        "variables": {
            "expression_tree": {
                "operation": "multiply", # ИСПРАВЛЕНО
                "operands": [
                    {
                        "operation": "subtract", # ИСПРАВЛЕНО
                        "operands": [
                            {"type": "common", "value": [3, 2], "text": "1 1/2"}, # ИСПРАВЛЕНО
                            {"type": "decimal", "value": 1.0, "text": "1.0"},
                        ],
                    },
                    {"type": "common", "value": [3, 2], "text": "1 1/2"}, # ИСПРАВЛЕНО
                ],
            }
        },
        "meta": {"difficulty": "hard", "pattern_id": "3.1"},
    }
