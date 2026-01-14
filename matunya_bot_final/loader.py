# loader.py
"""
Загрузчик баз заданий (наш "склад").
Читает все JSON-файлы из папки data и складывает их в TASKS_DB.
"""

import json
from pathlib import Path

# Корень проекта
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

# Глобальный "склад" задач
TASKS_DB: dict[str, list[dict]] = {}


def load_json_file(path: Path) -> list[dict]:
    """Безопасная загрузка JSON-массива задач."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] Файл не найден: {path}")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Ошибка чтения JSON {path}: {e}")
        return []


def load_all_tasks():
    """Загружает все JSON из data/* в TASKS_DB."""
    global TASKS_DB

    # Список наших «складов»
    task_files = {
        "6": DATA_DIR / "tasks_6" / "tasks_6.json",
        "7": DATA_DIR / "tasks_7" / "tasks_7.json",
        "8": DATA_DIR / "tasks_8" / "tasks_8.json",
        "9": DATA_DIR / "tasks_9" / "tasks_9.json",
        "11": DATA_DIR / "tasks_11" / "tasks_11.json",
        "12": DATA_DIR / "tasks_12" / "tasks_12.json",
        "15": DATA_DIR / "tasks_15" / "tasks_15.json",
        "16": DATA_DIR / "tasks_16" / "tasks_16.json",
        "20": DATA_DIR / "tasks_20" / "tasks_20.json",
    }

    for key, path in task_files.items():
        TASKS_DB[key] = load_json_file(path)
        print(f"[DEBUG] Задание {key}: загружено {len(TASKS_DB[key])} задач")


# Загружаем при импорте
load_all_tasks()
