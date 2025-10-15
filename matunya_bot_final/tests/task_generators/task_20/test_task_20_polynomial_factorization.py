"""Integration test for polynomial_factorization generator and validator."""

from __future__ import annotations

from collections import Counter

from matunya_bot_final.task_generators.task_20.generators import (
    generate_task_20_by_subtype,
)
from matunya_bot_final.task_generators.task_20.validators import (
    validate_task_20_polynomial_factorization,
)


REQUIRED_KEYS = {
    "id",
    "task_number",
    "topic",
    "subtype",
    "question_text",
    "answer",
    "variables",
}
ALLOWED_PATTERNS = {"common_poly", "diff_squares", "grouping"}


def _assert_common_structure(task: dict) -> None:
    assert set(task.keys()) == REQUIRED_KEYS
    assert task["task_number"] == 20
    assert task["topic"] == "algebraic_expressions"
    assert task["subtype"] == "polynomial_factorization"
    assert isinstance(task["question_text"], str) and task["question_text"].startswith("Реши уравнение")
    assert isinstance(task["answer"], list) and task["answer"]
    assert isinstance(task["variables"], dict)
    assert task["variables"].get("solution_pattern") in ALLOWED_PATTERNS


def test_task_20_polynomial_factorization_pipeline() -> None:
    """Ensure generator and validator work together for all patterns."""
    pattern_counts: Counter[str] = Counter()
    failures = []

    total_samples = 200
    max_attempts = 600

    def _process_sample(index: int) -> None:
        try:
            task = generate_task_20_by_subtype("polynomial_factorization")
        except Exception as exc:  # noqa: BLE001
            failures.append((index, "generation_failed", str(exc)))
            return

        try:
            _assert_common_structure(task)
            validate_task_20_polynomial_factorization(task)
        except Exception as exc:  # noqa: BLE001
            failures.append((index, task.get("id"), str(exc)))
            return

        pattern = task["variables"]["solution_pattern"]
        pattern_counts[pattern] += 1

    attempts = 0
    while attempts < total_samples:
        _process_sample(attempts)
        attempts += 1

    # Continue sampling until every pattern is observed or attempts exhausted.
    while len(pattern_counts) < len(ALLOWED_PATTERNS) and attempts < max_attempts:
        _process_sample(attempts)
        attempts += 1

    if failures:
        sample = "; ".join(
            f"#{idx} ({task_id}): {error}" for idx, task_id, error in failures[:5]
        )
        raise AssertionError(f"Failed {len(failures)} tasks. Examples: {sample}")

    missing_patterns = ALLOWED_PATTERNS - set(pattern_counts)
    assert not missing_patterns, f"Patterns not generated after {attempts} attempts: {missing_patterns}"

    for pattern in ALLOWED_PATTERNS:
        assert pattern_counts[pattern] > 0, f"No tasks generated for pattern '{pattern}'"
