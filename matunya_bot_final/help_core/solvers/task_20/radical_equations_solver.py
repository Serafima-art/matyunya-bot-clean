"""Solver for task 20 subtype: radical_equations (GOST-2026 compliant)."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Optional
import math
import logging

logger = logging.getLogger(__name__)

_SUBSCRIPT_MAP = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _subscript(index: int) -> str:
    """Return a digit with subscript glyphs: 1 -> ₁."""
    return str(index).translate(_SUBSCRIPT_MAP)


def _extract_equation(question_text: str) -> str:
    """Возвращает строку с уравнением из текста задания (первая строка с '=')."""
    for line in question_text.strip().split("\n"):
        if "=" in line:
            return line.strip()
    return question_text.strip()


def _format_answer_display(answer: Any) -> str:
    """Форматирует финальный ответ для value_display."""
    if isinstance(answer, list):
        if not answer:
            return "Нет решений"
        # ответы уже строки
        return ", ".join([f"x = {item}" for item in answer])
    return f"x = {answer}"


def _format_number(value: float) -> str:
    rounded = round(value)
    if math.isclose(value, rounded, rel_tol=1e-9, abs_tol=1e-9):
        return str(int(rounded))
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    if text == "-0":
        return "0"
    return text


def _normalize_float(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None
    return None


def _parse_linear_expression(expr: str) -> Tuple[float, float]:
    clean = expr.replace(" ", "")
    if "x" not in clean:
        raise ValueError(f"Cannot parse linear expression: {expr!r}")
    coef_part, const_part = clean.split("x", 1)
    if coef_part in ("", "+"):
        coef = 1.0
    elif coef_part == "-":
        coef = -1.0
    else:
        coef = float(coef_part.replace(",", "."))
    const = 0.0
    if const_part:
        const = float(const_part.replace(",", "."))
    return coef, const


def _format_linear_substitution(coef: float, const: float, root_display: str) -> str:
    if math.isclose(coef, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        term = root_display
    elif math.isclose(coef, -1.0, rel_tol=1e-9, abs_tol=1e-9):
        term = f"-{root_display}"
    else:
        term = f"{_format_number(coef)}·{root_display}"

    if math.isclose(const, 0.0, rel_tol=1e-9, abs_tol=1e-9):
        return term

    sign = "+" if const > 0 else "-"
    return f"{term} {sign} {_format_number(abs(const))}"


async def solve(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Построить solution_core для подтипа radical_equations.
    Поддерживаемые паттерны:
      - sum_zero
      - same_radical_cancel
      - cancel_identical_radicals
    """
    logger.info("Task 20 radical_equations solver started")

    variables: Dict[str, Any] = task_data.get("variables", {})
    pattern: str = variables.get("solution_pattern", "")

    if not pattern:
        raise ValueError("variables must contain 'solution_pattern'")

    # общий для пояснений вид исходного уравнения
    equation = _extract_equation(task_data.get("question_text", ""))

    if pattern == "sum_zero":
        steps, explanation, hints = _build_sum_zero_steps(variables, equation)
    elif pattern == "same_radical_cancel":
        steps, explanation, hints = _build_same_radical_cancel_steps(variables, equation)
    elif pattern == "cancel_identical_radicals":
        steps, explanation, hints = _build_cancel_identical_radicals_steps(variables, equation)
    else:
        raise ValueError(f"Unsupported solution pattern: {pattern}")

    # финальный ответ берём из task_data['answer'] (по ГОСТу решатель не искажает «истину из генератора»)
    answer = task_data.get("answer", [])
    value_display = _format_answer_display(answer)
    value_machine = answer if isinstance(answer, list) else [answer]

    solution_core: Dict[str, Any] = {
        # --- БЛОК 1: Идентификация ---
        "question_id": str(task_data.get("id", "radical_equations")),
        "question_group": "RADICAL_EQUATIONS",

        # --- БЛОК 2: Педагогическая часть ---
        "explanation_idea": explanation,

        # --- БЛОК 3: Математическое ядро ---
        "calculation_steps": steps,

        # --- БЛОК 4: Итоговый результат ---
        "final_answer": {
            "value_machine": value_machine,
            "value_display": value_display,
            "unit": None,
        },

        # --- БЛОК 5: Вспомогательная информация ---
        "validation_code": None,
        "hints": hints,
    }

    logger.info("Task 20 radical_equations solver finished")
    return solution_core


