"""
Лабораторный стенд для отладки ВАЛИДАТОРОВ Задания 15.
Запускается локально, без Telegram.

Читает сырьевые файлы (.txt), прогоняет их через указанный валидатор
и красиво печатает итоговый JSON для проверки.
"""

import json
import sys
import logging
import random
from pathlib import Path

# --- НАСТРОЙКА ПУТЕЙ ---
# Поднимаемся на 4 уровня: _debug -> validators -> task_15 -> non_generators -> matunya_bot_final
project_root = Path(__file__).resolve().parents[4]
sys.path.append(str(project_root / "matunya_bot_final"))

# --- ИМПОРТЫ ---
try:
    # Импортируем наш валидатор
    from non_generators.task_15.validators.general_triangles_validator import GeneralTrianglesValidator
except ImportError as e:
    print(f"🔴 Ошибка импорта: {e}. Проверьте правильность путей и структуру проекта.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# --- КОНФИГУРАЦИЯ ТЕСТА ---
# Имя файла с сырьем, который будем тестировать
DEFINITIONS_FILE = "general_triangles.txt"

# Класс валидатора, который будем использовать
VALIDATOR_CLASS = GeneralTrianglesValidator

# Сколько случайных примеров для КАЖДОГО паттерна показать (None - показать все)
LIMIT_PER_PATTERN = 2

# -------------------------------------------------------------------------

def load_raw_tasks(filename: str) -> list:
    """Загружает все строки из указанного .txt файла."""
    definitions_dir = project_root / "matunya_bot_final" / "non_generators" / "task_15" / "definitions"
    file_path = definitions_dir / filename

    if not file_path.exists():
        logger.error(f"❌ Файл с сырьем не найден: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return lines
    except Exception as e:
        logger.error(f"❌ Ошибка чтения файла {filename}: {e}")
        return []


def run_test():
    """
    Запускает валидатор на сырьевых данных и печатает результат.
    """
    print(f"\n_> 🔬 ДИАГНОСТИКА ВАЛИДАТОРА: '{VALIDATOR_CLASS.__name__}'")
    print(f"_> 📂 Файл с данными: '{DEFINITIONS_FILE}'")
    print("-" * 70)

    raw_lines = load_raw_tasks(DEFINITIONS_FILE)
    if not raw_lines:
        return

    # Группируем задачи по паттернам
    tasks_by_pattern = {}
    for line in raw_lines:
        if "|" not in line: continue
        pattern = line.split("|", 1)[0].strip()
        if pattern not in tasks_by_pattern:
            tasks_by_pattern[pattern] = []
        tasks_by_pattern[pattern].append(line)

    if not tasks_by_pattern:
        logger.warning("⚠️ Не найдено ни одной валидной строки в файле сырья.")
        return

    print(f"✅ Найдено паттернов в файле: {len(tasks_by_pattern)}")

    validator = VALIDATOR_CLASS()

    # Прогоняем тест для каждого паттерна
    for pattern, tasks in tasks_by_pattern.items():
        print(f"\n{'='*20} ТЕСТ ПАТТЕРНА: '{pattern}' {'='*20}")

        random.shuffle(tasks)

        limit = LIMIT_PER_PATTERN if LIMIT_PER_PATTERN is not None else len(tasks)

        for i, line in enumerate(tasks[:limit]):
            print(f"\n--- Пример #{i+1} ---")
            print(f"Сырая строка: {line}")

            try:
                pattern_from_line, text = line.split("|", 1)
                raw_data = {"pattern": pattern_from_line.strip(), "text": text.strip()}

                # Запускаем валидатор!
                result_json = validator.validate(raw_data)

                print("--- Итоговый JSON ---")
                # Красиво печатаем JSON для легкой проверки
                print(json.dumps(result_json, indent=2, ensure_ascii=False))

            except Exception as e:
                logger.error(f"❌ CRASH VALIDATOR: {e}", exc_info=True)

            print("-" * 40)

if __name__ == "__main__":
    run_test()
