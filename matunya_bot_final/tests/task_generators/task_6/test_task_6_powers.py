"""Integration test for powers generator and validator."""

from collections import Counter

from matunya_bot_final.task_generators.task_6.generators.powers_generator import (
    generate_powers_tasks,
)
from matunya_bot_final.task_generators.task_6.validators.powers_validator import (
    validate_powers_task,
)

_ALLOWED_PREFIXES = [
    "Вычисли значение выражения",
    "Вычисли выражение",
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
        "variables",
        "answer_type",
        "meta",
    }
    assert set(task.keys()) == required_keys
    assert task["task_number"] == 6
    assert task["topic"] == "powers"
    assert isinstance(task["question_text"], str)

    variants = _normalise_variants(task["question_text"])
    assert any(
        variant.startswith(prefix)
        for variant in variants
        for prefix in _ALLOWED_PREFIXES
    ), f"Unexpected question_text: {task['question_text']}"

    float(task["answer"])


def test_task_6_powers_pipeline() -> None:
    """Ensure generator and validator work together for both patterns."""  # noqa: D401
    pattern_counts: Counter[str] = Counter()
    failures = []

    total_samples = 100

    def _process_sample(index: int) -> None:
        try:
            task = generate_powers_tasks(1)[0]
        except Exception as exc:
            failures.append((index, "generation_failed", str(exc)))
            return

        try:
            _assert_common_structure(task)
            is_valid, errors = validate_powers_task(task)
            if not is_valid:
                raise AssertionError("; \n".join(errors))
        except Exception as exc:
            failures.append((index, task.get("id"), str(exc)))
            return

        pattern_counts[task["meta"]["pattern_id"]] += 1

    for i in range(total_samples):
        _process_sample(i)

    if failures:
        sample = "; \n".join(
            f"#{idx} ({task_id}): {error}" for idx, task_id, error in failures[:5]
        )
        raise AssertionError(f"Failed {len(failures)} tasks. Examples: {sample}")

    for pattern in {"4.1", "4.2"}:
        assert pattern_counts[pattern] > 0, f"No tasks generated for pattern '{pattern}'"
