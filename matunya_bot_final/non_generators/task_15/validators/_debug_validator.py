"""
Лабораторный стенд для отладки ВАЛИДАТОРА Задания 15
ТОЧЕЧНЫЙ РЕЖИМ: проверяем ТОЛЬКО triangle_area_by_parallel_line

Запускается локально, без Telegram.
"""

import json
import sys
import logging
from pathlib import Path

# ---------------------------------------------------------------------
# НАСТРОЙКИ
# ---------------------------------------------------------------------

TARGET_PATTERN = "triangle_area_by_parallel_line"
DEFINITIONS_FILE = "general_triangles.txt"

# ---------------------------------------------------------------------
# НАСТРОЙКА ПУТЕЙ
# Поднимаемся на 4 уровня: _debug -> validators -> task_15 -> non_generators -> matunya_bot_final
# ---------------------------------------------------------------------

project_root = Path(__file__).resolve().parents[4]
sys.path.append(str(project_root / "matunya_bot_final"))

# ---------------------------------------------------------------------
# ИМПОРТ ВАЛИДАТОРА
# ---------------------------------------------------------------------

try:
    from non_generators.task_15.validators.general_triangles_validator import (
        GeneralTrianglesValidator,
    )
except ImportError as e:
    print(f"🔴 Ошибка импорта валидатора: {e}")
    sys.exit(1)

# ---------------------------------------------------------------------
# ЛОГГИНГ
# ---------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# ЗАГРУЗКА СЫРЬЯ
# ---------------------------------------------------------------------


def load_raw_tasks(filename: str) -> list[str]:
    """
    Загружает все строки сырья из definitions/*.txt
    """
    definitions_dir = (
        project_root
        / "matunya_bot_final"
        / "non_generators"
        / "task_15"
        / "definitions"
    )
    file_path = definitions_dir / filename

    if not file_path.exists():
        logger.error(f"❌ Файл с сырьём не найден: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    except Exception as e:
        logger.error(f"❌ Ошибка чтения файла {filename}: {e}")
        return []


# ---------------------------------------------------------------------
# ОСНОВНОЙ ТЕСТ
# ---------------------------------------------------------------------


def run_test():
    print("\n" + "=" * 80)
    print("🔬 ДИАГНОСТИКА ВАЛИДАТОРА")
    print(f"🎯 ПАТТЕРН: {TARGET_PATTERN}")
    print(f"📂 ФАЙЛ СЫРЬЯ: {DEFINITIONS_FILE}")
    print("=" * 80)

    raw_lines = load_raw_tasks(DEFINITIONS_FILE)
    if not raw_lines:
        return

    # --- Фильтруем только нужный паттерн ---
    tasks = []
    for line in raw_lines:
        if "|" not in line:
            continue
        pattern, _ = line.split("|", 1)
        if pattern.strip() == TARGET_PATTERN:
            tasks.append(line)

    if not tasks:
        logger.warning(f"⚠️ В файле нет задач для паттерна {TARGET_PATTERN}")
        return

    print(f"✅ Найдено задач: {len(tasks)}")

    validator = GeneralTrianglesValidator()

    # --- Прогоняем ВСЕ задачи этого паттерна ---
    for i, line in enumerate(tasks, start=1):
        print("\n" + "-" * 80)
        print(f"🧪 Пример #{i}")
        print(f"📄 Сырьё: {line}")

        try:
            pattern_from_line, text = line.split("|", 1)
            raw_data = {
                "pattern": pattern_from_line.strip(),
                "text": text.strip(),
            }

            result_json = validator.validate(raw_data)

            print("✅ ВАЛИДАЦИЯ ПРОШЛА")
            print("📦 Итоговый JSON:")
            print(json.dumps(result_json, indent=2, ensure_ascii=False))

        except Exception as e:
            print("❌ CRASH VALIDATOR")
            logger.error(str(e), exc_info=True)

    print("\n" + "=" * 80)
    print("🏁 КОНЕЦ ДИАГНОСТИКИ")
    print("=" * 80)


# ---------------------------------------------------------------------

if __name__ == "__main__":
    run_test()