# =========================
#  ПАТТЕРН 1: sum_zero
# =========================
def _build_sum_zero_steps(variables: Dict[str, Any], equation: str) -> Tuple[List[Dict], str, List[str]]:
    """
    Паттерн: √A + √B = 0.
    Идея: сумма двух неотрицательных величин равна нулю тогда и только тогда, когда обе равны нулю.
    Входные данные (по контракту):
      variables = {
        "solution_pattern": "sum_zero",
        "radicals": {
          "A": {"text": "...", "roots": [...]},
          "B": {"text": "...", "roots": [...]}
        }
      }
    """
    radicals = variables.get("radicals", {})
    A = radicals.get("A", {})
    B = radicals.get("B", {})
    A_text = A.get("text", "A(x)")
    B_text = B.get("text", "B(x)")
    A_roots = A.get("roots", [])
    B_roots = B.get("roots", [])

    # Пересечение корней (реальные решения)
    common = sorted(set(A_roots).intersection(set(B_roots)))
    A_roots_str = ", ".join([str(r) for r in A_roots]) if A_roots else "—"
    B_roots_str = ", ".join([str(r) for r in B_roots]) if B_roots else "—"
    common_str = ", ".join([str(r) for r in common]) if common else "—"

    steps: List[Dict[str, Any]] = [
        {
            "step_number": 1,
            "description": "Квадратный корень неотрицателен. Сумма неотрицательных выражений равна нулю только при равенстве каждого из них нулю. Запишем равносильную систему:",
            "formula_general": "Если √A + √B = 0, то ⇔ { A = 0; B = 0 }",
            "formula_representation": equation,
            "calculation_result": "Переходим к системе двух уравнений.",
        },
        {
            "step_number": 2,
            "description": "Запишем систему уравнений для подкоренных выражений.",
            "formula_representation": "{ " + f"{A_text} = 0; {B_text} = 0" + " }",
            "calculation_result": "Переходим к поиску общих корней этих уравнений.",
        },
        {
            "step_number": 3,
            "description": "Решаем первое и второе уравнение системы по отдельности.",
            "formula_calculation": f"Корни A=0: {A_roots_str}\nКорни B=0: {B_roots_str}",
            "calculation_result": "Получены множества корней для каждого уравнения.",
        },
        {
            "step_number": 4,
            "description": "Ищем общие корни двух уравнений (подстановка/сравнение множеств).",
            "formula_calculation": f"Общие корни: {common_str}",
            "calculation_result": "Общие решения системы совпадают с решениями исходного уравнения.",
        },
    ]

    explanation = (
        "Так как корни неотрицательны, сумма двух квадратных корней равна нулю только при одновременном равенстве подкоренных выражений нулю. "
        "Решаем систему A=0 и B=0 и берём пересечение их корней."
    )
    hints = [
        "Сумма неотрицательных чисел может быть равна нулю только когда каждое из них равно нулю.",
        "Решите уравнения A=0 и B=0 по отдельности и найдите общие корни.",
        "Не забывайте при необходимости проверять найденные значения подстановкой в исходное уравнение.",
    ]

    return steps, explanation, hints


