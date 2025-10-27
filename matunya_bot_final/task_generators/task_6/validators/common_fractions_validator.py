"""Validator for common fractions tasks (Task 6, Theme 1)."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Tuple

_ALLOWED_PREFIXES = [
    "Вычисли результат",
    "Выполни действия",
    "Раскрой скобки и выполни вычисления",
    "Вычисли значение дроби",
    "Найди значение выражения",
    "Получи результат",
]


def _trim_leading_noise(value: str) -> str:
    for idx, char in enumerate(value):
        if char.isalpha():
            return value[idx:]
    return value


def _normalise_variants(text: str) -> List[str]:
    normalised = text.replace("\u00a0", " ").replace("\u202f", " ").strip()
    variants = {normalised, _trim_leading_noise(normalised)}
    try:
        converted = normalised.encode("cp1251", errors="ignore").decode(
            "utf-8", errors="ignore"
        )
        variants.add(converted)
        variants.add(_trim_leading_noise(converted))
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return list(variants)


def validate_common_fractions_task(task: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not isinstance(task, dict):
        return False, ["Задача должна быть словарём."]

    required_fields = {
        "id", "task_number", "subtype", "pattern", "question_text",
        "answer", "answer_type", "variables", "meta",
    }
    missing = required_fields - set(task)
    if missing:
        errors.append(f"Отсутствуют поля: {', '.join(sorted(missing))}.")

    if task.get("task_number") != 6:
        errors.append("Некорректный номер задания (ожидалось 6).")

    if task.get("subtype") != "common_fractions":
        errors.append("Некорректный subtype (ожидалось 'common_fractions').")
    allowed_patterns = {
        "cf_addition_subtraction",
        "multiplication_division",
        "parentheses_operations",
        "complex_fraction",
    }
    if task.get("pattern") not in allowed_patterns:
        errors.append(f"Недопустимое значение для 'pattern': {task.get('pattern')}")

    variants = _normalise_variants(task.get("question_text", ""))
    if not any(
        variant.strip().startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ):
        errors.append(f"Unexpected question_text: {task.get('question_text')}")
    # --- Блок, запрещающий пустые задания ---
    qt = task.get("question_text", "")
    tail_lines = qt.splitlines()[1:]  # всё после первой строки с заголовком
    tail = " ".join(tail_lines).strip()

    # Должна быть хотя бы одна цифра и хотя бы один оператор/разделитель
    if not tail or not any(ch.isdigit() for ch in tail) or not any(sym in tail for sym in "/:·+−-()"):
        errors.append("В question_text отсутствует математическое выражение.")
    # Простая эвристика: хотя бы одна дробь вида a/b
    if not any("/" in tok for tok in tail.split()):
        errors.append("В question_text не обнаружена ни одна дробь вида a/b.")


    expects_numerator = "В ответ запишите числитель" in qt
    answer_type = task.get("answer_type")
    answer_value = task.get("answer")

    if expects_numerator:
        if answer_type not in {"integer", "string"}:
            errors.append("answer_type для задач с числителем должен быть 'integer' или 'string'.")
        try:
            int(answer_value)
        except (TypeError, ValueError):
            errors.append("Ответ должен преобразовываться в целое число для задач с числителем.")
    else:
        if answer_type != "decimal":
            errors.append("answer_type должен быть 'decimal' для задач с десятичным ответом.")
        else:
            try:
                value = float(answer_value)
                if not _is_pretty_decimal(value):
                    errors.append("Ответ не является 'красивым' (конечная десятичная дробь или целое).")
            except (TypeError, ValueError):
                errors.append("Ответ не преобразуется в число при answer_type='decimal'.")

    meta = task.get("meta", {})
    if "pattern_id" not in meta:
        errors.append("Отсутствует meta.pattern_id")

    expression_tree = task.get("variables", {}).get("expression_tree")
    if expression_tree:
        _validate_expression_tree(expression_tree, errors)
    else:
        errors.append("Отсутствует variables.expression_tree")

    return len(errors) == 0, errors
def _validate_expression_tree(node: Any, errors: List[str]) -> None:
    if not isinstance(node, dict):
        errors.append("expression_tree: узел не является словарём")
        return
    if "type" in node:
        if node["type"] == "mixed":
            errors.append("expression_tree: тип 'mixed' недопустим")
    if "operation" in node:
        if node["operation"] not in ["add", "subtract", "multiply", "divide"]:
            errors.append(f"expression_tree: недопустимая операция '{node['operation']}'")
    if "operands" in node:
        operands = node["operands"]
        if isinstance(operands, list):
            for child in operands:
                _validate_expression_tree(child, errors)


def _is_pretty_decimal(value: float) -> bool:
    try:
        frac = Fraction(value).limit_denominator()
        den = frac.denominator
        while den % 2 == 0:
            den //= 2
        while den % 5 == 0:
            den //= 5
        if den != 1:
            return False
        s = f"{float(value):.10f}".rstrip("0").rstrip(".")
        if "." in s:
            decimals = len(s.split(".")[1])
            if decimals > 2:
                return False
        return True
    except Exception:
        return False
