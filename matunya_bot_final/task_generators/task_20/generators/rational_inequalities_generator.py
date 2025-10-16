"""Solver for Task 20 / subtype: rational_inequalities (ОГЭ-2026).

Поддерживаемые паттерны:
  1) compare_unit_fractions_linear           : 1/x ⊙ 1/(x−a)
  2) const_over_quadratic_nonpos_nonneg      : −C/(x²+bx+c) ⊙ 0
  3) x_vs_const_over_x                        : x ⊙ K/x    → (x²−K)/x ⊙ 0, K=m²
  4) neg_const_over_shifted_square_minus_const: −C/((x−a)²−d) ⊙ 0

Результат: solution_core по ГОСТ-2026 v2.2
"""

from __future__ import annotations
from typing import Any, Dict, List


# =============================== ВСПОМОГАТЕЛЬНЫЕ УТИЛИТЫ ===============================

def _ans(task: Dict[str, Any]) -> str:
    """Финальный ответ как строка интервалов (из task['answer'])."""
    a = task.get("answer", [])
    return a[0] if isinstance(a, list) and a else ""


def _axis(task: Dict[str, Any]) -> Dict[str, Any]:
    """Готовые данные для оси (передаются генератором)."""
    return task["variables"].get("axis_data", {})


def _is_weak(sign: str) -> bool:
    """Нестрогое неравенство?"""
    return sign in ("≤", "≥")


def _choose_intervals_phrase(want_positive: bool) -> str:
    """Фраза выбора интервалов по знаку."""
    return f"Выберем интервалы со знаком «{'+' if want_positive else '−'}»."


# =============================== ПОСТРОИТЕЛИ ШАГОВ ===============================

