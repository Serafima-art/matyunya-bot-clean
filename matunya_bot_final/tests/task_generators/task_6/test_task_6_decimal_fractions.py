"""Integration test for decimal fractions generator and validator."""

from collections import Counter

from matunya_bot_final.task_generators.task_6.generators.decimal_fractions_generator import (
    generate_decimal_fractions_tasks,
)
from matunya_bot_final.task_generators.task_6.validators.decimal_fractions_validator import (
    validate_decimal_fractions_task,
)

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


def _assert_common_structure(task: dict) -> None:
    required_keys = {
    "id",
    "task_number",
    "topic",
    "subtype",
    "question_text",
    "answer",
    "display_answer",
    "variables",
    "answer_type",
    "meta",
    }
    assert set(task.keys()) == required_keys
    assert task["task_number"] == 6
    assert task["topic"] == "decimal_fractions"
    assert isinstance(task["question_text"], str)

    variants = _normalise_variants(task["question_text"])
    assert any(
        variant.startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ), f"Unexpected question_text: {task['question_text']}"

    float(str(task["answer"]).replace(",", "."))


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

        pattern_counts[task["meta"]["pattern_id"]] += 1

    attempts = 0
    while attempts < total_samples:
        _process_sample(attempts)
        attempts += 1

    while len(pattern_counts) < 3 and attempts < max_attempts:
        _process_sample(attempts)
        attempts += 1

    if failures:
        sample = "; ".join(
            f"#{idx} ({task_id}): {error}" for idx, task_id, error in failures[:5]
        )
        raise AssertionError(f"Failed {len(failures)} tasks. Examples: {sample}")

    missing_patterns = {"2.1", "2.2", "2.3"} - set(pattern_counts)
    assert not missing_patterns, (
        f"Patterns not generated after {attempts} attempts: {missing_patterns}"
    )
    for pattern in {"2.1", "2.2", "2.3"}:
        assert pattern_counts[pattern] > 0, f"No tasks generated for pattern '{pattern}'"
