"""Tests for task 20 radical_equations generator and validator."""

import pytest

from matunya_bot_final.task_generators.task_20.generators.radical_equations_generator import (
    generate_task_20_radical_equations,
)
from matunya_bot_final.task_generators.task_20.validators.radical_equations_validator import (
    validate_task_20_radical_equations,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("i", range(5))
async def test_task_20_radical_equations_generator_and_validator(i):
    """Check that generator creates valid tasks and validator accepts them."""
    task = generate_task_20_radical_equations()

    # --- Общие поля ---
    assert isinstance(task, dict)
    assert task["task_number"] == 20
    assert task["topic"] == "equations"
    assert task["subtype"] == "radical_equations"

    variables = task.get("variables", {})
    assert "solution_pattern" in variables
    assert variables["solution_pattern"] in ("sum_zero", "same_radical_cancel")

    # --- Поля radicals ---
    radicals = variables.get("radicals", {})
    assert isinstance(radicals, dict)
    assert "A" in radicals and "B" in radicals
    assert "text" in radicals["A"] and "text" in radicals["B"]

    # --- Ответ ---
    answer = task["answer"]
    assert isinstance(answer, list)
    assert all(isinstance(x, str) for x in answer)
    assert len(answer) >= 1

    # --- Валидация ---
    assert validate_task_20_radical_equations(task)


def test_invalid_pattern_raises():
    """Invalid pattern must raise ValueError."""
    bad_task = {
        "task_number": 20,
        "topic": "equations",
        "subtype": "radical_equations",
        "variables": {"solution_pattern": "nonsense"},
        "answer": ["0"],
    }
    with pytest.raises(ValueError):
        validate_task_20_radical_equations(bad_task)