# =================================
#  ПАТТЕРН 2: same_radical_cancel
# =================================
def _build_same_radical_cancel_steps(variables: Dict[str, Any], equation: str) -> Tuple[List[Dict], str, List[str]]:
    '''
    Паттерн: √A = √B.
    Идея: (при A≥0 и B≥0) имеем A = B; далее проверка на посторонние корни обязательна.
    Входные данные (по контракту):
      variables = {
        "solution_pattern": "same_radical_cancel",
        "radicals": {"A": {"text": "..."}, "B": {"text": "..."}},
        "found_roots": [...],
        "extraneous_roots": [...]
      }
    '''
    radicals = variables.get("radicals", {})
    A_text = radicals.get("A", {}).get("text", "A(x)")
    B_text = radicals.get("B", {}).get("text", "B(x)")
    extraneous = variables.get("extraneous_roots", [])
    found_roots_raw = variables.get("found_roots", [])

    steps: List[Dict[str, Any]] = [
        {
            "step_number": 1,
            "description": "Возведём обе части уравнения в квадрат, чтобы убрать знаки корня.",
            "formula_general": "(√A)² = (√B)² ⇒ A = B (при A ≥ 0, B ≥ 0)",
            "formula_calculation": f"(√({A_text}))² = (√({B_text}))²",
            "calculation_result": f"{A_text} = {B_text}",
        },
        {
            "step_number": 2,
            "description": "Решаем полученное уравнение A = B.",
            "formula_representation": f"{A_text} = {B_text}",
            "calculation_result": "Находим возможные значения x (последующая проверка обязательна).",
        },
    ]

    try:
        coef_a, const_a = _parse_linear_expression(A_text)
        coef_b, const_b = _parse_linear_expression(B_text)
    except ValueError:
        coef_a = const_a = coef_b = const_b = None

    if isinstance(found_roots_raw, list):
        found_roots_list = found_roots_raw
    elif found_roots_raw in (None, ""):
        found_roots_list = []
    else:
        found_roots_list = [found_roots_raw]

    extraneous_numeric = [
        value
        for value in (_normalize_float(item) for item in extraneous)
        if value is not None
    ]

    def root_is_extraneous(candidate: float) -> bool:
        return any(
            math.isclose(candidate, ex, rel_tol=1e-9, abs_tol=1e-9)
            for ex in extraneous_numeric
        )

    details_added = False
    next_step_number = 3

    if coef_a is not None and coef_b is not None and found_roots_list:
        for raw_root in found_roots_list:
            root_value = _normalize_float(raw_root)
            if root_value is None:
                continue

            root_display = _format_number(root_value)
            substitution_left = _format_linear_substitution(coef_a, const_a, root_display)
            substitution_right = _format_linear_substitution(coef_b, const_b, root_display)

            left_value = coef_a * root_value + const_a
            right_value = coef_b * root_value + const_b

            left_display = _format_number(left_value)
            right_display = _format_number(right_value)

            equal_values = math.isclose(left_value, right_value, rel_tol=1e-9, abs_tol=1e-9)
            is_extraneous = (not equal_values) or root_is_extraneous(root_value)

            result_text = (
                "Верное равенство — корень подходит."
                if not is_extraneous
                else "Неверное равенство — корень посторонний."
            )

            steps.append(
                {
                    "step_number": next_step_number,
                    "description": f"Подставляем x = {root_display} и проверяем корни.",
                    "formula_calculation": (
                        f"√({substitution_left}) = √({substitution_right})\n"
                        f"√({left_display}) = √({right_display})"
                    ),
                    "calculation_result": result_text,
                }
            )
            next_step_number += 1
            details_added = True

    if not details_added:
        steps.append(
            {
                "step_number": next_step_number,
                "description": "Подставляем найденные значения в исходное равенство радикалов.",
                "calculation_result": "Детализированная проверка недоступна — не хватает данных о корнях.",
            }
        )

    explanation = (
        "Если √A = √B, то при A≥0 и B≥0 получаем A=B. После возведения в квадрат обязательно выполняем проверку, "
        "так как могли появиться посторонние корни."
    )
    hints = [
        "При равенстве корней квадратов удобно возвести обе части уравнения в квадрат.",
        "Не забудьте проверить найденные значения подстановкой в исходное уравнение.",
        "Следите за областью допустимых значений: подкоренные выражения неотрицательны.",
    ]

    return steps, explanation, hints


