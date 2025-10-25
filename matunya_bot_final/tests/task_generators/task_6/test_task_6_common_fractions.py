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
]

# =================================================================
# ★★★ ОСНОВНАЯ ЛОГИКА ТЕСТА ★★★
# =================================================================

def _assert_common_structure(task: dict) -> None:
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
    ), f"Неожиданный текст вопроса: {task['question_text']}"


def test_task_6_common_fractions_pipeline() -> None:
    """Гарантирует, что генератор и валидатор работают вместе для всех паттернов."""
    pattern_counts: Counter[str] = Counter()
    failures = []

    total_samples = 150
    max_attempts = 400

    def _process_sample(index: int) -> None:
        try:
            task = generate_common_fractions_tasks(1)[0]
        except Exception as exc:
            failures.append((index, "generation_failed", str(exc)))
            return

        try:
            _assert_common_structure(task)
            is_valid, errors = validate_common_fractions_task(task)
            if not is_valid:
                raise AssertionError("; ".join(errors))
        except Exception as exc:
            failures.append((index, task.get("id"), str(exc)))
            return

        pattern_counts[task["pattern"]] += 1

    attempts = 0
    while len(pattern_counts) < len(_EXPECTED_PATTERNS) and attempts < max_attempts:
        _process_sample(attempts)
        attempts += 1

    if attempts < total_samples:
        for i in range(attempts, total_samples):
            _process_sample(i)

    if failures:
        sample = "; ".join(
            f"#{idx} ({task_id}): {error}" for idx, task_id, error in failures[:5]
        )
        raise AssertionError(f"Failed {len(failures)} tasks. Examples: {sample}")

    missing_patterns = _EXPECTED_PATTERNS - set(pattern_counts)
    assert not missing_patterns, f"Patterns not generated after {attempts} attempts: {missing_patterns}"
