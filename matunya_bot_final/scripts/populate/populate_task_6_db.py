# scripts/populate_task_6_db.py

import sys
from pathlib import Path

# Добавляем корневую папку проекта в пути для поиска модулей
# Это нужно, чтобы Python мог найти папку py_generators
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
import json
from pathlib import Path
from typing import Dict, Any, List

# Импортируем "карту генераторов" и "сборщик" из нашей "фабрики"
from matunya_bot_final.py_generators.task_6_generator import GENERATOR_MAP, create_task_object

# --- НАСТРОЙКИ ---
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "tasks_6.json"
TASKS_PER_SUBTYPE = 7 # Давай сгенерируем по 7 заданий каждого из 14 типов = 98 заданий!

# ================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ================================================================
def generate_all_tasks():
    """
    Главная функция, которая запускает все 14 генераторов из карты
    и сохраняет результат, полностью перезаписывая файл.
    """
    all_tasks: List[Dict[str, Any]] = []
    subtype_counters: Dict[str, int] = {}

    print(f"▶️  Начинаю генерацию заданий №6 для {len(GENERATOR_MAP)} подтипов...")

    # Умный цикл, который проходит по всем генераторам
    for subtype_key, generator_func in GENERATOR_MAP.items():
        print(f"  -> Генерирую задания для подтипа: {subtype_key}...")
        for _ in range(TASKS_PER_SUBTYPE):
            # Вызываем генератор
            _, text, answer = generator_func()
            
            # Считаем, сколько заданий этого типа мы уже создали
            subtype_counters[subtype_key] = subtype_counters.get(subtype_key, 0) + 1
            counter = subtype_counters[subtype_key]
            
            # Создаем УНИФИЦИРОВАННЫЙ ID
            task_id = f"6_{subtype_key}_{counter:03d}"
            
            # Собираем и добавляем объект задания
            all_tasks.append(create_task_object(task_id, subtype_key, text, answer))

    # --- СОХРАНЕНИЕ В ФАЙЛ ---
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_tasks, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Успешно сгенерировано и сохранено {len(all_tasks)} заданий в файл:")
        print(f"   -> {OUTPUT_FILE}")
    except Exception as e:
        print(f"\n❌ Ошибка при сохранении файла: {e}")

if __name__ == "__main__":
    generate_all_tasks()