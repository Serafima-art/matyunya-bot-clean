"""Generator for task 20 radical_equations subtype (ОГЭ-2026)."""

from __future__ import annotations

import random
import math
import uuid
from typing import Any, Dict, List, Tuple


# === 1. Базовые диапазоны ===
ROOT_CANDIDATES = [n for n in range(-9, 10) if n != 0]
LINEAR_COEFFS = [1, 2, 3, -1, -2, -3]


# === 2. Вспомогательные утилиты ===
SUPERSCRIPTS = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
}


def _equation_to_display(equation: str) -> str:
    """Преобразует степени в надстрочные символы для красивого вывода."""
    for k, v in SUPERSCRIPTS.items():
        equation = equation.replace(f"^{k}", v)
    return equation


def _prepare_question_text(equation: str) -> str:
    """Оборачивает уравнение в стандартную инструкцию."""
    return f"Реши уравнение:\n{_equation_to_display(equation)}"


# === 3. Генераторы паттернов ===
def _generate_sum_zero_task() -> Tuple[str, List[str], Dict[str, Any]]:
    """
    Паттерн: √A + √B = 0
    Условие существования решения: подкоренные выражения должны обнуляться одновременно.
    """
    for _ in range(500):
        # 1. Выбираем базовый корень
        common_root = random.choice(ROOT_CANDIDATES)

        # 2. Строим A и B так, чтобы они обнулялись при этом корне
        # A = x² - a²
        a = abs(common_root)
        A_text = f"x^2 - {a**2}"
        A_roots = [a, -a]

        # B = kx² + p*x + q, подбираем так, чтобы B(common_root)=0
        k = random.choice([1, 2])
        p = random.randint(-10, 10)
        q = -(k * common_root**2 + p * common_root)
        B_text = f"{k if k != 1 else ''}x^2 {f'+ {p}x' if p >= 0 else f'- {abs(p)}x'} {f'+ {q}' if q >= 0 else f'- {abs(q)}'}"

        # решаем B(x)=0
        D = p**2 - 4 * k * q
        if D < 0:
            continue
        sqrt_D = math.sqrt(D)
        x1 = round((-p + sqrt_D) / (2 * k), 3)
        x2 = round((-p - sqrt_D) / (2 * k), 3)
        B_roots = sorted([x1, x2])

        # 3. Пересечение корней
        common = sorted(set(B_roots) & set(A_roots))
        if not common:
            continue

        equation = f"√({A_text}) + √({B_text}) = 0"
        answers = [str(x) for x in common]

        variables = {
            "solution_pattern": "sum_zero",
            "radicals": {
                "A": {"text": A_text, "roots": A_roots},
                "B": {"text": B_text, "roots": B_roots},
            },
        }
        return equation, answers, variables

    raise RuntimeError("Failed to generate sum_zero radical equation.")


def _generate_same_radical_cancel_task() -> Tuple[str, List[str], Dict[str, Any]]:
    """
    Паттерн: √A = √B
    Решается приравниванием подкоренных выражений: A = B.
    """
    for _ in range(500):
        # линейные выражения под корнем
        a, b = random.choice(LINEAR_COEFFS), random.randint(-10, 10)
        c, d = random.choice(LINEAR_COEFFS), random.randint(-10, 10)

        if a == c:
            continue

        # вычисляем корень уравнения A=B
        x = round((d - b) / (a - c), 3)
        if abs(x) > 15:
            continue

        A_text = f"{a if a != 1 else ''}x {f'+ {b}' if b >= 0 else f'- {abs(b)}'}"
        B_text = f"{c if c != 1 else ''}x {f'+ {d}' if d >= 0 else f'- {abs(d)}'}"

        equation = f"√({A_text}) = √({B_text})"
        answers = [str(x)]

        variables = {
            "solution_pattern": "same_radical_cancel",
            "radicals": {
                "A": {"text": A_text},
                "B": {"text": B_text},
            },
            "found_roots": [x],
            "extraneous_roots": [],
        }
        return equation, answers, variables

    raise RuntimeError("Failed to generate same_radical_cancel radical equation.")


