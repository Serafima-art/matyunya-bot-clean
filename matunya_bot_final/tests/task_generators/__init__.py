"""
Тест на совместимость генератора и валидатора для form_match_mixed.
"""

import pytest

from matunya_bot_final.task_generators.task_11.generators.form_match_mixed_generator import (
    generate_task_11_form_match_mixed,
)
from matunya_bot_final.task_generators.task_11.validators.form_match_mixed_validator import (
    validate_task_11_form_match_mixed,
)


@pytest.mark.asyncio
async def test_form_match_mixed_generator_and_validator():
    # Несколько итераций для проверки стабильности
    for i in range(20):
        task = generate_task_11_form_match_mixed()
        errors = validate_task_11_form_match_mixed(task)

        assert errors == [], f"Ошибки валидации: {errors}\nЗадача: {task}"