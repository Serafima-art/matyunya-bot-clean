# scripts/populate_task_12_db.py

import json
import sys
from pathlib import Path

# --- Пути ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))


from matunya_bot_final.task_generators.task_12.task_12_generator import GENERATOR_MAP
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_12.TASK_12_MAP import TASK_12_MAP

OUTPUT_PATH = PROJECT_ROOT / "data" / "tasks_12" / "tasks_12.json"


def generate_tasks():

    tasks = []
    task_type = 12

    # Создаем обратную карту для быстрого поиска
    reverse_map = {}
    for category, sub_map in TASK_12_MAP.items():
        if isinstance(sub_map, dict):
            for subcategory, subtypes in sub_map.items():
                for subtype in subtypes:
                    reverse_map[subtype] = (category, subcategory)
        else:  # Для 'misc'
            for subtype in sub_map:
                reverse_map[subtype] = (category, None)

    for subtype, generator_func in GENERATOR_MAP.items():
        for i in range(1, 31):  # 30 задач на каждый подтип
            task = generator_func()

            # Получаем категорию и подкатегорию по карте
            category, subcategory = reverse_map.get(subtype, ("unknown", "unknown"))

            # Формируем id
            task_id = f"12_{subtype}_{i:03d}"

            # Собираем итоговую структуру
            tasks.append(
                {
                    "id": task_id,
                    "task_type": task_type,
                    "subtype": subtype,
                    "category": category,
                    "subcategory": subcategory,
                    "text": task["text"],
                    "answer": task["answer"],
                    "source_plot": {
                        "plot_id": task["plot_id"],
                        "params": task.get("params") or {},
                        "hidden_params": task.get("hidden_params") or {},
                        "constants": task.get("constants") or {},
                    },
                }
            )

    return tasks


def main():
    tasks = generate_tasks()

    # Создаём папку, если вдруг нет
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Сохраняем JSON красиво (UTF-8)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    print(f"[OK] Сгенерировано {len(tasks)} задач. Сохранено в {OUTPUT_PATH}")


if __name__ == "__main__":
    main()