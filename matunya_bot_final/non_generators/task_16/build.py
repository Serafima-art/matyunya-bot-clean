# matunya_bot_final/non_generators/task_16/build.py
# -*- coding: utf-8 -*-

"""
Сборщик JSON-базы для Задания 16.
Исправлен под новую архитектуру (task_context + answer в корне).
"""

import os
import json
import sys
import re

# Добавляем корень проекта в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(project_root)

from matunya_bot_final.non_generators.task_16.validators.central_and_inscribed_angles_validator import (
    CentralAndInscribedAnglesValidator,
)

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFINITIONS_DIR = os.path.join(BASE_DIR, "definitions")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(project_root, "matunya_bot_final", "data", "task_16")
OUTPUT_FILE = os.path.join(DATA_DIR, "tasks_16.json")

VALIDATOR_MAPPING = {
    "central_and_inscribed_angles.txt": CentralAndInscribedAnglesValidator,
}

START_ID = 1600000

def _asset_exists(filename: str) -> bool:
    if not filename: return True
    return os.path.exists(os.path.join(ASSETS_DIR, filename))

def load_and_parse_file(filepath: str) -> list[dict]:
    tasks = []
    current_narrative = None
    narrative_regex = re.compile(r"^#\s*(?:narrative|нарратив|Нарратив):\s*([a-zA-Z_0-9]+)")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line: continue

            narrative_match = narrative_regex.match(line)
            if narrative_match:
                current_narrative = narrative_match.group(1)
                continue

            if line.startswith("#"): continue

            if "|" in line:
                if not current_narrative:
                    print(f"⚠️ [WARN] Строка {line_num}: Нет нарратива! Пропуск.")
                    continue

                pattern, text = line.split("|", 1)
                tasks.append({
                    "pattern": pattern.strip(),
                    "narrative": current_narrative,
                    "question_text": text.strip(),
                    "answer": -1, # Фейковый ответ для запуска валидатора
                    "source_line": line_num
                })
            else:
                print(f"⚠️ [WARN] Строка {line_num}: Неверный формат.")

    except Exception as e:
        print(f"❌ Ошибка чтения файла {filepath}: {e}")

    return tasks

def build() -> None:
    print("\n" + "="*60)
    print("🏭 ЗАПУСК СБОРОЧНОГО ЦЕХА ЗАДАНИЯ 16")
    print(f"📍 Сырьё: {DEFINITIONS_DIR}")
    print(f"📍 Выход: {OUTPUT_FILE}")
    print("="*60 + "\n")

    os.makedirs(DATA_DIR, exist_ok=True)

    all_tasks: list[dict] = []
    current_id = START_ID
    total_errors = 0

    for filename, ValidatorClass in VALIDATOR_MAPPING.items():
        filepath = os.path.join(DEFINITIONS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"🔸 [SKIP] Файл {filename} не найден.")
            continue

        print(f"🔨 Обработка {filename}...")
        raw_tasks = load_and_parse_file(filepath)
        print(f"   📥 Загружено: {len(raw_tasks)}")

        try:
            validator = ValidatorClass()
        except Exception as e:
            print(f"❌ CRITICAL: Ошибка инициализации валидатора: {e}")
            continue

        file_valid_count = 0

        for task in raw_tasks:
            try:
                # ВАЛИДАЦИЯ (изменяет task in-place)
                is_valid, errors = validator.validate(task)

                # Фильтруем ошибки
                real_errors = [e for e in errors if "Неверный ответ" not in e and "Математическая ошибка" not in e]
                if not is_valid and real_errors:
                    print(f"   ❌ Ошибка (стр {task.get('source_line')}): {', '.join(real_errors)}")
                    total_errors += 1
                    continue

                # --- ПОСТ-ОБРАБОТКА ---
                current_id += 1
                task["id"] = current_id

                # --- ПРОВЕРКА ОТВЕТА (ОБНОВЛЕННАЯ ЛОГИКА) ---
                # Валидатор должен был заменить -1 на реальный ответ в поле "answer"
                final_answer = task.get("answer")
                if final_answer == -1 or final_answer is None:
                     print(f"   ⚠️ [WARN] Валидатор не рассчитал ответ для задачи {current_id} (остался -1)")
                     total_errors += 1
                     continue

                # Убедимся, что task_context существует (бывший solution_vars)
                if "task_context" not in task:
                     print(f"   ⚠️ [WARN] Отсутствует task_context для задачи {current_id}")
                     total_errors += 1
                     continue

                # Проверяем картинки
                imgs = [task.get("image_file"), task.get("help_image_file")]
                for img in imgs:
                    if not _asset_exists(img):
                        print(f"   ⚠️ [ASSET MISSING] {img}")

                if "source_line" in task: del task["source_line"]

                all_tasks.append(task)
                file_valid_count += 1

            except Exception as e:
                print(f"   ❌ CRASH: {e}")
                total_errors += 1

        print(f"   ✅ Успешно добавлено: {file_valid_count}")

    print("\n" + "-" * 50)
    if all_tasks:
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_tasks, f, ensure_ascii=False, indent=2)
            print("🎉 СБОРКА ЗАВЕРШЕНА!")
            print(f"📊 Всего задач: {len(all_tasks)}")
            if total_errors > 0:
                print(f"🗑 Отброшено ошибок: {total_errors}")
            print(f"💾 Файл: {OUTPUT_FILE}")
        except Exception as e:
            print(f"❌ FATAL ERROR: {e}")
    else:
        print("🤷‍♂️ База пуста.")

if __name__ == "__main__":
    build()
