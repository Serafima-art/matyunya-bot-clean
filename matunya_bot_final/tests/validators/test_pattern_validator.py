import json
import random
import pytest
from pathlib import Path

from matunya_bot_final.non_generators.task_15.validators.general_triangles_validator import (
    GeneralTrianglesValidator
)


def run_pattern(pattern_name: str, max_cases: int = 10, random_case: bool = False):
    """
    Универсальный прогон задач одного паттерна.

    pattern_name — имя паттерна ('triangle_area_by_dividing_point', ...)
    max_cases — сколько задач выводить
    random_case — если True → выводим только одну случайную задачу
    """

    validator = GeneralTrianglesValidator()

    # ПРАВИЛЬНЫЙ путь к general_triangles.txt
    data_file = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "non_generators"
        / "task_15"
        / "definitions"
        / "general_triangles.txt"
    )

    if not data_file.exists():
        raise FileNotFoundError(f"Не найден файл с задачами: {data_file}")

    with open(data_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Фильтруем строки по паттерну
    pattern_lines = [line.strip() for line in lines if line.startswith(pattern_name + "|")]

    print(f"\n==================== ТЕСТ ПАТТЕРНА: '{pattern_name}' ====================")
    print(f"🔎 Найдено задач: {len(pattern_lines)}")

    # Рандомная задача
    if random_case and pattern_lines:
        pattern_lines = [random.choice(pattern_lines)]
        print("🎲 Выбрана СЛУЧАЙНАЯ задача\n")

    else:
        print(f"🔢 Печатаем первые {min(max_cases, len(pattern_lines))}\n")
        pattern_lines = pattern_lines[:max_cases]

    # Обработка
    for i, raw_line in enumerate(pattern_lines, start=1):
        print(f"\n--- Пример #{i} ---")
        print(f"Сырая строка: {raw_line}")

        try:
            pattern, text = raw_line.split("|", 1)
        except ValueError:
            print("❌ Ошибка: нет разделителя '|'")
            continue

        raw_data = {"id": None, "pattern": pattern, "text": text}

        try:
            result = validator.validate_one(raw_data)
        except Exception as e:
            print(f"❌ Ошибка валидатора: {e}")
            continue

        print("--- Итоговый JSON ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))


@pytest.mark.parametrize(
    "pattern_name, max_cases, random_case",
    [
        #("triangle_by_two_angles_and_side", 10, False),
        # Можно включать другие паттерны:
        #("triangle_area_by_sin" , 30, False),
        # ("triangle_area_by_midpoints", 10, False),
        #("triangle_area_by_parallel_line", 30, False),
        ("triangle_area_by_dividing_point", 30, False),
        # ("cosine_law_find_cos", 10, False),
        # Чтобы тестировать рандомные примеры:
        # ("triangle_by_two_angles_and_side", 1, True),
    ]
)
def test_pattern(pattern_name, max_cases, random_case):
    run_pattern(pattern_name, max_cases, random_case)

