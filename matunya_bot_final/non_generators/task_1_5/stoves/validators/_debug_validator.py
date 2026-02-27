import sys
import os
import argparse
import json

# --- НАСТРОЙКА ПУТЕЙ ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../../"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Абсолютный импорт валидатора
from matunya_bot_final.non_generators.task_1_5.stoves.validators.stoves_validator import (
    StovesValidator
)


def run_debug(to_file: bool = False) -> None:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    INPUT_FILE = os.path.abspath(
        os.path.join(BASE_DIR, "../definitions/stoves_variants.txt")
    )

    OUTPUT_LOG = os.path.join(BASE_DIR, "debug_stoves_validator_output.txt")
    OUTPUT_JSON = os.path.join(BASE_DIR, "debug_stoves_validator_json_output.json")

    log_lines = []
    all_variants_json = []

    def log(message: str) -> None:
        print(message)
        log_lines.append(message)

    log("🔬 ДИАГНОСТИКА ВАЛИДАТОРА (Печи 1-5)")
    log(f"📂 Файл: {INPUT_FILE}")
    log("=" * 60)

    if not os.path.exists(INPUT_FILE):
        log(f"❌ Файл {INPUT_FILE} не найден!")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    raw_blocks = content.split("=== VARIANT START ===")
    validator = StovesValidator()

    total_valid = 0
    total_errors = 0

    for i, block in enumerate(raw_blocks):
        if i == 0:
            continue

        clean_text = block.split("=== VARIANT END ===")[0].strip()
        if not clean_text:
            continue

        var_id_line = [
            L for L in clean_text.split("\n")
            if L.startswith("VARIANT_CODE:")
        ]

        var_id = (
            var_id_line[0].split(":", 1)[1].strip()
            if var_id_line else f"Unknown_{i}"
        )

        log(f"\n📂 ВАРИАНТ: {var_id}")
        log("-" * 40)

        is_valid, container, errors = validator.validate({"question_text": clean_text})

        if is_valid:
            total_valid += 1
            log("✅ Статус: ВАЛИДНО")

            # Сейчас у нас проверяется только Q1
            for q in container.get("questions", []):
                log(
                    f"   🔹 Q{q['q_number']} "
                    f"[{q['narrative']}]: "
                    f"Ответ = {q['answer']}"
                )

            all_variants_json.append(container)

        else:
            total_errors += 1
            log("❌ Статус: ОШИБКА")
            for err in errors:
                log(f"   🔴 {err}")

    log("\n" + "=" * 60)
    log(f"📊 ИТОГ: Успешно: {total_valid} | Ошибок: {total_errors}")

    # --- Сохранение файлов ---
    if to_file:
        with open(OUTPUT_LOG, "w", encoding="utf-8") as lf:
            lf.write("\n".join(log_lines))

        with open(OUTPUT_JSON, "w", encoding="utf-8") as jf:
            json.dump(all_variants_json, jf, indent=2, ensure_ascii=False)

        print(f"\n📄 Лог сохранен в:\n{OUTPUT_LOG}")
        print(f"📦 JSON сохранен в:\n{OUTPUT_JSON}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--to-file",
        action="store_true",
        help="Сохранить вывод в файл"
    )
    args = parser.parse_args()

    run_debug(args.to_file)