# =========================================
#  ПАТТЕРН 3: cancel_identical_radicals
# =========================================
def _build_cancel_identical_radicals_steps(variables: Dict[str, Any], equation: str) -> Tuple[List[Dict], str, List[str]]:
    """
    Паттерн: одинаковый корень стоит в обеих частях уравнения; после переноса — сокращается.
    Далее — равносильный переход к смешанной системе: { уравнение; ОДЗ }.
    Входные данные (по контракту):
      variables = {
        "solution_pattern": "cancel_identical_radicals",
        "identical_radical": "S − x",
        "od_inequality": "x <= S",
        "resulting_equation": {
          "text": "x^2 + ... = 0",
          "coeffs": [c, b, a],
          "roots": [r1, r2]
        },
        "extraneous_roots": [ ... ]
      }
    """
    ident = variables.get("identical_radical", "S − x")
    od_ineq = variables.get("od_inequality", "x <= S")
    req = variables.get("resulting_equation", {})
    req_text = req.get("text", "Q(x) = 0")
    coeffs = req.get("coeffs", [0, 0, 1])  # [c, b, a]
    roots = req.get("roots", [])
    extraneous = variables.get("extraneous_roots", [])

    # Сопроводительные вычисления для красивой подачи (через дискриминант)
    c, b, a = coeffs
    D = b * b - 4 * a * c
    sqrtD: Optional[float] = math.sqrt(D) if D >= 0 else None

    # Неравенство вида: идентичный_подкоренный ≥ 0 → преобразуем к x <= S (у нас уже дано в od_inequality)
    odz_raw = f"{ident} ≥ 0"

    # Корни уравнения:
    roots_str = ", ".join([f"x{_subscript(i+1)} = {roots[i]}" for i in range(len(roots))]) if roots else "—"

    # Отбор по ОДЗ:
    valid_str = ", ".join([str(x) for x in req.get("roots", []) if str(x) not in map(str, extraneous)]) if roots else "—"
    extraneous_str = ", ".join(map(str, extraneous)) if extraneous else "—"

    # Пошагово по "Золотому эталону"
    steps: List[Dict[str, Any]] = [
        {
            "step_number": 1,
            "description": "Перенесём одинаковые корни в одну часть и сократим их, сделав равносильный переход к смешанной системе.",
            "formula_representation": equation,
            "formula_calculation": (
            "----------\n"
            f"+ √({ident})\n"
            f"− √({ident})\n"
            "----------"
        ),
            "calculation_result": "Получим систему: уравнение без радикала и неравенство (ОДЗ) для подкоренного.",
        },
        {
            "step_number": 2,
            "description": "Запишем смешанную систему: уравнение после упрощения и неравенство ОДЗ (область допустимых значений).",
            "formula_calculation": "{ " + f"{req_text}; {odz_raw} " + "}",
            "calculation_result": "ОДЗ гарантирует допустимость значений переменной.",
        },
        {
            "step_number": 3,
            "description": "Решим неравенство (ОДЗ) для подкоренного выражения.",
            "formula_general": f"{ident} ≥ 0",
            "formula_calculation": f"⇔ {od_ineq}",
            "calculation_result": "Получили условие на x из области допустимых значений.",
        },
        {
            "step_number": 4,
            "description": "Решим уравнение системы (квадратное) через дискриминант.",
            "formula_general": "D = b² − 4ac",
            "formula_calculation": f"D = ({b})² − 4·{a}·({c}) = {D}" + (f" = ({int(sqrtD)})²" if sqrtD and float(int(sqrtD)) == sqrtD else ""),
            "calculation_result": (f"Корни: {roots_str}" if roots else "Действительных корней нет."),
        },
        {
            "step_number": 5,
            "description": "Отберём корни с учётом ОДЗ (область допустимых значений).",
            "formula_calculation": f"Допустимые: {valid_str}\nПосторонние (не удовлетворяют ОДЗ): {extraneous_str}",
            "calculation_result": "Исключаем неподходящие значения, оставляем только допустимые.",
        },
    ]

    explanation = (
        "Так как одинаковые корни присутствуют в обеих частях уравнения, после переноса можно их сократить. "
        "Равносильно переходим к смешанной системе из уравнения без радикала и неравенства (ОДЗ). "
        "Далее решаем квадратное уравнение и отбираем корни по ОДЗ (область допустимых значений)."
    )
    hints = [
        "Если одинаковый корень встречается по обе стороны, перенесите и сократите его.",
        "Всегда записывайте ОДЗ (область допустимых значений): подкоренное выражение должно быть неотрицательно.",
        "После решения уравнения обязательно выполните отбор корней по ОДЗ (область допустимых значений).",
    ]

    return steps, explanation, hints


__all__ = ["solve"]
