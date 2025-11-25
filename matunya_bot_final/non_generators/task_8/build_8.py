import json
import importlib
import random
import string
from pathlib import Path


def _generate_short_id(length=6):
    """Генерирует короткий случайный ID."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))


def _short_expr_from_raw(raw: str) -> str:
    """Красивый вывод выражения из строки raw."""
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) >= 3:
        return f"{parts[1]} | {parts[2]}"
    if len(parts) == 2:
        return parts[1]
    return raw


def main():
    print("--- Сборщик задания 8 запущен ---")

    current_dir = Path(__file__).parent
    definitions_dir = current_dir / "definitions"
    output_dir = current_dir.parent.parent / "data" / "task_8"
    output_file = output_dir / "tasks_8.json"

    all_valid_tasks = []

    definition_files = sorted(list(definitions_dir.glob("*.txt")))
    if not definition_files:
        print("[!] ВНИМАНИЕ: В 'definitions' нет .txt файлов.")
        return

    print(f"[*] Найдено {len(definition_files)} файлов.")

    for def_path in definition_files:
        subtype_from_filename = def_path.stem
        print(f"\n--- Обработка темы: {subtype_from_filename} ---")

        # Имя валидатора = <subtype>_validator.py
        validator_module_name = f".validators.{subtype_from_filename}_validator"
        validator_func_name = f"validate"

        try:
            validator_module = importlib.import_module(
                validator_module_name,
                package=__package__
            )
            validator_func = getattr(validator_module, validator_func_name)
        except (ImportError, AttributeError):
            print(f"[!] ОШИБКА: Валидатор для '{subtype_from_filename}' не найден. Пропуск.")
            continue

        tasks_in_file = 0

        with open(def_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                try:
                    rich_data = validator_func(line)
                except Exception as e:
                    expr = _short_expr_from_raw(line)
                    print(f"FAIL [{subtype_from_filename}]: {expr} — исключение валидатора: {e}")
                    continue

                if not rich_data:
                    expr = _short_expr_from_raw(line)
                    print(f"FAIL [{subtype_from_filename}]: {expr} — валидатор вернул None")
                    continue

                # Собираем объект задания
                final_task_object = {
                    "id": f"8_{rich_data['solution_pattern']}_{_generate_short_id()}",
                    "task_number": 8,
                    "subtype": subtype_from_filename,
                    "pattern": rich_data["solution_pattern"],

                    # структура строго такая, как возвращает валидатор
                    "expression_tree": rich_data["expression_tree"],
                    "variables": rich_data["variables"],
                    "answer": rich_data["answer"],

                    # meta — минимальная, как в заданиях 20 и 6
                    "meta": {
                        "pattern_id": rich_data["solution_pattern"]
                    }
                }

                all_valid_tasks.append(final_task_object)
                tasks_in_file += 1

                expr = _short_expr_from_raw(line)
                print(f"OK [{subtype_from_filename}]: {expr} → {rich_data['answer']}")

        print(f"[+] Принято в файле: {tasks_in_file}")

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_valid_tasks, f, indent=4, ensure_ascii=False)

    print(f"\n[*] Финальный файл сохранён: {output_file}")
    print(f"[✓] Всего собрано: {len(all_valid_tasks)}")
    print("--- Сборка задания 8 завершена ---")


if __name__ == "__main__":
    main()
