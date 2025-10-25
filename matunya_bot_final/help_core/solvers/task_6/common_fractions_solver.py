"""
Решатель для подтипа 'common_fractions' (Задание 6).
Теперь соответствует педагогическому стандарту ГОСТ-2026.
Каждый шаг содержит объяснение смысла действий, а не просто формулы.
"""

from fractions import Fraction
from typing import Dict, List, Any
import math

# =============================================================================
# ★★★ ГЛАВНАЯ ФУНКЦИЯ ★★★
# =============================================================================

def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Универсальный решатель подтипа 'common_fractions'.
    Возвращает пошаговое педагогическое решение по ГОСТ-2026.
    """
    expression_tree = task_data.get("variables", {}).get("expression_tree")
    if not expression_tree:
        raise ValueError("Отсутствует 'expression_tree' в task_data")

    steps: List[Dict[str, Any]] = []
    step_counter = [1]

    final_fraction = _evaluate_tree(expression_tree, steps, step_counter)
    _add_decimal_conversion_step(final_fraction, steps, step_counter)

    return {
        "question_id": task_data.get("id", "placeholder_id"),
        "question_group": "TASK6_COMMON",
        "explanation_idea": _generate_explanation_idea(),
        "calculation_steps": steps,
        "final_answer": {
            "value_machine": float(final_fraction),
            "value_display": str(float(final_fraction))
        },
        "hints": _generate_hints()
    }

# =============================================================================
# ★★★ РЕКУРСИВНЫЙ ДВИЖОК ★★★
# =============================================================================

def _evaluate_tree(node: Dict[str, Any], steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Рекурсивно вычисляет выражение и добавляет пошаговые действия."""
    if node.get("type") == "common":
        n, d = node["value"]
        return Fraction(n, d)

    operation = node["operation"]
    left = _evaluate_tree(node["operands"][0], steps, step_counter)
    right = _evaluate_tree(node["operands"][1], steps, step_counter)

    return _perform_operation(operation, left, right, steps, step_counter)

# =============================================================================
# ★★★ ВЫБОР ОПЕРАЦИИ ★★★
# =============================================================================

def _perform_operation(op: str, left: Fraction, right: Fraction,
                       steps: List[Dict], step_counter: List[int]) -> Fraction:
    if op == "add":
        return _perform_addition(left, right, steps, step_counter)
    elif op == "subtract":
        return _perform_subtraction(left, right, steps, step_counter)
    elif op == "multiply":
        return _perform_multiplication(left, right, steps, step_counter)
    elif op == "divide":
        return _perform_division(left, right, steps, step_counter)
    else:
        raise ValueError(f"Неизвестная операция: {op}")

# =============================================================================
# ★★★ 1. СЛОЖЕНИЕ ДРОБЕЙ ★★★
# =============================================================================

