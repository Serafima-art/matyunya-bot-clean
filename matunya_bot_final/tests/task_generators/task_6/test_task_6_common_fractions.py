"""Integration tests for common fractions generator and validator (Task 6)."""

from __future__ import annotations

from collections import Counter

from matunya_bot_final.task_generators.task_6.generators.common_fractions_generator import (
    generate_common_fractions_tasks,
)
from matunya_bot_final.task_generators.task_6.validators.common_fractions_validator import (
    validate_common_fractions_task,
)

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


def _assert_common_structure(task: dict) -> None:
    expected_keys = {
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
    assert set(task.keys()) == expected_keys
    assert task["task_number"] == 6
    assert task["topic"] == "common_fractions"
    assert isinstance(task["question_text"], str)

    variants = _normalise_variants(task["question_text"])
    assert any(
        variant.startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ), f"Unexpected question_text: {task['question_text']}"

    assert task["answer_type"] in {"decimal", "fraction"}
    assert isinstance(task["variables"], dict)
    assert isinstance(task["meta"], dict)


def test_task_6_common_fractions_pipeline() -> None:
    """Ensure generator and validator work together for all four patterns."""
    pattern_counts: Counter[str] = Counter()
    failures = []

    total_samples = 100
    max_attempts = 300

    def _process_sample(index: int) -> None:
        try:
            task = generate_common_fractions_tasks(1)[0]
        except Exception as exc:  # noqa: BLE001
            failures.append((index, "generation_failed", str(exc)))
            return

        try:
            _assert_common_structure(task)
            is_valid, errors = validate_common_fractions_task(task)
            if not is_valid:
                raise AssertionError("; ".join(errors))
        except Exception as exc:  # noqa: BLE001
            failures.append((index, task.get("id"), str(exc)))
            return

        pattern = task["meta"]["pattern_id"]
        pattern_counts[pattern] += 1

    attempts = 0
    while attempts < total_samples:
        _process_sample(attempts)
        attempts += 1

    while len(pattern_counts) < 4 and attempts < max_attempts:
        _process_sample(attempts)
        attempts += 1

    if failures:
        sample = "; ".join(
            f"#{idx} ({task_id}): {error}" for idx, task_id, error in failures[:5]
        )
        raise AssertionError(f"Failed {len(failures)} tasks. Examples: {sample}")

    missing_patterns = {"1.1", "1.2", "1.3", "1.4"} - set(pattern_counts)
    assert not missing_patterns, (
        f"Patterns not generated after {attempts} attempts: {missing_patterns}"
    )
    for pattern in {"1.1", "1.2", "1.3", "1.4"}:
        assert pattern_counts[pattern] > 0, f"No tasks generated for pattern '{pattern}'"
