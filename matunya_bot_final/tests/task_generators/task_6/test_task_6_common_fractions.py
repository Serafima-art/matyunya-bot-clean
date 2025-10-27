# matunya_bot_final/tests/task_generators/task_6/test_task_6_common_fractions.py

"""Integration tests for common fractions generator and validator (Task 6)."""

from __future__ import annotations

from collections import Counter

from matunya_bot_final.task_generators.task_6.generators.common_fractions_generator import (
    generate_common_fractions_tasks,
)
from matunya_bot_final.task_generators.task_6.validators.common_fractions_validator import (
    validate_common_fractions_task,
)

# =================================================================
# ★★★ ЭТАЛОННЫЕ ДАННЫЕ (УТВЕРЖДЕНЫ КАПИТАНОМ) ★★★
# =================================================================

# Правильные имена паттернов, как мы договорились
_EXPECTED_PATTERNS = {
    "cf_addition_subtraction",
    "multiplication_division",
    "parentheses_operations",
    "complex_fraction",
}

# Корректные префиксы для текста вопроса
_ALLOWED_PREFIXES = [
    "Вычисли результат",
    "Выполни действия",
    "Раскрой скобки и выполни вычисления",
    "Вычисли значение дроби",
    "Найди значение выражения",
    "Получи результат",
]

# =================================================================
# ★★★ ОСНОВНАЯ ЛОГИКА ТЕСТА ★★★
# =================================================================

def _assert_common_structure(task: dict, expected_answer_type: str | None = None) -> None:
    """Проверяет общую структуру задачи на соответствие ГОСТ-JSON-6."""
    expected_keys = {
        "id", "task_number", "subtype", "pattern", "question_text",
        "answer", "answer_type", "variables", "meta",
    }
    assert set(task.keys()) == expected_keys, f"Набор ключей не совпадает с эталоном. Лишние/недостающие: {set(task.keys()) ^ expected_keys}"
    assert task["task_number"] == 6, "Неверный номер задания"
    assert task["subtype"] == "common_fractions", "Неверный подтип"

    # Проверяем, что pattern - один из разрешенных
    assert task["pattern"] in _EXPECTED_PATTERNS, f"Недопустимый паттерн: {task['pattern']}"

    assert isinstance(task["question_text"], str), "Текст вопроса должен быть строкой"

    # Проверка текста вопроса на корректное начало
    # (Вспомогательные функции для корректной работы с кодировками)
    def _trim_leading_noise(value: str) -> str:
        for idx, char in enumerate(value):
            if char.isalpha(): return value[idx:]
        return value

    def _normalise_variants(text: str) -> list[str]:
        normalised = text.replace("\u00a0", " ").replace("\u202f", " ").strip()
        variants = {normalised, _trim_leading_noise(normalised)}
        return list(variants)

    variants = _normalise_variants(task["question_text"])
    assert any(
        variant.startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ), f"����������� ����� �������: {task['question_text']}"
    if expected_answer_type is not None:
        assert task["answer_type"] == expected_answer_type, (
            f"expected answer_type '{expected_answer_type}', got '{task['answer_type']}'"
        )



def _looks_ok(task: dict) -> None:
    ok, errs = validate_common_fractions_task(task)
    assert ok, f"validator errors: {errs}"
    qt = task["question_text"]
    assert len(qt.splitlines()) >= 2 and any("/" in ln for ln in qt.splitlines()[1:]), "No fraction in body"

def test_decimal_answer_patterns() -> None:
    """Проверяет, что паттерны с десятичным ответом генерируются корректно."""
    decimal_patterns = {
        "multiplication_division",
        "parentheses_operations",
        "complex_fraction",
    }
    pattern_counts: Counter[str] = Counter()
    failures = []
    max_attempts = 500

    for index in range(max_attempts):
        if len(pattern_counts) == len(decimal_patterns):
            break
        try:
            task = generate_common_fractions_tasks(1)[0]
        except Exception as exc:
            failures.append((index, "generation_failed", str(exc)))
            continue

        if task.get("pattern") not in decimal_patterns:
            continue

        try:
            _assert_common_structure(task, expected_answer_type="decimal")
            _looks_ok(task)
        except Exception as exc:
            failures.append((index, task.get("id"), str(exc)))
            continue

        pattern_counts[task["pattern"]] += 1

    if failures:
        sample = "; ".join(
            f"#{idx} ({task_id}): {error}" for idx, task_id, error in failures[:5]
        )
        raise AssertionError(f"Failed {len(failures)} tasks. Examples: {sample}")

    missing_patterns = decimal_patterns - set(pattern_counts)
    assert not missing_patterns, (
        f"Decimal patterns not generated after {max_attempts} attempts: {missing_patterns}"
    )


def test_numerator_answer_pattern() -> None:
    """Проверяет паттерн cf_addition_subtraction с ответом-числителем."""
    task_data = None
    failures = []
    max_attempts = 300

    for index in range(max_attempts):
        if task_data is not None:
            break
        try:
            task = generate_common_fractions_tasks(1)[0]
        except Exception as exc:
            failures.append((index, "generation_failed", str(exc)))
            continue

        if task.get("pattern") != "cf_addition_subtraction":
            continue

        try:
            _assert_common_structure(task, expected_answer_type="integer")
            _looks_ok(task)
        except Exception as exc:
            failures.append((index, task.get("id"), str(exc)))
            continue

        assert "В ответ запишите числитель" in task["question_text"], (
            "question_text должен содержать фразу про числитель"
        )
        try:
            int(task["answer"])
        except (TypeError, ValueError):
            raise AssertionError("Ответ для паттерна cf_addition_subtraction должен приводиться к int")
        task_data = task

    if task_data is None:
        sample = "; ".join(
            f"#{idx} ({task_id}): {error}" for idx, task_id, error in failures[:5]
        )
        raise AssertionError(
            f"cf_addition_subtraction не сгенерирован за {max_attempts} попыток. Примеры: {sample}"
        )
