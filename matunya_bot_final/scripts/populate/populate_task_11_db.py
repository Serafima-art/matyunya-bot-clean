"""
populate_task_11_db.py
Скрипт для генерации и сохранения задач №11 (подтипы).
"""

import argparse
import json
import shutil
from pathlib import Path

from matunya_bot_final.task_generators.task_11.generators import GENERATOR_MAP, generate_task_11_by_subtype
from matunya_bot_final.task_generators.task_11.validators import (
    validate_task_11_match_signs_a_c,
    validate_task_11_form_match_mixed,
    validate_task_11_match_signs_k_b,
)

# ==============================
# Пути
# ==============================
DB_PATH = Path("matunya_bot_final/data/tasks_11/tasks_11.json")
TEMP_DIR = Path("matunya_bot_final/temp/task_11")

# ==============================
# Карта валидаторов
# ==============================
VALIDATOR_MAP = {
    "match_signs_a_c": validate_task_11_match_signs_a_c,
    "form_match_mixed": validate_task_11_form_match_mixed,
    "match_signs_k_b": validate_task_11_match_signs_k_b,
}

# ==============================
# Функция populate
# ==============================
def populate_db(n: int = 5, clear: bool = False, no_clean: bool = False):
    tasks = []

    if clear and DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[✓] Очистили базу данных ({DB_PATH.name})")

    if clear and TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
        print(f"[✓] Очистили временные файлы")

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    for subtype, generator in GENERATOR_MAP.items():
        validator = VALIDATOR_MAP[subtype]
        for _ in range(n):
            task = generator()
            # --- Валидируем задачу ---
            is_valid, errors = validator(task)
            if not is_valid:
                print(f"[WARN] Ошибки генерации {subtype}:")
                for err in errors:
                    print(f"   • {err}")
                continue

            # ⚠️ Чистим несериализуемые функции перед сохранением
            for fd in task.get("func_data", []):
                if "func" in fd:
                    fd.pop("func")

            tasks.append(task)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(tasks, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"[✓] Сохранили {len(tasks)} задач в {DB_PATH}")


# ==============================
# CLI
# ==============================
def main():
    parser = argparse.ArgumentParser(description="Populate tasks_11.json with generated tasks")
    parser.add_argument("--n", type=int, default=5, help="Количество задач на каждый подтип")
    parser.add_argument("--clear", action="store_true", help="Очистить БД и временные файлы перед генерацией")
    parser.add_argument("--no-clean", action="store_true", help="Не очищать временные файлы после генерации")
    args = parser.parse_args()

    populate_db(n=args.n, clear=args.clear, no_clean=args.no_clean)


if __name__ == "__main__":
    main()
