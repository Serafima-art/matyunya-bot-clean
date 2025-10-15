import json
from pathlib import Path
from typing import Dict, Any, List

# 👇 ОБНОВЛЕННЫЙ БЛОК ИМПОРТОВ 👇
# Теперь мы импортируем не отдельные генераторы, а саму "карту" и функцию-создатель
from matunya_bot_final.py_generators.task_8_generator import GENERATOR_MAP

# --- НАСТРОЙКИ ---
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "tasks_8.json"
TASKS_PER_SUBTYPE = 5 # Давай генерировать по 5 заданий каждого типа для разнообразия

def create_task_object(task_id: str, subtype: str, text: str, answer: str) -> Dict[str, Any]:
    """Собирает финальный JSON-объект для одного задания."""
    return {
        "id": task_id,
        "task_type": "8",
        "subtype": subtype,
        "text": text,
        "answer": str(answer)
    }

# ================================================================
# ГЛАВНАЯ ФУНКЦИЯ (УЛУЧШЕННАЯ ВЕРСИЯ)
# ================================================================
def generate_all_tasks():
    """
    Главная функция, которая запускает все 17 генераторов из карты
    и сохраняет результат.
    """
    all_tasks: List[Dict[str, Any]] = []
    subtype_counters: Dict[str, int] = {}

    print(f"▶️  Начинаю генерацию заданий №8 для {len(GENERATOR_MAP)} подтипов...")

    # --- УМНЫЙ ЦИКЛ, КОТОРЫЙ ПРОХОДИТ ПО ВСЕМ ГЕНЕРАТОРАМ ---
    for subtype_key, generator_func in GENERATOR_MAP.items():
        print(f"  -> Генерирую задания для подтипа: {subtype_key}...")
        for i in range(TASKS_PER_SUBTYPE):
            # Вызываем генератор (он возвращает кортеж)
            # ВАЖНО: subtype в кортеже может быть псевдонимом, поэтому используем subtype_key из карты
            _, text, answer = generator_func()
            
            # Считаем, сколько заданий этого типа мы уже создали
            subtype_counters[subtype_key] = subtype_counters.get(subtype_key, 0) + 1
            counter = subtype_counters[subtype_key]
            
            # Создаем уникальный ID
            task_id = f"8_{subtype_key}_{counter:03d}"
            
            # Собираем и добавляем объект задания в общий список
            all_tasks.append(create_task_object(task_id, subtype_key, text, answer))

    # --- СОХРАНЕНИЕ В ФАЙЛ ---
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True) # Создаем папку data, если ее нет
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_tasks, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Успешно сгенерировано и сохранено {len(all_tasks)} заданий в файл:")
        print(f"   -> {OUTPUT_FILE}")
    except Exception as e:
        print(f"\n❌ Ошибка при сохранении файла: {e}")

if __name__ == "__main__":
    generate_all_tasks()