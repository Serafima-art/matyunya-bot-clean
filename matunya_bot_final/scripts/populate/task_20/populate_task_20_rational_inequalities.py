"""
populate_task_20_rational_inequalities.py
=========================================
Создаёт задания подтипа rational_inequalities для задания №20 (ОГЭ-2026).

Паттерны:
  1. compare_unit_fractions_linear            → 1/x ⊙ 1/(x−a)
  2. const_over_quadratic_nonpos_nonneg       → −C/(x²+bx+c) ⊙ 0
  3. x_vs_const_over_x                        → x ⊙ K/x
  4. neg_const_over_shifted_square_minus_const→ −C/((x−a)²−d) ⊙ 0

Все сгенерированные задачи записываются в общий файл:
matunya_bot_final/data/tasks_20/tasks_20.json
в формате {"tasks": [ ... ]}.
"""

from __future__ import annotations
import random
import json
from pathlib import Path
from matunya_bot_final.task_generators.task_20.generators.rational_inequalities_generator import (
    generate_task_20_rational_inequalities,
)
from matunya_bot_final.task_generators.task_20.validators.rational_inequalities_validator import (
    validate_task_20_rational_inequalities,
)


# ==========================================================
# Константы и пути
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DB_PATH = PROJECT_ROOT / "matunya_bot_final" / "data" / "tasks_20" / "tasks_20.json"
OUTPUT_DIR = PROJECT_ROOT / "matunya_bot_final" / "temp" / "task_20"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# Основная логика генерации
# ==========================================================

def main() -> None:
    print("🔄 Генерация заданий rational_inequalities...\n")

    patterns = [
        "compare_unit_fractions_linear",
        "const_over_quadratic_nonpos_nonneg",
        "x_vs_const_over_x",
        "neg_const_over_shifted_square_minus_const",
    ]

    generated_tasks = []

    for i in range(40):
        pattern = random.choice(patterns)
        task_data = generate_task_20_rational_inequalities(pattern=pattern)

        is_valid, errors = validate_task_20_rational_inequalities(task_data), []
        if isinstance(is_valid, tuple):
            is_valid, errors = is_valid

        if is_valid:
            generated_tasks.append(task_data)
            ans = task_data.get("answer", ["?"])[0]
            print(f"✅ {i+1:02}) {pattern:<40} → {ans}")
        else:
            print(f"❌ {i+1:02}) {pattern:<40} → INVALID")
            if errors:
                for e in errors:
                    print("   •", e)

    # ======================================================
    # Финальное сохранение с ключом "tasks"
    # ======================================================
    if DB_PATH.exists():
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "tasks" in data:
                    tasks = data["tasks"]
                elif isinstance(data, list):
                    tasks = data
                else:
                    tasks = []
        except json.JSONDecodeError:
            tasks = []
    else:
        tasks = []

    tasks.extend(generated_tasks)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    print(
        f"\n📦 Добавление завершено!\n"
        f"Всего новых задач создано: {len(generated_tasks)}\n"
        f"Уникальных добавлено в базу: {len(tasks)}\n"
        f"Файл БД: {DB_PATH}\n"
    )

    # Сохраним один пример в temp для ручной проверки
    if generated_tasks:
        sample_path = OUTPUT_DIR / "sample_rational_inequality.json"
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(generated_tasks[0], f, ensure_ascii=False, indent=2)
        print(f"💾 Пример сохранён в {sample_path}")


if __name__ == "__main__":
    main()