def _perform_addition(left: Fraction, right: Fraction,
                     steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Пошаговое сложение обыкновенных дробей по ГОСТ-2026."""

    # Шаг 1. Нахождение НОЗ
    noz = _lcm(left.denominator, right.denominator)
    description_1 = (
        f"Найдём наименьший общий знаменатель (НОЗ) для знаменателей {left.denominator} и {right.denominator}. "
        f"НОЗ — это наименьшее число, которое делится и на {left.denominator}, и на {right.denominator} без остатка. "
        "Это нужно, чтобы сделать знаменатели одинаковыми и можно было сложить дроби. "
        f"НОЗ({left.denominator}, {right.denominator}) = {noz}."
    )
    steps.append({
        "step_number": step_counter[0],
        "description": description_1,
        "formula_representation": f"{_format_fraction(left)} + {_format_fraction(right)}",
        "formula_calculation": f"НОЗ({left.denominator}, {right.denominator}) = {noz}",
        "calculation_result": str(noz)
    })
    step_counter[0] += 1

    # Шаг 2. Приведение и сложение
    lm, rm = noz // left.denominator, noz // right.denominator
    ln, rn = left.numerator * lm, right.numerator * rm
    raw_num = ln + rn
    raw_frac = Fraction(raw_num, noz)

    description_2 = (
        f"Приведём дроби к общему знаменателю {noz}. "
        f"Домножим первую дробь на {lm}, а вторую — на {rm}, "
        "чтобы получить одинаковые знаменатели, и сложим числители."
    )
    formula_2 = (
        f"({left.numerator}·{lm})/({left.denominator}·{lm}) + "
        f"({right.numerator}·{rm})/({right.denominator}·{rm}) = "
        f"{ln}/{noz} + {rn}/{noz} = {raw_num}/{noz}"
    )
    steps.append({
        "step_number": step_counter[0],
        "description": description_2,
        "formula_representation": f"{_format_fraction(left)} + {_format_fraction(right)}",
        "formula_calculation": formula_2,
        "calculation_result": f"{raw_num}/{noz}"
    })
    step_counter[0] += 1

    # Шаг 3. Сокращение
    g = math.gcd(raw_num, noz)
    if g > 1:
        simplified = Fraction(raw_num, noz)
        description_3 = f"Сократим полученную дробь на {g}, чтобы сделать её проще."
        formula_3 = f"{raw_num}/{noz} = {simplified.numerator}/{simplified.denominator}"
        steps.append({
            "step_number": step_counter[0],
            "description": description_3,
            "formula_representation": f"{raw_num}/{noz}",
            "formula_calculation": formula_3,
            "calculation_result": _format_fraction(simplified)
        })
        step_counter[0] += 1
        return simplified
    return raw_frac

# =============================================================================
# ★★★ 2. ВЫЧИТАНИЕ ДРОБЕЙ ★★★
# =============================================================================

def _perform_subtraction(left: Fraction, right: Fraction,
                        steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Пошаговое вычитание обыкновенных дробей по ГОСТ-2026."""

    # Шаг 1. НОЗ
    noz = _lcm(left.denominator, right.denominator)
    description_1 = (
        f"Найдём наименьший общий знаменатель (НОЗ) для знаменателей {left.denominator} и {right.denominator}. "
        f"НОЗ — это наименьшее число, которое делится и на {left.denominator}, и на {right.denominator} без остатка. "
        "Это нужно, чтобы сделать знаменатели одинаковыми и можно было вычесть дроби. "
        f"НОЗ({left.denominator}, {right.denominator}) = {noz}."
    )
    steps.append({
        "step_number": step_counter[0],
        "description": description_1,
        "formula_representation": f"{_format_fraction(left)} - {_format_fraction(right)}",
        "formula_calculation": f"НОЗ({left.denominator}, {right.denominator}) = {noz}",
        "calculation_result": str(noz)
    })
    step_counter[0] += 1

    # Шаг 2. Приведение и вычитание
    lm, rm = noz // left.denominator, noz // right.denominator
    ln, rn = left.numerator * lm, right.numerator * rm
    raw_num = ln - rn
    raw_frac = Fraction(raw_num, noz)

    description_2 = (
        f"Приведём дроби к общему знаменателю {noz}. "
        f"Домножим первую дробь на {lm}, а вторую — на {rm}, "
        "чтобы получить одинаковые знаменатели, и выполним вычитание числителей."
    )
    formula_2 = (
        f"({left.numerator}·{lm})/({left.denominator}·{lm}) - "
        f"({right.numerator}·{rm})/({right.denominator}·{rm}) = "
        f"{ln}/{noz} - {rn}/{noz} = {raw_num}/{noz}"
    )
    steps.append({
        "step_number": step_counter[0],
        "description": description_2,
        "formula_representation": f"{_format_fraction(left)} - {_format_fraction(right)}",
        "formula_calculation": formula_2,
        "calculation_result": f"{raw_num}/{noz}"
    })
    step_counter[0] += 1

    # Шаг 3. Сокращение
    g = math.gcd(abs(raw_num), noz)
    if g > 1:
        simplified = Fraction(raw_num, noz)
        description_3 = f"Сократим полученную дробь на {g}, чтобы сделать её проще."
        formula_3 = f"{raw_num}/{noz} = {simplified.numerator}/{simplified.denominator}"
        steps.append({
            "step_number": step_counter[0],
            "description": description_3,
            "formula_representation": f"{raw_num}/{noz}",
            "formula_calculation": formula_3,
            "calculation_result": _format_fraction(simplified)
        })
        step_counter[0] += 1
        return simplified
    return raw_frac

# =============================================================================
# ★★★ 3. УМНОЖЕНИЕ ★★★
# =============================================================================

def _perform_multiplication(left: Fraction, right: Fraction,
                           steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Пошаговое умножение дробей по ГОСТ-2026."""
    result_num = left.numerator * right.numerator
    result_den = left.denominator * right.denominator
    result = Fraction(result_num, result_den)

    description = (
        "Перемножим дроби: умножаем числители друг на друга и знаменатели друг на друга. "
        "После этого проверяем, можно ли сократить результат."
    )
    formula = f"({left.numerator}·{right.numerator})/({left.denominator}·{right.denominator}) = {result_num}/{result_den}"

    if result.numerator != result_num or result.denominator != result_den:
        formula += f" = {_format_fraction(result)}"

    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": f"{_format_fraction(left)} · {_format_fraction(right)}",
        "formula_calculation": formula,
        "calculation_result": _format_fraction(result)
    })
    step_counter[0] += 1
    return result

# =============================================================================
# ★★★ 4. ДЕЛЕНИЕ ★★★
# =============================================================================

def _perform_division(left: Fraction, right: Fraction,
                     steps: List[Dict], step_counter: List[int]) -> Fraction:
    """Пошаговое деление дробей по ГОСТ-2026."""
    description = (
        f"Чтобы разделить дробь {_format_fraction(left)} на {_format_fraction(right)}, "
        "нужно умножить первую дробь на перевёрнутую вторую дробь."
    )
    flipped = Fraction(right.denominator, right.numerator)
    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": f"{_format_fraction(left)} : {_format_fraction(right)}",
        "formula_calculation": f"{_format_fraction(left)} · {flipped.numerator}/{flipped.denominator}",
        "calculation_result": ""
    })
    step_counter[0] += 1

    result_num = left.numerator * flipped.numerator
    result_den = left.denominator * flipped.denominator
    result = Fraction(result_num, result_den)

    steps.append({
        "step_number": step_counter[0],
        "description": "Перемножаем числители и знаменатели, затем сокращаем, если возможно.",
        "formula_representation": f"{_format_fraction(left)} · {flipped.numerator}/{flipped.denominator}",
        "formula_calculation": f"({left.numerator}·{flipped.numerator})/({left.denominator}·{flipped.denominator}) = {_format_fraction(result)}",
        "calculation_result": _format_fraction(result)
    })
    step_counter[0] += 1
    return result

# =============================================================================
# ★★★ ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ★★★
# =============================================================================

def _add_decimal_conversion_step(frac: Fraction, steps: List[Dict], step_counter: List[int]) -> None:
    """Финальный шаг — преобразование результата в десятичную дробь."""
    val = float(frac)
    description = (
        "Так как ответ в бланке ОГЭ записывается в виде десятичного числа, "
        "преобразуем полученную дробь."
    )
    steps.append({
        "step_number": step_counter[0],
        "description": description,
        "formula_representation": _format_fraction(frac),
        "formula_calculation": f"{_format_fraction(frac)} = {val}",
        "calculation_result": str(val)
    })
    step_counter[0] += 1

def _format_fraction(fr: Fraction) -> str:
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"

def _lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)

def _generate_explanation_idea() -> str:
    return "Чтобы решить выражение с дробями, нужно выполнять действия по порядку: сначала найти НОЗ, затем привести дроби, выполнить действие и, если нужно, сократить результат."

def _generate_hints() -> List[str]:
    return [
        "При сложении и вычитании дробей находите наименьший общий знаменатель (НОЗ).",
        "Домножайте дроби, чтобы сделать знаменатели одинаковыми.",
        "При делении на дробь умножайте на перевёрнутую дробь.",
        "После каждого действия проверяйте, можно ли сократить результат."
    ]