def _generate_cancel_identical_radicals_task() -> Tuple[str, List[str], Dict[str, Any]]:
    """
    Паттерн: cancel_identical_radicals
    Вид:  x^2 + b x + √(S - x) = √(S - x) + k
    После сокращения одинаковых корней: x^2 + b x - k = 0
    ОДЗ: x <= S
    """
    for _ in range(500):
        # Берём S так, чтобы область определения была x <= S
        S = random.randint(-5, 8)

        # Генерируем два целых корня квадратного уравнения после сокращения
        r1 = random.randint(-9, 9)
        # гарантируем хотя бы один допустимый корень (<= S), чтобы ответ был не пустым
        r1 = min(r1, S)
        r2 = random.randint(-9, 9)

        # коэффициенты для x^2 + b x - k = 0 из суммы/произведения корней
        b = -(r1 + r2)
        k = - (r1 * r2)

        # ограничим величины, чтобы выглядело по-ОГЭшному
        if abs(b) > 12 or abs(k) > 80:
            continue

        # собираем равенство до сокращения
        # LHS: x^2 + b x + √(S - x)
        # RHS: √(S - x) + k
        def _fmt_lin(coeff: int) -> str:
            if coeff == 0:
                return ""
            sign = "+ " if coeff > 0 else "- "
            body = "x" if abs(coeff) == 1 else f"{abs(coeff)}x"
            return f"{sign}{body}"

        def _fmt_const(val: int) -> str:
            if val == 0:
                return "+ 0"
            return f"+ {val}" if val > 0 else f"- {abs(val)}"

        lhs = f"x^2{_fmt_lin(b)} + √({S} - x)"
        rhs = f"√({S} - x) {_fmt_const(k)}".replace("+ -", "- ")
        equation = f"{lhs} = {rhs}"

        # переменные для решателя
        ident_radical = f"{S} - x"
        od_ineq = f"x <= {S}"

        # итоговое квадратное
        coeffs = [-k, b, 1]  # [c, b, a] как в твоих генераторах
        roots = sorted([r1, r2])

        # ответ = корни, удовлетворяющие ОДЗ
        valid = [x for x in roots if x <= S]
        if not valid:
            continue

        answers = [str(x) for x in valid]
        extraneous = [x for x in roots if x > S]

        variables = {
            "solution_pattern": "cancel_identical_radicals",
            "identical_radical": ident_radical,
            "od_inequality": od_ineq,
            "resulting_equation": {
                "text": f"x^2{_fmt_lin(b)} {_fmt_const(-k)} = 0".replace("+ -", "- "),
                "coeffs": coeffs,
                "roots": roots,
            },
            "extraneous_roots": extraneous,
        }

        return equation, answers, variables

    raise RuntimeError("Failed to generate cancel_identical_radicals pattern.")


# === 4. Карта паттернов ===
PATTERN_GENERATORS = {
    "sum_zero": _generate_sum_zero_task,
    "same_radical_cancel": _generate_same_radical_cancel_task,
    "cancel_identical_radicals": _generate_cancel_identical_radicals_task,
}


# === 5. Главная функция ===
def generate_task_20_radical_equations() -> Dict[str, Any]:
    """Генерирует задачу подтипа radical_equations для задания 20 (ОГЭ)."""
    pattern_key = random.choice(list(PATTERN_GENERATORS))
    generator = PATTERN_GENERATORS[pattern_key]
    equation, answers, variables = generator()

    variables.setdefault("solution_pattern", pattern_key)

    # --- защита от копирования оригинальных номеров ОГЭ-2026 ---
    banned_examples = {
        "√(x² − 121) + √(2x² + 23x + 11) = 0",
        "√(3x + 7) = √(2x + 13)",
        "√(x − 2) + √(5 − 2x) = 3",
    }
    if equation in banned_examples:
        # Перегенерируем задание, чтобы избежать совпадений с оригиналом
        return generate_task_20_radical_equations()

    return {
        "id": f"20_radical_equations_{uuid.uuid4().hex[:6]}",
        "task_number": 20,
        "topic": "equations",
        "subtype": "radical_equations",
        "question_text": _prepare_question_text(equation),
        "answer": answers,
        "variables": variables,
    }


__all__ = ["generate_task_20_radical_equations"]
