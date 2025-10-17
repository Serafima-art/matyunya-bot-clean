"""
Интеграционный тест: генератор + валидатор для task_20 (rational_inequalities)

Цель:
Проверить, что все сгенерированные задания проходят ГОСТ-валидацию без ошибок.
"""

import json
import os
import pytest

from matunya_bot_final.task_generators.task_20.generators.rational_inequalities_generator import (
    generate_task_20_rational_inequalities,
)
from matunya_bot_final.task_generators.task_20.validators.rational_inequalities_validator import (
    validate_task_20_rational_inequalities,
)

# 🔹 Временная папка для примеров
TEMP_DIR = "matunya_bot_final/temp/task_20"
os.makedirs(TEMP_DIR, exist_ok=True)

# 🔹 Количество тестовых генераций
N = 20


@pytest.mark.parametrize("i", range(N))
def test_generator_validator_compatibility(i):
    """Генерирует задание и проверяет его через валидатор."""
    task = generate_task_20_rational_inequalities()  # 🔸 генерация одного задания
    pattern = task["variables"]["solution_pattern"]

    # 🔹 Проверяем через валидатор
    is_valid, errors = validate_task_20_rational_inequalities(task)

    # 🔹 Логируем результат
    if is_valid:
        print(f"✅ [{i+1:02}] {pattern} → VALID")
    else:
        print(f"❌ [{i+1:02}] {pattern} → FAIL")
        for e in errors:
            print("   •", e)

    # 🔹 Проверяем
    assert is_valid, f"Task {i+1} ({pattern}) не прошёл валидацию:\n" + "\n".join(errors)


def test_save_sample_json(tmp_path):
    """Сохраняет один пример задания в JSON для ручной проверки."""
    sample = generate_task_20_rational_inequalities()
    file_path = tmp_path / "sample_rational_inequality.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

    print(f"📦 Пример сохранён: {file_path}")
    assert file_path.exists()
