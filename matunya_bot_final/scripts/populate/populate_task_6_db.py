"""
populate_task_6_db.py — единый скрипт для генерации и записи всех подтипов задания №6.

Темы:
  1. common_fractions        → actions with common fractions
  2. decimal_fractions       → actions with decimal fractions
  3. mixed_fractions         → actions with mixed (common + decimal) fractions
  4. powers                  → powers with fractions and powers of ten

Выходной файл:
  matunya_bot_final/data/tasks_6/tasks_6.json
"""

import json
import os
from datetime import datetime

from matunya_bot_final.task_generators.task_6.generators.common_fractions_generator import (
    generate_common_fractions_tasks,
)
from matunya_bot_final.task_generators.task_6.generators.decimal_fractions_generator import (
    generate_decimal_fractions_tasks,
)
from matunya_bot_final.task_generators.task_6.generators.mixed_fractions_generator import (
    generate_mixed_fractions_tasks,
)
from matunya_bot_final.task_generators.task_6.generators.powers_generator import (
    generate_powers_tasks,
)

# --- Путь к БД ---
OUTPUT_PATH = os.path.join(
    "matunya_bot_final", "data", "tasks_6", "tasks_6.json"
)

# --- Основная функция ---
def main() -> None:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    print("=== 🧮 Генерация заданий №6 ===")
    all_tasks = []

    # 1. Обыкновенные дроби
    cf_tasks = generate_common_fractions_tasks(30)
    print(f"✅ common_fractions: {len(cf_tasks)} задач")
    all_tasks.extend(cf_tasks)

    # 2. Десятичные дроби
    df_tasks = generate_decimal_fractions_tasks(30)
    print(f"✅ decimal_fractions: {len(df_tasks)} задач")
    all_tasks.extend(df_tasks)

    # 3. Смешанные типы
    mf_tasks = generate_mixed_fractions_tasks(20)
    print(f"✅ mixed_fractions: {len(mf_tasks)} задач")
    all_tasks.extend(mf_tasks)

    # 4. Степени
    pw_tasks = generate_powers_tasks(20)
    print(f"✅ powers: {len(pw_tasks)} задач")
    all_tasks.extend(pw_tasks)

    print(f"\nВсего сгенерировано: {len(all_tasks)} заданий")

    # --- Бэкап старой версии ---
    if os.path.exists(OUTPUT_PATH):
        backup_path = OUTPUT_PATH.replace(
            ".json", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        os.rename(OUTPUT_PATH, backup_path)
        print(f"💾 Старый файл сохранён как {backup_path}")

    # --- Сохраняем в JSON ---
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_tasks, f, ensure_ascii=False, indent=2)

    print(f"🎉 Файл успешно записан: {OUTPUT_PATH}\n")


# --- Точка входа ---
if __name__ == "__main__":
    main()
