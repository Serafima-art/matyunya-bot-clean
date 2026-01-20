"""
Лабораторный стенд для отладки ВАЛИДАТОРА Задания 16
ТОЧЕЧНЫЙ РЕЖИМ: проверяем ТОЛЬКО один паттерн (TARGET_PATTERN)

Скрипт эмулирует работу Генератора:
1. Читает сырой файл definitions.
2. Парсит комментарии вида "# narrative: ..." для определения контекста.
3. Подставляет фейковый ответ (-1), чтобы валидатор отработал логику парсинга.
4. Выводит итоговый JSON (с картинками и переменными) в консоль или файл.

Запускается локально, без Telegram.

Опции:
  --to-file   перенаправляет stdout+stderr в файл debug_validator_output.txt
"""

import json
import sys
import logging
import argparse
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

# ---------------------------------------------------------------------
# НАСТРОЙКИ
# ---------------------------------------------------------------------

TARGET_PATTERN = "arc_length_ratio"
DEFINITIONS_FILE = "central_and_inscribed_angles.txt"
OUTPUT_FILENAME = "debug_validator_output.txt"

# ---------------------------------------------------------------------
# НАСТРОЙКА ПУТЕЙ (УЛУЧШЕННАЯ)
# Добавляем в path и корень репозитория, и папку с кодом
# ---------------------------------------------------------------------

# Файл лежит в: matunya_bot_final/non_generators/task_16/validators/_debug_validator.py
current_file = Path(__file__).resolve()
project_root = current_file.parents[4]  # Папка matunya (где лежит .venv)
source_root = current_file.parents[3]   # Папка matunya_bot_final

# Добавляем оба пути, чтобы работали любые импорты
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(source_root) not in sys.path:
    sys.path.insert(0, str(source_root))

# ---------------------------------------------------------------------
# ИМПОРТ ВАЛИДАТОРА
# ---------------------------------------------------------------------

try:
    # Пробуем импорт через полный путь (рекомендуемый)
    from matunya_bot_final.non_generators.task_16.validators.central_and_inscribed_angles_validator import (
        CentralAndInscribedAnglesValidator,
    )
except ImportError:
    try:
        # Пробуем импорт напрямую (если запущен изнутри папки)
        from non_generators.task_16.validators.central_and_inscribed_angles_validator import (
            CentralAndInscribedAnglesValidator,
        )
    except ImportError as e:
        print(f"🔴 Ошибка импорта валидатора: {e}")
        print(f"Путь поиска (sys.path): {sys.path}")
        sys.exit(1)

# ---------------------------------------------------------------------
# ЛОГГИНГ
# ---------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# ЗАГРУЗКА И ПАРСИНГ СЫРЬЯ
# ---------------------------------------------------------------------

def load_parsed_tasks(filename: str) -> List[Dict[str, Any]]:
    """
    Загружает задачи из definitions/*.txt, учитывая контекст нарратива.
    """
    definitions_dir = (
        source_root
        / "non_generators"
        / "task_16"
        / "definitions"
    )
    file_path = definitions_dir / filename

    if not file_path.exists():
        logger.error(f"❌ Файл с сырьём не найден: {file_path}")
        return []

    parsed_tasks = []
    current_narrative = "unknown_narrative"

    # Регулярка для поиска нарратива в комментариях
    narrative_regex = re.compile(r"^#\s*(?:narrative|нарратив|Нарратив):\s*([a-zA-Z_0-9]+)")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Проверяем, не смена ли это нарратива
            narrative_match = narrative_regex.match(line)
            if narrative_match:
                current_narrative = narrative_match.group(1)
                continue

            # Пропускаем остальные комментарии
            if line.startswith("#"):
                continue

            # Если строка задачи
            if "|" in line:
                pattern_from_line, text = line.split("|", 1)

                # Фильтруем только целевой паттерн
                if pattern_from_line.strip() == TARGET_PATTERN:
                    task_obj = {
                        "pattern": pattern_from_line.strip(),
                        "narrative": current_narrative,
                        "question_text": text.strip(),
                        "answer": -1 # Фейковый ответ
                    }
                    parsed_tasks.append(task_obj)

        return parsed_tasks

    except Exception as e:
        logger.error(f"❌ Ошибка чтения файла {filename}: {e}")
        return []


# ---------------------------------------------------------------------
# ОСНОВНОЙ ТЕСТ
# ---------------------------------------------------------------------

def run_test() -> None:
    print("\n" + "=" * 80)
    print("🔬 ДИАГНОСТИКА ВАЛИДАТОРА (Задание 16)")
    print(f"🎯 ПАТТЕРН: {TARGET_PATTERN}")
    print(f"📂 ФАЙЛ СЫРЬЯ: {DEFINITIONS_FILE}")
    print("=" * 80)

    tasks = load_parsed_tasks(DEFINITIONS_FILE)

    if not tasks:
        logger.warning(f"⚠️ Задач не найдено или файл пуст.")
        return

    print(f"✅ Загружено задач: {len(tasks)}")

    validator = CentralAndInscribedAnglesValidator()

    # --- Прогоняем ВСЕ задачи этого паттерна ---
    for i, raw_data in enumerate(tasks, start=1):
        print("\n" + "-" * 80)
        print(f"🧪 Пример #{i} [Narrative: {raw_data['narrative']}]")
        print(f"📄 Текст: {raw_data['question_text']}")

        try:
            # Валидатор возвращает Tuple[bool, List[str]] и меняет raw_data IN-PLACE
            is_valid, errors = validator.validate(raw_data)

            if is_valid:
                print("✅ СТАТУС: ВАЛИДНО (Ответ совпал)")
            else:
                math_errors = [e for e in errors if "Неверный ответ" in e or "Математическая ошибка" in e]
                other_errors = [e for e in errors if e not in math_errors]

                if not other_errors and math_errors:
                     print("⚠️ СТАТУС: ЛОГИКА ОК (Ответ ожидаемо не совпал с заглушкой -1)")
                else:
                    print("❌ СТАТУС: ОШИБКИ ВАЛИДАЦИИ")
                    for err in errors:
                        print(f"   🔴 {err}")

            print("📦 Итоговый JSON (сформированный валидатором):")
            print(json.dumps(raw_data, indent=2, ensure_ascii=False))

        except Exception as e:
            print("❌ CRASH VALIDATOR")
            logger.error(str(e), exc_info=True)

    print("\n" + "=" * 80)
    print("🏁 КОНЕЦ ДИАГНОСТИКИ")
    print("=" * 80)


# ---------------------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Debug validator for task_16 pattern")
    parser.add_argument(
        "--to-file",
        action="store_true",
        help=f"Redirect stdout+stderr to {OUTPUT_FILENAME}",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    output_file: Optional[object] = None

    try:
        if args.to_file:
            output_path = Path(OUTPUT_FILENAME)
            output_file = output_path.open("w", encoding="utf-8")

            # Перенаправляем ОБА потока: stdout и stderr
            sys.stdout = output_file
            sys.stderr = output_file

            print("🧪 DEBUG VALIDATOR OUTPUT (TASK 16)")
            print("=" * 80)
            print(f"📌 Redirected stdout+stderr to: {output_path.resolve()}")
            print("=" * 80)

        run_test()

        print("\n✅ Диагностика завершена.")

    finally:
        if output_file:
            try:
                print("\n🏁 LOG FILE CLOSED")
                print("=" * 80)
            except Exception:
                pass

            output_file.close()
            sys.stdout = original_stdout
            sys.stderr = original_stderr
