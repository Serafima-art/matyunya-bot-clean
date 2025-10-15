# verify_answers.py (ВРЕМЕННАЯ ВЕРСИЯ ДЛЯ АУДИТА tasks_7.json)

import json
from pathlib import Path

TASKS_FILE_PATH = Path(__file__).parent / "data" / "tasks_7.json"

def audit_tasks_7():
    """
    Просто читает tasks_7.json, проверяет его структуру и выводит ID и подтипы.
    """
    print(f"▶️  Начинаю аудит файла: {TASKS_FILE_PATH}")
    
    try:
        with open(TASKS_FILE_PATH, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print(f"❌ ОШИБКА: Файл не найден.")
        return
    except json.JSONDecodeError as e:
        print(f"❌ ОШИБКА JSON: {e}")
        return

    if not isinstance(tasks, list):
        print("❌ ОШИБКА: Файл должен содержать список [...] заданий.")
        return
        
    print(f"✅ Файл успешно прочитан. Найдено заданий: {len(tasks)}")
    print("-" * 40)
    
    all_subtypes = set()
    for task in tasks:
        task_id = task.get('id', 'N/A')
        subtype = task.get('subtype', '--- НЕ НАЙДЕН ---')
        print(f"  - ID: {task_id:<5} | subtype: {subtype}")
        all_subtypes.add(subtype)
        
    print("-" * 40)
    print(f"📊 Аудит завершен. Найдено уникальных подтипов: {len(all_subtypes)}")
    print("Список найденных подтипов:")
    for s in sorted(list(all_subtypes)):
        print(f"  - {s}")


if __name__ == "__main__":
    audit_tasks_7()