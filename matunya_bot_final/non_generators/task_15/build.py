# matunya_bot_final/non_generators/task_15/build.py

import os
import json
import sys

# Добавляем корневую директорию проекта в sys.path, чтобы импорты работали корректно
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Импортируем валидаторы
from matunya_bot_final.non_generators.task_15.validators.angles_validator import AnglesValidator
from matunya_bot_final.non_generators.task_15.validators.general_triangles_validator import GeneralTrianglesValidator

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFINITIONS_DIR = os.path.join(BASE_DIR, "definitions")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ИСПРАВЛЕНИЕ: Правильный путь к корню проекта (matunya_bot_final)
# Поднимаемся на 2 уровня вверх от task_15
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir, os.pardir))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "tasks_15")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tasks_15.json")

# --- КАРТА ВАЛИДАТОРОВ ---
VALIDATOR_MAPPING = {
    "angles.txt": AnglesValidator,
    "general_triangles.txt": GeneralTrianglesValidator,
}

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def load_svg_content(filename: str) -> str:
    if not filename: return ""
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        print(f"⚠️  WARNING: SVG файл не найден: {filename}")
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ ERROR: Не удалось прочитать SVG {filename}: {e}")
        return ""

# --- ОСНОВНАЯ ФУНКЦИЯ СБОРКИ ---
def build():
    print(f"🏭 ЗАПУСК СБОРОЧНОГО ЦЕХА ЗАДАНИЯ 15...")
    print(f"📍 Директория определений: {DEFINITIONS_DIR}")
    print(f"📍 Директория ассетов: {ASSETS_DIR}")
    print(f"📍 Файл на выходе: {OUTPUT_FILE}")
    print("-" * 50)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_tasks = []
    current_id = 1500000

    for filename, ValidatorClass in VALIDATOR_MAPPING.items():
        filepath = os.path.join(DEFINITIONS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"🔸 Пропуск {filename}: файл еще не создан.")
            continue
        print(f"🔨 Обработка {filename}...")
        try:
            validator = ValidatorClass()
        except Exception as e:
            print(f"❌ CRITICAL: Не удалось инициализировать валидатор для {filename}: {e}")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        file_tasks_count = 0
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"): continue

            try:
                if "|" not in line: raise ValueError("Неверный формат строки (нет разделителя '|').")
                pattern, text = line.split("|", 1)
                raw_data = {"pattern": pattern.strip(), "text": text.strip()}

                # --- ГИБКИЙ ВЫЗОВ ВАЛИДАТОРА ---
                # Проверяем, какой метод использовать
                if hasattr(validator, 'validate_one'):
                    # Для новых валидаторов
                    task_data = validator.validate_one(raw_data)
                else:
                    # Для старых (как AnglesValidator)
                    task_data = validator.validate(raw_data)

                current_id += 1
                task_data["id"] = current_id

                img_filename = task_data.get("image_file")
                task_data["image_svg"] = load_svg_content(img_filename) if img_filename else ""

                all_tasks.append(task_data)
                file_tasks_count += 1

            except Exception as e:
                print(f"❌ Ошибка в файле {filename} на строке {line_num}:")
                print(f"   Текст: {line[:70]}...")
                print(f"   Причина: {e}")

        print(f"   ✅ Добавлено задач: {file_tasks_count}")

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_tasks, f, ensure_ascii=False, indent=2)
        print("-" * 50)
        print(f"🎉 СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print(f"📊 Всего задач в базе: {len(all_tasks)}")
        print(f"💾 Путь к файлу: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ FATAL ERROR: Не удалось сохранить итоговый файл: {e}")

if __name__ == "__main__":
    build()