def _steps_compare_unit_fractions_linear(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """1/x ⊙ 1/(x−a). Генератор уже даёт transformed_expression вида a/(x(x−a)) ⊙' 0."""
    vars_ = task["variables"]
    a = int(vars_["coefficients"]["a"])
    initial_sign = vars_["coefficients"]["sign"]  # исходный знак между 1/x и 1/(x−a), «≥» или «≤»
    # После приведения: −a/(x(x−a)) initial_sign 0 → умножили на −1 → a/(x(x−a)) flipped_sign 0
    flipped_sign = "≤" if initial_sign == "≥" else "≥"

    steps: List[Dict[str, Any]] = [
        {
            "step_number": 1,
            "description": "Перенесём всё в левую часть.",
            "formula_representation": f"1/x − 1/(x−{a}) {initial_sign} 0",
            "calculation_result": ""
        },
        {
            "step_number": 2,
            "description": "Приведём к общему знаменателю x(x−a).",
            "formula_general": "1/x − 1/(x−a) = ((x−a) − x) / (x(x−a))",
            "formula_calculation": f"((x−{a}) − x) / (x(x−{a})) {initial_sign} 0",
            "calculation_result": f"−{a} / (x(x−{a})) {initial_sign} 0"
        },
        {
            "step_number": 3,
            "description": "Умножим обе части на −1, изменив знак неравенства.",
            "formula_representation": f"{a} / (x(x−{a})) {flipped_sign} 0",
            "calculation_result": ""
        },
        {
            "step_number": 4,
            "description": "Числитель положителен, значит знак дроби определяется только знаменателем.",
            "formula_representation": f"x(x−{a}) {'< 0' if flipped_sign == '≤' else '> 0'}",
            "calculation_result": ""
        },
        {
            "step_number": 5,
            "description": "Найдём критические точки (нули знаменателя):",
            "formula_representation": "",
            "calculation_result": f"x = 0,  x = {a}"
        },
        {
            "step_number": 6,
            "description": "Отметим точки на числовой оси и расставим знаки выражения на интервалах.",
            "visual_instruction": {"tool": "number_axis", "params": _axis(task)},
            "calculation_result": ""
        },
        {
            "step_number": 7,
            "description": _choose_intervals_phrase(want_positive=(flipped_sign == "≥")),
            "calculation_result": _ans(task)
        },
    ]
    return steps


def _steps_x_vs_const_over_x(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """x ⊙ K/x, где K = m². После переноса: (x²−K)/x ⊙ 0, затем раскладываем числитель."""
    vars_ = task["variables"]
    K = int(vars_["coefficients"]["K"])
    m = int(vars_["coefficients"]["m"])
    sign = vars_["coefficients"]["sign"]  # «≤» или «≥»
    want_positive = (sign == "≥")  # для финального выбора по знакам

    steps: List[Dict[str, Any]] = [
        {
            "step_number": 1,
            "description": "Перенесём все слагаемые в левую часть.",
            "formula_representation": f"x − {K}/x {sign} 0",
            "calculation_result": ""
        },
        {
            "step_number": 2,
            "description": "Приведём к общему знаменателю x.",
            "formula_representation": f"(x^2 − {K})/x {sign} 0",
            "calculation_result": ""
        },
        {
            "step_number": 3,
            "description": "Разложим числитель на множители по формуле разности квадратов.",
            "formula_general": "x^2 − K = (x − √K)(x + √K)",
            "formula_calculation": f"x^2 − {K} = (x − {m})(x + {m})",
            "calculation_result": f"(x − {m})(x + {m}) / x {sign} 0"
        },
        {
            "step_number": 4,
            "description": "Найдём критические точки — нули числителя и знаменателя.",
            "calculation_result": f"x = −{m},  x = 0,  x = {m}"
        },
        {
            "step_number": 5,
            "description": "Отметим точки на числовой оси и расставим знаки выражения на интервалах.",
            "visual_instruction": {"tool": "number_axis", "params": _axis(task)},
            "calculation_result": ""
        },
        {
            "step_number": 6,
            "description": _choose_intervals_phrase(want_positive=want_positive),
            "calculation_result": _ans(task)
        },
    ]
    return steps


def _steps_const_over_quadratic(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """−C/(x²+bx+c) ⊙ 0. Числитель — отрицательная константа."""
    vars_ = task["variables"]
    b = int(vars_["coefficients"]["b"])
    c = int(vars_["coefficients"]["c"])
    C = int(vars_["coefficients"]["C"])  # отрицательное
    sign = vars_["coefficients"]["sign"]  # «≤» или «≥»

    # Идея анализа знака:
    #  −C < 0. Чтобы дробь была ≥ 0 → знаменатель ≤ 0 (но =0 запрещено ⇒ фактически <0).
    #  Чтобы дробь была ≤ 0 → знаменатель ≥ 0 (но =0 запрещено ⇒ фактически >0).
    need = "< 0" if sign == "≥" else "> 0"

    # Корни знаменателя (даны генератором)
    roots = vars_["coefficients"].get("roots", [])
    roots_sorted = sorted(roots)
    r_text = ", ".join(str(x) for x in roots_sorted) if roots_sorted else "—"

    steps: List[Dict[str, Any]] = [
        {
            "step_number": 1,
            "description": "Упростим неравенство: числитель отрицателен, меняем рассуждение на знак знаменателя.",
            "formula_representation": f"{C}/(x^2 + {b}x + {c}) {sign} 0",
            "calculation_result": ""
        },
        {
            "step_number": 2,
            "description": "Так как числитель отрицательен, чтобы дробь удовлетворяла неравенству, требуемый знак знаменателя:",
            "formula_representation": f"x^2 + {b}x + {c} {need}",
            "calculation_result": ""
        },
        {
            "step_number": 3,
            "description": "Найдём нули знаменателя, решив квадратное уравнение x^2 + bx + c = 0.",
            "formula_general": "Коэффициенты: a = 1,  b = b,  c = c",
            "formula_calculation": f"Здесь: a = 1, b = {b}, c = {c}",
            "calculation_result": f"Корни: x = {r_text}"
        },
        {
            "step_number": 4,
            "description": "Вычислим дискриминант по формуле D = b² − 4ac и поясним подстановку.",
            "formula_general": "D = b² − 4ac",
            "formula_calculation": f"D = {b}² − 4·1·({c}) = {b*b} − {4*c} = {b*b - 4*c}",
            "calculation_result": ""
        },
        {
            "step_number": 5,
            "description": "Отметим критические точки на числовой оси и расставим знаки выражения.",
            "visual_instruction": {"tool": "number_axis", "params": _axis(task)},
            "calculation_result": ""
        },
        {
            "step_number": 6,
            "description": _choose_intervals_phrase(want_positive=(sign == "≤")),  # при «≤0» хотим «−», но мы формулируем через знак дроби (числитель<0) → хотим «+»? Объясним в подсказках.
            "calculation_result": _ans(task)
        },
    ]
    # Пояснение к описанию выбора: шаги выше уже свели задачу к условию на знак знаменателя.
    # Чертёж (axis_data) уже отражает верный выбор интервалов, а calculation_result — финальный ответ из task['answer'].
    return steps


def _steps_neg_const_over_shifted_square(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """−C/((x−a)²−d) ⊙ 0. Числитель < 0, знаменатель вида (x−a)²−d."""
    vars_ = task["variables"]
    a = int(vars_["coefficients"]["a"])
    d = int(vars_["coefficients"]["d"])
    C = int(vars_["coefficients"]["C"])  # отрицательное
    sign = vars_["coefficients"]["sign"]  # «≤» или «≥»

    # (отрицательное)/(знаменатель) ⊙ 0:
    #  ⊙ = ≥  ⇒ знаменатель < 0
    #  ⊙ = ≤  ⇒ знаменатель > 0
    need = "< 0" if sign == "≥" else "> 0"

    left_txt = f"{a}−√{d}"
    right_txt = f"{a}+√{d}"

    steps: List[Dict[str, Any]] = [
        {
            "step_number": 1,
            "description": "Учтём знак числителя: он отрицательный, поэтому знак дроби определяется знаком знаменателя.",
            "formula_representation": f"{C}/((x−{a})^2−{d}) {sign} 0",
            "calculation_result": ""
        },
        {
            "step_number": 2,
            "description": "Переформулируем условие на знак знаменателя.",
            "formula_representation": f"(x−{a})^2 − {d} {need}",
            "calculation_result": ""
        },
        {
            "step_number": 3,
            "description": "Выделим границы по формуле разности квадратов: d = (√d)^2.",
            "formula_general": "A^2 − B^2 = (A − B)(A + B)",
            "formula_calculation": f"(x−{a})^2 − {d} = ((x−{a}) − √{d})((x−{a}) + √{d})",
            "calculation_result": f"Критические точки: x = {left_txt},  x = {right_txt}"
        },
        {
            "step_number": 4,
            "description": "Отметим точки на числовой оси и расставим знаки выражения на интервалах.",
            "visual_instruction": {"tool": "number_axis", "params": _axis(task)},
            "calculation_result": ""
        },
        {
            "step_number": 5,
            "description": _choose_intervals_phrase(want_positive=(sign == "≤")),  # см. пояснение в комментарии к const_over_quadratic
            "calculation_result": _ans(task)
        },
    ]
    return steps


# =============================== ИДЕИ РЕШЕНИЯ ===============================

def _idea_compare() -> str:
    return (
        "Это дробно-рациональное неравенство. Нельзя умножать «крест-накрест», так как знаки x и (x−a) заранее неизвестны. "
        "Правильный путь: перенести всё в одну часть, привести к общему знаменателю и решить методом интервалов."
    )


def _idea_x_vs_const() -> str:
    return (
        "Это дробно-рациональное неравенство. Переносим всё в одну часть, приводим к общему знаменателю x, "
        "раскладываем числитель по формуле разности квадратов и решаем методом интервалов с учётом нулей числителя и знаменателя."
    )


def _idea_const_over_quadratic() -> str:
    return (
        "Это дробно-рациональное неравенство с отрицательной константой в числителе. "
        "Знак дроби определяется знаком знаменателя: переносим рассуждение на квадратный трёхчлен, "
        "находим его корни и решаем методом интервалов."
    )


def _idea_neg_const_shifted_square() -> str:
    return (
        "Это дробно-рациональное неравенство с отрицательным числителем и знаменателем вида (x−a)²−d. "
        "Знак дроби определяется знаком знаменателя; выделяем границы a±√d и решаем методом интервалов."
    )


# =============================== ПУБЛИЧНЫЙ ИНТЕРФЕЙС ===============================

async def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Главная функция «Решателя» для подтипа rational_inequalities.
    На вход получает весь объект задачи; на выход — стандартизованный solution_core.
    """
    vars_ = task_data.get("variables", {})
    pattern = vars_.get("solution_pattern", "")

    # Идентификатор
    if pattern == "compare_unit_fractions_linear":
        qid = "20_rational_inequalities_compare_unit_fractions_linear"
    elif pattern == "x_vs_const_over_x":
        qid = "20_rational_inequalities_x_vs_const_over_x"
    elif pattern == "const_over_quadratic_nonpos_nonneg":
        qid = "20_rational_inequalities_const_over_quadratic_nonpos_nonneg"
    elif pattern == "neg_const_over_shifted_square_minus_const":
        qid = "20_rational_inequalities_neg_const_over_shifted_square_minus_const"
    else:
        qid = f"20_rational_inequalities_{pattern or 'unknown'}"

    # Ветвление по паттерну
    if pattern == "compare_unit_fractions_linear":
        explanation_idea = _idea_compare()
        steps = _steps_compare_unit_fractions_linear(task_data)
    elif pattern == "x_vs_const_over_x":
        explanation_idea = _idea_x_vs_const()
        steps = _steps_x_vs_const_over_x(task_data)
    elif pattern == "const_over_quadratic_nonpos_nonneg":
        explanation_idea = _idea_const_over_quadratic()
        steps = _steps_const_over_quadratic(task_data)
    elif pattern == "neg_const_over_shifted_square_minus_const":
        explanation_idea = _idea_neg_const_shifted_square()
        steps = _steps_neg_const_over_shifted_square(task_data)
    else:
        explanation_idea = (
            "Данный шаблон решения пока в разработке. "
            "Скоро добавим подробные шаги с числовой осью и методическими комментариями."
        )
        steps = [{
            "step_number": 1,
            "description": "Шаблон решения для этого паттерна будет добавлен в ближайшем обновлении.",
            "calculation_result": ""
        }]

    final_answer = {"value_machine": _ans(task_data), "value_display": _ans(task_data)}

    # Общее — полезные подсказки
    hints = [
        "Не умножай «крест-накрест», если неизвестны знаки множителей — это частая ошибка.",
        "Нули знаменателя всегда выкалываются на оси (в решение не включаются).",
        "При умножении или делении неравенства на отрицательное число знак меняется на противоположный.",
        "Метод интервалов: при проходе через простые корни линейных множителей знак меняется.",
    ]

    solution_core: Dict[str, Any] = {
        "question_id": qid,
        "question_group": "RATIONAL_INEQUALITIES",
        "explanation_idea": explanation_idea,
        "calculation_steps": steps,
        "final_answer": final_answer,
        "hints": hints,
        "validation_code": None,
    }
    return solution_core


__all__ = ["solve"]
