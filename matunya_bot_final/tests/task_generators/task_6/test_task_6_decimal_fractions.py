# matunya_bot_final/tests/task_generators/task_6/test_task_6_decimal_fractions.py

"""Integration test for decimal fractions generator and validator."""

from __future__ import annotations

from collections import Counter
import pytest

from matunya_bot_final.task_generators.task_6.generators.decimal_fractions_generator import (
    generate_decimal_fractions_tasks,
)
from matunya_bot_final.task_generators.task_6.validators.decimal_fractions_validator import (
    validate_decimal_fractions_task,
)

# Вспомогательные функции, которые нужны тесту, но не меняются
# =================================================================

_ALLOWED_PREFIXES = [
    "Посчитай значение",
    "Вычисли выражение",
    "Посчитай значение дроби",
]


def _trim_leading_noise(value: str) -> str:
    for idx, char in enumerate(value):
        if char.isalpha():
            return value[idx:]
    return value


def _normalise_variants(text: str) -> list[str]:
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


# Основная логика теста
# =================================================================

def _assert_common_structure(task: dict) -> None:
    """
    Asserts the common structure of a task, now updated for the new JSON standard.
    """
    expected_keys = {
        "id",
        "task_number",
        "subtype",
        "pattern",
        "question_text",
        "answer",
        "display_answer",
        "answer_type",
        "variables",
        "meta",
    }
    assert set(task.keys()) == expected_keys
    assert task["task_number"] == 6
    assert task["subtype"] == "decimal_fractions"

    # Проверяем, что pattern - один из разрешенных
    allowed_patterns = {"df_addition_subtraction", "linear_operations", "fraction_structure"}
    assert task["pattern"] in allowed_patterns, f"Unexpected pattern: {task['pattern']}"

    assert isinstance(task["question_text"], str)

    variants = _normalise_variants(task["question_text"])
    assert any(
        variant.startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ), f"Unexpected question_text: {task['question_text']}"

    float(str(task["answer"]).replace(",", "."))


@pytest.mark.slow
def test_task_6_decimal_fractions_pipeline() -> None:
    """Ensure generator and validator work together for all patterns."""
    pattern_counts: Counter[str] = Counter()
    failures = []

    total_samples = 100
    max_attempts = 300

    def _process_sample(index: int) -> None:
        try:
            task = generate_decimal_fractions_tasks(1)[0]
        except Exception as exc:
            failures.append((index, "generation_failed", str(exc)))
            return

        try:
            _assert_common_structure(task)
            is_valid, errors = validate_decimal_fractions_task(task)
            if not is_valid:
                raise AssertionError("; ".join(errors))
        except Exception as exc:
            failures.append((index, task.get("id"), str(exc)))
            return

        pattern_counts[task["pattern"]] += 1


    attempts = 0
    # Генерируем, пока не встретим все 3 паттерна
    while len(pattern_counts) < 3 and attempts < max_attempts:
        _process_sample(attempts)
        attempts += 1

    # Добиваем до нужного количества
    if attempts < total_samples:
        for i in range(attempts, total_samples):
            _process_sample(i)


    if failures:
        sample = "; ".join(
            f"#{idx} ({task_id}): {error}" for idx, task_id, error in failures[:5]
        )
        raise AssertionError(f"Failed {len(failures)} tasks. Examples: {sample}")

    # Проверяем правильные имена паттернов
    expected_patterns = {"df_addition_subtraction", "linear_operations", "fraction_structure"}
    missing_patterns = expected_patterns - set(pattern_counts)
    assert not missing_patterns, (
        f"Patterns not generated after {attempts} attempts: {missing_patterns}"
    )
    for pattern in expected_patterns:
        assert pattern_counts[pattern] > 0, f"No tasks generated for pattern '{pattern}'"
