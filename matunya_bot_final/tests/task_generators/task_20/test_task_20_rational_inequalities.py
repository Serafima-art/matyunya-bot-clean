"""Tests for rational_inequalities generator and validator."""

from matunya_bot_final.task_generators.task_20.generators.rational_inequalities_generator import (
    generate_task_20_rational_inequalities,
)
from matunya_bot_final.task_generators.task_20.validators.rational_inequalities_validator import (
    validate_task_20_rational_inequalities,
)


def test_generation_and_validation():
    """Генерация и полная валидация 10 задач rational_inequalities."""
    for i in range(10):
        task = generate_task_20_rational_inequalities()
        ok = validate_task_20_rational_inequalities(task)
        assert ok, f"❌ Ошибка в задаче #{i+1}: {task['variables']['solution_pattern']}"
        print(f"✅ {i+1}) {task['variables']['solution_pattern']} → {task['answer'][0]}")
