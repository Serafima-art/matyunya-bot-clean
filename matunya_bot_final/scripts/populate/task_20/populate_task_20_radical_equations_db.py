"""Populate script for task 20 radical_equations subtype."""

from __future__ import annotations
import json
import sys
from pathlib import Path

from matunya_bot_final.task_generators.task_20.generators.radical_equations_generator import (
    generate_task_20_radical_equations,
)
from matunya_bot_final.task_generators.task_20.validators.radical_equations_validator import (
    validate_task_20_radical_equations,
)


def main(output_dir: str | None = None, total: int = 30, pattern: str | None = None) -> None:
    """
    Генерирует несколько заданий указанного подтипа и сохраняет их в общий JSON.
    Параметры:
      total  – сколько заданий создать
      pattern – какой паттерн использовать (sum_zero, same_radical_cancel, cancel_identical_radicals)
    """
    from matunya_bot_final.task_generators.task_20.generators import radical_equations_generator as gen

    base_path = Path(output_dir or "matunya_bot_final/data/tasks_20")
    base_path.mkdir(parents=True, exist_ok=True)

    file_path = base_path / "tasks_20.json"
    tasks = []

    for _ in range(total):
        if pattern == "cancel_identical_radicals":
            equation, answers, variables = gen._generate_cancel_identical_radicals_task()
            variables.setdefault("solution_pattern", "cancel_identical_radicals")
            task = {
                "id": f"20_radical_equations_{pattern}_{_}",
                "task_number": 20,
                "topic": "equations",
                "subtype": "radical_equations",
                "question_text": f"Реши уравнение:\n{equation}",
                "answer": answers,
                "variables": variables,
            }
        else:
            task = generate_task_20_radical_equations()

        try:
            validate_task_20_radical_equations(task)
            tasks.append(task)
        except Exception as e:
            print(f"⚠️  Task skipped due to validation error: {e}")
            continue

    # Загружаем существующие задачи, если файл уже есть
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    # Добавляем новые
    existing.extend(tasks)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"✅ Added {len(tasks)} tasks ({pattern or 'mixed patterns'}) to {file_path}")


if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 30
    pattern = sys.argv[2] if len(sys.argv) > 2 else None
    main(total=total, pattern=pattern)
