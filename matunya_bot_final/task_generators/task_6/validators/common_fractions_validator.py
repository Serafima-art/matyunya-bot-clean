"""Validator for common fractions tasks (Task 6, Theme 1)."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Tuple

_ALLOWED_PREFIXES = [
    "Вычисли результат",
    "Выполни действия",
    "Раскрой скобки и выполни вычисления",
    "Вычисли значение дроби",
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
        "id",
        "task_number",
        "topic",
        "subtype",
        "question_text",
        "answer",
        "answer_type",
        "variables",
        "meta",
    }
    missing = required_fields - set(task)
    if missing:
        errors.append(f"Отсутствуют поля: {', '.join(sorted(missing))}.")

    if task.get("task_number") != 6:
        errors.append("Некорректный номер задания (ожидалось 6).")

    if task.get("topic") != "common_fractions":
        errors.append("Некорректная тема (ожидалось 'common_fractions').")

    variants = _normalise_variants(task.get("question_text", ""))
    if not any(
        variant.startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ):
        errors.append(f"Unexpected question_text: {task.get('question_text')}")

    answer_type = task.get("answer_type")
    if answer_type not in {"decimal", "fraction"}:
        errors.append("answer_type должен быть 'decimal' или 'fraction'.")

    if answer_type == "decimal":
        try:
            value = float(task.get("answer", ""))
            if not _is_pretty_decimal(value):
                errors.append("Ответ не является 'красивым' (конечная десятичная дробь или целое).")
        except (TypeError, ValueError):
            errors.append("Ответ не преобразуется в число при answer_type='decimal'.")

    meta = task.get("meta", {})
    if "pattern_id" not in meta:
        errors.append("Отсутствует meta.pattern_id")

    return len(errors) == 0, errors


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
