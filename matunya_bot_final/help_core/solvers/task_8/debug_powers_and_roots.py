"""
Лабораторный стенд для отладки решателя powers_and_roots.
Запускается локально, без Telegram.

Выводит СЛУЧАЙНЫЕ примеры для выбранного паттерна, чтобы проверить разные формы.
"""

import json
import sys
import logging
import random  # <--- Добавили
from pathlib import Path

# --- НАСТРОЙКА ПУТЕЙ ---
project_root = Path(__file__).resolve().parents[4]
sys.path.append(str(project_root))

# --- ИМПОРТЫ ---
try:
    from matunya_bot_final.help_core.solvers.task_8.powers_and_roots_solver import solve
    from matunya_bot_final.help_core.humanizers.template_humanizers.task_8_humanizer import humanize
except ImportError as e:
    print(f"🔴 Ошибка импорта: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def load_db_tasks() -> list:
    db_path = project_root / "matunya_bot_final" / "data" / "tasks_8" / "tasks_8.json"
    if not db_path.exists():
        logger.error(f"Файл БД не найден: {db_path}")
        return []
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка чтения JSON: {e}")
        return []


def run_test(target_pattern: str, limit: int = 10):
    """
    Ищет задачи с заданным паттерном и выводит случайную выборку.
    """
    print(f"\n🔍 --- ТЕСТ ПАТТЕРНА: {target_pattern} (Случайные {limit} шт.) ---\n")

    all_tasks = load_db_tasks()
    candidates = [t for t in all_tasks if t.get("subtype") == "powers_and_roots" and t.get("pattern") == target_pattern]

    if not candidates:
        logger.warning(f"⚠️ Не найдено ни одной задачи с паттерном '{target_pattern}'.")
        return

    print(f"✅ Всего найдено задач: {len(candidates)}")

    # ПЕРЕМЕШИВАЕМ, чтобы увидеть разные формы
    random.shuffle(candidates)

    for i, task in enumerate(candidates[:limit]):
        print(f"\n{'='*20} ПРИМЕР #{i+1} (ID: {task.get('id')}) {'='*20}")

        # 1. SOLVER
        try:
            solution_core = solve(task)
        except Exception as e:
            logger.error(f"❌ CRASH SOLVER: {e}", exc_info=True)
            continue

        # 2. HUMANIZER
        try:
            final_text = humanize(solution_core)
        except Exception as e:
            logger.error(f"❌ CRASH HUMANIZER: {e}", exc_info=True)
            continue

        # 3. OUTPUT
        print(final_text)
        print("="*60)


if __name__ == "__main__":
    # === ЗДЕСЬ МЕНЯЕМ ПАТТЕРН ДЛЯ ТЕСТА ===

    # 1. squared_radical
    # 2. radical_multiplication
    # 3. radical_product
    # 4. radical_product_with_powers
    # 5. radical_fraction
    # 6. conjugate_radicals
    # 7. numeric_power_fraction
    # 8. count_integers_between_radicals

    TEST_PATTERN = "numeric_power_fraction"

    run_test(TEST_PATTERN, limit=10)
