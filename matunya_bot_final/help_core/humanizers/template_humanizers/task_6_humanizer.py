"""Формирование человеко-понятного объяснения для решения дробей (задание 6)."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


# ---------------------------------------------------------------------------
# Шаблоны для описаний шагов
# ---------------------------------------------------------------------------

STEP_TEMPLATES: Dict[str, str] = {
    "INITIAL_EXPRESSION": "{ctx}Рассматриваем исходное выражение.",
    "FIND_LCM": "{ctx}Находим наименьший общий знаменатель {den1} и {den2}: {lcm}.",
    "SCALE_TO_COMMON_DENOM": (
        "{ctx}Приводим дроби к общему знаменателю {lcm}: "
        "левая дробь становится {left_scaled_num}/{lcm}, правая — {right_scaled_num}/{lcm}."
    ),
    "ADD_OR_SUB_NUMERATORS": (
    "{ctx}{operation_name_cap} числители: {left_num} {sign} {right_num} = {result_num}."
    ),
    "REDUCE_FRACTION": (
        "{ctx}Сокращаем дробь {num}/{den} на {gcd}: получаем {result_num}/{result_den}."
    ),
    "FRACTION_ALREADY_REDUCED": "{ctx}Дробь {num}/{den} уже несократима.",
    "CONVERT_MIXED_FIRST": (
        "{ctx}Преобразуем смешанное число {mixed_text} в неправильную дробь: "
        "({whole}·{den} + {num})/{den} = {result_num}/{result_den}."
    ),
    "CONVERT_MIXED_NEXT": (
        "{ctx}Аналогично преобразуем {mixed_text}: "
        "({whole}·{den} + {num})/{den} = {result_num}/{result_den}."
    ),
    "SHOW_CONVERTED_EXPRESSION": "{ctx}После преобразования работаем с выражением {expression}.",
    "MULTIPLY_FRACTIONS_SETUP": (
        "{ctx}Записываем произведение дробей и вспоминаем правило умножения: "
        "(a/b) · (c/d) = (a·c)/(b·d)."
    ),
    "CROSS_CANCEL": (
        "{ctx}Выполняем предварительное сокращение: {cancellations_text}."
    ),
    "NO_CROSS_CANCEL": (
        "{ctx}Сократить нечего, оставляем множители {num1}, {num2} в числителе и "
        "{den1}, {den2} в знаменателе."
    ),
    "FINAL_MULTIPLICATION": (
    "{ctx}Перемножаем числители и знаменатели: "
    "{num1}·{num2} = {result_num}, {den1}·{den2} = {result_den}. "
    "Получаем произведение дробей."
    ),
    "DIVIDE_SAME_VALUE": "{ctx}Делим число само на себя и сразу получаем 1.",
    "DIVISION_TO_MULTIPLICATION": (
        "{ctx}Заменяем деление на умножение обратной дробью: "
        "{right_num}/{right_den} превращается в {flipped_num}/{flipped_den}."
    ),
    "DIVISION_COMBINED_CANCEL": (
        "{ctx}После замены выполняем сокращение: {cancellations_text}."
    ),
    "DIVISION_COMBINED_NO_CANCEL": (
        "{ctx}После замены деления на умножение сокращать нечего."
    ),
    "DIVISION_FINAL_RESULT": (
        "{ctx}Итоговое значение деления записываем как {result}."
    ),
    "COMPLEX_NUMERATOR_RESULT": "{ctx}Значение числителя равно {value}.",
    "COMPLEX_NUMERATOR_FINAL": "{ctx}Дробь уже несократима, поэтому значение числителя равно {value}.",
    "COMPLEX_DIVISION_SETUP": (
        "{ctx}Теперь делим числитель {numerator} на знаменатель {denominator}."
    ),
    "CONVERT_TO_DECIMAL": (
        "{ctx}Переводим дробь {num}/{den} в десятичное число: {decimal}."
    ),
    "EXTRACT_NUMERATOR": (
        "{ctx}Берём числитель из дроби {num}/{den}: это {num}."
    ),
    "EXTRACT_DENOMINATOR": (
        "{ctx}Берём знаменатель из дроби {num}/{den}: это {den}."
    ),
}


# ---------------------------------------------------------------------------
# Шаблоны для идеи и подсказок
# ---------------------------------------------------------------------------

IDEA_TEMPLATES: Dict[str, str] = {
    "ADD_SUB_FRACTIONS_IDEA": (
    "Приводим дроби к общему знаменателю, {operation_name} числители и приводим результат к несократимому виду."
    ),
    "MULTIPLY_DIVIDE_FRACTIONS_IDEA": (
        "Если встречаются смешанные числа, преобразуем их в неправильные дроби, после чего используем правила умножения и деления дробей."
    ),
    "PARENTHESES_OPERATIONS_IDEA": (
        "Сначала выполняем действия в скобках, затем последовательно обрабатываем внешнюю операцию, соблюдая порядок действий."
    ),
    "COMPLEX_FRACTION_IDEA": (
        "Отдельно вычисляем числитель сложной дроби, затем делим его на знаменатель по правилу деления дробей."
    ),
    "GENERIC_IDEA": (
        "Разберём выражение по шагам, чтобы чётко проследить каждое преобразование."
    ),
}

HINT_TEMPLATES: Dict[str, str] = {
    "HINT_ORDER_OF_OPERATIONS": (
        "Соблюдайте порядок действий: сначала вычисляйте выражения в скобках, затем выполняйте умножение или деление."
    ),
    "HINT_FIND_LCM": (
        "Для сложения и вычитания дробей приведите их к общему знаменателю через наименьшее общее кратное."
    ),
    "HINT_CHECK_REDUCTION": (
        "После вычислений проверьте, можно ли сократить полученную дробь на общий делитель числителя и знаменателя."
    ),
    "HINT_CONVERT_MIXED": (
        "Смешанные числа удобнее преобразовать в неправильные дроби: целую часть умножьте на знаменатель и прибавьте числитель."
    ),
    "HINT_DIVIDE_AS_MULTIPLY": (
        "Чтобы разделить дроби, умножьте первую дробь на обратную ко второй."
    ),
    "HINT_CROSS_CANCEL": (
        "Перед перемножением числителей и знаменателей попробуйте выполнить перекрёстное сокращение, чтобы упростить вычисления."
    ),
    "HINT_MULTIPLY_AFTER_PARENTHESES": (
        "После упрощения выражения в скобках аккуратно перенесите результат во внешнюю операцию."
    ),
    "HINT_PROCESS_NUMERATOR": (
        "В сложной дроби сначала упростите выражение в числителе, затем переходите к делению на знаменатель."
    ),
}


# ---------------------------------------------------------------------------
# Публичные функции
# ---------------------------------------------------------------------------

def humanize(solution_core: Dict[str, Any]) -> str:
    """Возвращает HTML-представление solution_core."""

    parts: List[str] = []

    idea_text = _resolve_idea(solution_core)
    parts.append(f"<b>Идея решения:</b> {idea_text}")

    steps = solution_core.get("calculation_steps") or []
    rendered_steps = [_render_step(step) for step in steps]
    if rendered_steps:
        steps_block = "\n\n".join(rendered_steps)
        parts.append(f"<b>Подробные шаги:</b>\n{steps_block}")

    final_answer_block = _render_final_answer(solution_core.get("final_answer") or {})
    parts.append(final_answer_block)

    hints_block = _render_hints(solution_core)
    if hints_block:
        parts.append(hints_block)

    return "\n\n".join(parts)


def validate_solution_core(solution_core: Dict[str, Any]) -> bool:
    """Быстрая проверка структуры solution_core."""

    required_fields = ["question_id", "question_group", "calculation_steps", "final_answer"]
    if not all(field in solution_core for field in required_fields):
        return False

    steps = solution_core.get("calculation_steps")
    if not isinstance(steps, list):
        return False

    for step in steps:
        if not isinstance(step, dict):
            return False
        if "step_number" not in step or "description_key" not in step:
            return False

    final_answer = solution_core.get("final_answer")
    if not isinstance(final_answer, dict):
        return False
    if "value_display" not in final_answer:
        return False

    return True


def get_available_templates() -> List[str]:
    """Возвращает список доступных шаблонов описаний шагов."""
    return sorted(STEP_TEMPLATES.keys())


# ---------------------------------------------------------------------------
# Внутренние помощники
# ---------------------------------------------------------------------------

def _resolve_idea(solution_core: Dict[str, Any]) -> str:
    key = solution_core.get("explanation_idea_key")
    params = solution_core.get("explanation_idea_params") or {}
    if key in IDEA_TEMPLATES:
        return IDEA_TEMPLATES[key].format(**params)

    fallback = solution_core.get("explanation_idea")
    if isinstance(fallback, str) and fallback.strip():
        return fallback.strip()

    return IDEA_TEMPLATES["GENERIC_IDEA"]


def _render_step(step: Dict[str, Any]) -> str:
    number = step.get("step_number")
    description = _format_step_description(step)

    formula_lines = []
    for field in ("formula_representation", "formula_general", "formula_calculation"):
        value = step.get(field)
        if value:
            formula_lines.append(_escape_newlines(value))

    formulas_html = ""
    if formula_lines:
        formulas_html = "\n".join(f"<code>{line}</code>" for line in formula_lines)

    if formulas_html:
        return f"<b>Шаг {number}.</b> {description}\n{formulas_html}"
    return f"<b>Шаг {number}.</b> {description}"


def _format_step_description(step: Dict[str, Any]) -> str:
    key = step.get("description_key", "")
    params = dict(step.get("description_params") or {})

    ctx = _prepare_context(params.pop("context", None), step)
    params["ctx"] = ctx

    if "cancellations" in params:
        params["cancellations_text"] = _format_cancellations(params.pop("cancellations"))

    if key == "DIVISION_FINAL_RESULT":
        params.setdefault("result", step.get("calculation_result", ""))

    if key == "CONVERT_TO_DECIMAL":
        params["decimal"] = _format_decimal(params.get("decimal"))

    template = STEP_TEMPLATES.get(key)
    if not template:
        return f"{ctx}{key}"

    try:
        return template.format(**params)
    except KeyError as missing:
        missing_key = missing.args[0]
        params[missing_key] = f"{{{missing_key}}}"
        return template.format(**params)


def _render_final_answer(final_answer: Dict[str, Any]) -> str:
    """Формирует блок финального ответа с лаконичным оформлением."""
    value = str(final_answer.get("value_display", "")).strip()
    return f"<b>Ответ:</b> <code>{value}</code>"


def _render_hints(solution_core: Dict[str, Any]) -> Optional[str]:
    hint_keys: Iterable[str] = solution_core.get("hints_keys") or []
    hints: List[str] = []

    for key in hint_keys:
        text = HINT_TEMPLATES.get(key)
        if text:
            hints.append(text)

    if not hints:
        raw_hints = solution_core.get("hints") or []
        hints.extend(str(item) for item in raw_hints if str(item).strip())

    if not hints:
        return None

    items = "\n".join(f"• {text}" for text in hints)
    return f"<tg-spoiler><b>Полезно помнить:</b>\n{items}</tg-spoiler>"


def _prepare_context(raw: Optional[str], step: Optional[Dict[str, Any]] = None) -> str:
    """Готовит текст контекста (например, 'В числителе.') для шага."""
    if not raw:
        return ""
    text = raw.strip()

    # Если это контекст вида 'В числителе' — превращаем в осмысленную фразу
    if text.lower().startswith("в числителе") and step:
        expr = step.get("formula_representation") or ""
        expr_clean = expr.strip()
        if expr_clean:
            return f"Находим значение числителя {expr_clean}. "

    if text and text[-1] not in ".!?:":
        text += "."
    return f"{text} "


def _format_cancellations(items: Iterable[Dict[str, Any]]) -> str:
    formatted: List[str] = []
    for item in items:
        num = item.get("num")
        den = item.get("den")
        gcd = item.get("gcd")
        num_result = item.get("num_result")
        den_result = item.get("den_result")
        formatted.append(
            f"{num} и {den} ÷ {gcd} → {num_result}/{den_result}"
        )
    return "; ".join(formatted)


def _format_decimal(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:g}"


def _escape_newlines(text: str) -> str:
    return text
