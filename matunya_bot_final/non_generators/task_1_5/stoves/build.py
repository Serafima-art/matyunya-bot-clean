import os
import sys
import json

# --- НАСТРОЙКА ПУТЕЙ ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Импорт валидатора
from matunya_bot_final.non_generators.task_1_5.stoves.validators.stoves_validator import (
    StovesValidator
)


def build_database() -> None:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    INPUT_FILE = os.path.abspath(
        os.path.join(BASE_DIR, "definitions/stoves_variants.txt")
    )

    OUTPUT_DIR = os.path.abspath(
        os.path.join(project_root, "matunya_bot_final/data/tasks_1_5/stoves")
    )

    OUTPUT_FILE = os.path.join(
        OUTPUT_DIR,
        "tasks_1_5_stoves.json"
    )

    print("🏗 СБОРКА БАЗЫ ДАННЫХ (Печи 1–5)")
    print(f"📂 Источник: {INPUT_FILE}")

    if not os.path.exists(INPUT_FILE):
        print("❌ Файл definitions/stoves_variants.txt не найден!")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    raw_blocks = content.split("=== VARIANT START ===")
    validator = StovesValidator()

    all_variants = []
    total_valid = 0
    total_errors = 0

    for i, block in enumerate(raw_blocks):
        if i == 0:
            continue

        clean_text = block.split("=== VARIANT END ===")[0].strip()
        if not clean_text:
            continue

        is_valid, container, errors = validator.validate(
            {"question_text": clean_text}
        )

        if is_valid:
            total_valid += 1
            all_variants.append(container)
        else:
            total_errors += 1
            print("\n❌ Ошибка в варианте:")
            for err in errors:
                print(f"   🔴 {err}")

    print("\n" + "=" * 60)
    print(f"📊 Итог: Валидных: {total_valid} | Ошибок: {total_errors}")

    if total_valid == 0:
        print("❌ Нет валидных вариантов. База не создана.")
        return

    # создаём папку если её нет
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_variants, f, indent=2, ensure_ascii=False)

    print("\n✅ База успешно создана!")
    print(f"📦 Файл сохранён: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_database()
