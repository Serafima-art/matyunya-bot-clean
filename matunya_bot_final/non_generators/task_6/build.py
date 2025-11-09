import json
import importlib
import random
import string
from pathlib import Path

def _generate_short_id(length=6):
    """Генерирует короткий случайный ID."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def main():
    """Финальная версия сборщика для Задания 6."""
    print("--- Запуск Фабрики v2.2 (Финальная): Сборка Задания 6 ---")

    current_dir = Path(__file__).parent
    definitions_dir = current_dir / "definitions"
    output_dir = current_dir.parent.parent / "data" / "tasks_6"
    output_file = output_dir / "tasks_6.json"

    all_valid_tasks = []

    definition_files = sorted(list(definitions_dir.glob("*.txt")))

    if not definition_files:
        print("[!] ВНИМАНИЕ: В 'definitions' не найдено .txt файлов.")
        return

    print(f"[*] Найдено {len(definition_files)} файлов для обработки.")

    for def_path in definition_files:
        subtype_from_filename = def_path.stem
        print(f"\n--- Обработка: {subtype_from_filename} ---")

        # Поддержка всех стандартных подтипов + powers
        if subtype_from_filename == "powers":
            validator_module_name = ".validators.powers_validator"
            validator_func_name = "validate_powers"
        else:
            validator_module_name = f".validators.{subtype_from_filename}_validator"
            validator_func_name = f"validate_{subtype_from_filename.replace('_fractions', '_fraction')}"

        try:
            validator_module = importlib.import_module(validator_module_name, package=__package__)
            validator_func = getattr(validator_module, validator_func_name)
        except (ImportError, AttributeError):
            print(f"[!] ОШИБКА: Не найден валидатор для '{subtype_from_filename}'. Пропускаем.")
            continue

        tasks_in_file = 0
        with open(def_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue

                rich_data = validator_func(line)
                if rich_data:
                    pattern = rich_data['pattern']
                    difficulty = 'hard' if pattern in ['complex_fraction', 'parentheses_operations'] else 'medium'

                    final_task_object = {
                        "id": f"6_{pattern}_{_generate_short_id()}",
                        "task_number": 6,
                        "subtype": subtype_from_filename,
                        "pattern": pattern,
                        "question_text": rich_data['question_text'],
                        "answer": rich_data['answer'],
                        "answer_type": rich_data['answer_type'],
                        "variables": {
                            "expression_tree": rich_data['expression_tree']
                        },
                        "meta": {
                            "difficulty": difficulty,
                            "pattern_id": pattern
                        }
                    }
                    all_valid_tasks.append(final_task_object)
                    tasks_in_file += 1

        print(f"[+] Успешно принято: {tasks_in_file} заданий.")

    # Финальная структура JSON без лишних полей
    # Мы записываем в файл напрямую список задач, а не словарь.
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_valid_tasks, f, indent=4, ensure_ascii=False)

    print(f"\n[*] Итоговый файл сохранен: {output_file}")
    print(f"[✓] Всего собрано: {len(all_valid_tasks)} заданий.")
    print("--- Сборка Задания 6 успешно завершена! ---")

if __name__ == '__main__':
    main()
