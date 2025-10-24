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

# --- Валидаторы (подключаем мягко, чтобы ничего не сломать, если какого-то ещё нет) ---
try:
    from matunya_bot_final.task_generators.task_6.validators.common_fractions_validator import (
        validate_common_fractions_task,
    )
except Exception:  # noqa: BLE001
    validate_common_fractions_task = None

try:
    from matunya_bot_final.task_generators.task_6.validators.decimal_fractions_validator import (
        validate_decimal_fractions_task,
    )
except Exception:  # noqa: BLE001
    validate_decimal_fractions_task = None

try:
    from matunya_bot_final.task_generators.task_6.validators.mixed_fractions_validator import (
        validate_mixed_fractions_task,
    )
except Exception:  # noqa: BLE001
    validate_mixed_fractions_task = None

try:
    from matunya_bot_final.task_generators.task_6.validators.powers_validator import (
        validate_powers_task,
    )
except Exception:  # noqa: BLE001
    validate_powers_task = None


# --- Путь к БД ---
OUTPUT_PATH = os.path.join("matunya_bot_final", "data", "tasks_6", "tasks_6.json")


# --- Вспомогательные фильтры ---
def _filter_fallbacks(tasks):
    """Удаляет заглушечные задачи (fallbacks), если вдруг попались."""
    before = len(tasks)
    tasks = [
        t
        for t in tasks
        if not t.get("subtype", "").endswith("_error_recovery")
        and t.get("meta", {}).get("pattern_id") != "recovery_fallback"
    ]
    removed = before - len(tasks)
    if removed > 0:
        print(f"⚠️  Удалено {removed} заглушечных задач (fallbacks)")
    return tasks


def _filter_valid(tasks, validator, label: str):
    """
    Прогоняет задачи через валидатор по ГОСТ-ВАЛИДАТОР-2025.
    Если валидатор отсутствует — пропускаем фильтрацию.
    """
    if validator is None:
        print(f"ℹ️  Валидатор для {label} не найден — фильтрация по ГОСТ пропущена.")
        return tasks

    valid = []
    discarded = 0
    for t in tasks:
        try:
            is_valid, errors = validator(t)
        except Exception as exc:  # noqa: BLE001
            is_valid, errors = False, [f"Исключение валидатора: {exc}"]

        if not is_valid:
            discarded += 1
            tid = t.get("id", "<no-id>")
            # Печатаем только первую строку ошибки, чтобы не зашумлять
            first_err = errors[0] if errors else "Неизвестная ошибка"
            print(f"[⚠️ Брак {label}] {tid}: {first_err}")
            continue
        valid.append(t)

    if discarded:
        print(f"🧹 Отбраковано {discarded} задач для {label}")
    return valid


# --- Основная функция ---
def main() -> None:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    print("=== 🧮 Генерация заданий №6 (ГОСТ-JSON-6) ===")
    print("Все задачи будут сохранены в новом стандарте ГОСТ-JSON-6.")
    all_tasks = []

    # 1. Обыкновенные дроби
    cf_tasks = generate_common_fractions_tasks(30)
    cf_tasks = _filter_fallbacks(cf_tasks)
    cf_tasks = _filter_valid(cf_tasks, validate_common_fractions_task, "common_fractions")
    print(f"✅ common_fractions: {len(cf_tasks)} валидных задач")
    all_tasks.extend(cf_tasks)

    # 2. Десятичные дроби
    df_tasks = generate_decimal_fractions_tasks(30)
    df_tasks = _filter_fallbacks(df_tasks)
    df_tasks = _filter_valid(df_tasks, validate_decimal_fractions_task, "decimal_fractions")
    print(f"✅ decimal_fractions: {len(df_tasks)} валидных задач")
    all_tasks.extend(df_tasks)

    # 3. Смешанные типы
    mf_tasks = generate_mixed_fractions_tasks(20)
    mf_tasks = _filter_fallbacks(mf_tasks)
    mf_tasks = _filter_valid(mf_tasks, validate_mixed_fractions_task, "mixed_fractions")
    print(f"✅ mixed_fractions: {len(mf_tasks)} валидных задач")
    all_tasks.extend(mf_tasks)

    # 4. Степени
    pw_tasks = generate_powers_tasks(20)
    pw_tasks = _filter_fallbacks(pw_tasks)
    pw_tasks = _filter_valid(pw_tasks, validate_powers_task, "powers")
    print(f"✅ powers: {len(pw_tasks)} валидных задач")
    all_tasks.extend(pw_tasks)

    print(f"\n📊 Всего к записи: {len(all_tasks)} валидных заданий")

    # --- Если файл уже есть, просто удаляем ---
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)
        print("🧹 Старый tasks_6.json удалён перед перезаписью")

    # --- Сохраняем в JSON ---
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_tasks, f, ensure_ascii=False, indent=2)

    print(f"🎉 Файл успешно записан: {OUTPUT_PATH}\n")


# --- Точка входа ---
if __name__ == "__main__":
    main()

# Для запуска скрипта используйте команду:
#
#   python -m matunya_bot_final.scripts.populate.populate_task_6_db
