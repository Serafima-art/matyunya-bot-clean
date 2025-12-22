# matunya_bot_final/non_generators/task_15/build.py
# -*- coding: utf-8 -*-

"""
Сборщик JSON-базы для Задания 15.

ВАЖНО (после перехода на PNG):
- билд НЕ читает картинки (ни SVG, ни PNG)
- в JSON хранится только имя файла в поле "image_file" (его проставляет валидатор)
- сами PNG лежат в: matunya_bot_final/non_generators/task_15/assets
"""

import os
import json
import sys

# Добавляем корень проекта в sys.path, чтобы импорты работали корректно
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from matunya_bot_final.non_generators.task_15.validators.angles_validator import AnglesValidator
from matunya_bot_final.non_generators.task_15.validators.general_triangles_validator import (
    GeneralTrianglesValidator,
)

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFINITIONS_DIR = os.path.join(BASE_DIR, "definitions")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Правильный путь к корню пакета matunya_bot_final (поднимаемся от .../task_15 на 2 уровня)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir, os.pardir))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "tasks_15")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tasks_15.json")

# --- КАРТА ВАЛИДАТОРОВ ---
VALIDATOR_MAPPING = {
    "angles.txt": AnglesValidator,
    "general_triangles.txt": GeneralTrianglesValidator,
}


def _asset_exists(filename: str) -> bool:
    """Мягкая проверка наличия ассета (PNG) — предупреждаем, но не падаем."""
    if not filename:
        return False
    return os.path.exists(os.path.join(ASSETS_DIR, filename))


def build() -> None:
    print("🏭 ЗАПУСК СБОРОЧНОГО ЦЕХА ЗАДАНИЯ 15...")
    print(f"📍 Директория определений: {DEFINITIONS_DIR}")
    print(f"📍 Директория ассетов: {ASSETS_DIR}")
    print(f"📍 Файл на выходе: {OUTPUT_FILE}")
    print("-" * 50)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_tasks: list[dict] = []
    current_id = 1500000

    for filename, ValidatorClass in VALIDATOR_MAPPING.items():
        filepath = os.path.join(DEFINITIONS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"🔸 Пропуск {filename}: файл ещё не создан.")
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
            if not line or line.startswith("#"):
                continue

            try:
                if "|" not in line:
                    raise ValueError("Неверный формат строки (нет разделителя '|').")

                pattern, text = line.split("|", 1)
                raw_data = {"pattern": pattern.strip(), "text": text.strip()}

                # --- ГИБКИЙ ВЫЗОВ ВАЛИДАТОРА ---
                if hasattr(validator, "validate_one"):
                    task_data = validator.validate_one(raw_data)
                else:
                    task_data = validator.validate(raw_data)

                if not isinstance(task_data, dict):
                    raise ValueError("Валидатор вернул не dict.")

                # --- ID ---
                current_id += 1
                task_data["id"] = current_id

                # --- КАРТИНКИ ---
                # Ничего не читаем и не встраиваем в JSON.
                # Только мягко предупредим, если файл указан, но его нет.
                img_filename = task_data.get("image_file")
                if img_filename and not _asset_exists(str(img_filename)):
                    print(f"⚠️  WARNING: ассет не найден в assets: {img_filename} (строка {line_num})")

                all_tasks.append(task_data)
                file_tasks_count += 1

            except Exception as e:
                print(f"❌ Ошибка в файле {filename} на строке {line_num}:")
                print(f"   Текст: {line[:120]}...")
                print(f"   Причина: {e}")

        print(f"   ✅ Добавлено задач: {file_tasks_count}")

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_tasks, f, ensure_ascii=False, indent=2)

        print("-" * 50)
        print("🎉 СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print(f"📊 Всего задач в базе: {len(all_tasks)}")
        print(f"💾 Путь к файлу: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ FATAL ERROR: Не удалось сохранить итоговый файл: {e}")


if __name__ == "__main__":
    build()
