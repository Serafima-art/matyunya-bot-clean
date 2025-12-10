"""
Лабораторный стенд для отладки РЕШАТЕЛЕЙ ТЕМ Задания 15.
Запускается локально, без Telegram.
"""

import json
import sys
import os
import logging
import random
from pathlib import Path

# --- ИМПОРТЫ ---
try:
    # Добавляем корень проекта в sys.path для стабильных импортов
    # __file__ -> .../_debug_solver.py -> task_15 -> solvers -> help_core -> matunya_bot_final
    project_root_for_import = Path(__file__).resolve().parents[4]
    sys.path.append(str(project_root_for_import))

    # ⭐️ ВАЖНО: Импортируем solve НАПРЯМУЮ из тематического солвера
    from matunya_bot_final.help_core.solvers.task_15.general_triangles_solver import solve
    #from matunya_bot_final.help_core.solvers.task_15.angles_solver import solve
    from matunya_bot_final.help_core.humanizers.template_humanizers.task_15_humanizer import humanize
except ImportError as e:
    print(f"🔴 Ошибка импорта: {e}. Проверьте правильность путей и структуру проекта.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def load_db_tasks() -> list:
    """Загружает все задачи из итоговой базы данных."""
    try:
        # Ищем корень проекта (папку matunya_bot_final)
        current_path = Path(__file__).resolve()
        project_root = current_path
        while project_root.name != 'matunya_bot_final':
            project_root = project_root.parent

        db_path = project_root / "data" / "tasks_15" / "tasks_15.json"

        if not db_path.exists():
            logger.error(f"❌ Файл БД не найден по пути: {db_path}")
            return []

        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        logger.error(f"❌ Ошибка чтения JSON: {e}")
        return []


def run_test(target_pattern: str, limit: int = 3):
    """
    Ищет задачи с заданным паттерном и выводит случайную выборку.
    """
    print(f"\n_> 🔍 ТЕСТИРОВАНИЕ ПАТТЕРНА: '{target_pattern}' (до {limit} случайных примеров)")
    print("-" * 70)

    all_tasks = load_db_tasks()
    if not all_tasks:
        return

    candidates = [t for t in all_tasks if t.get("pattern") == target_pattern]

    if not candidates:
        logger.warning(f"⚠️ Не найдено ни одной задачи с паттерном '{target_pattern}'.")
        return

    print(f"✅ Всего найдено задач с этим паттерном: {len(candidates)}")
    random.shuffle(candidates)

    for i, task in enumerate(candidates[:limit]):
        print(f"\n{'='*25} ПРИМЕР #{i+1} (ID: {task.get('id')}) {'='*25}")
        print(f"Условие: {task.get('text')}\n")

        # 1. SOLVER
        try:
            # Вызываем импортированную функцию solve напрямую
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
        print("--- РЕЗУЛЬТАТ РЕШЕНИЯ ---")
        print(final_text)
        print("="*70)


if __name__ == "__main__":
    # === СПИСОК ПАТТЕРНОВ ДЛЯ ТЕСТИРОВАНИЯ ===
    # Чтобы протестировать паттерн, просто раскомментируй нужную строку

    # --- ТЕМА 1: УГЛЫ ---
    # TEST_PATTERN = "triangle_external_angle"
    # TEST_PATTERN = "angle_bisector_find_half_angle"

    # --- ТЕМА 2: ПРОИЗВОЛЬНЫЕ ТРЕУГОЛЬНИКИ ---
    # TEST_PATTERN = "triangle_area_by_midpoints"
    TEST_PATTERN = "triangle_area_by_sin"
    # TEST_PATTERN = "triangle_area_by_dividing_point"
    # TEST_PATTERN = "triangle_area_by_parallel_line"
    # TEST_PATTERN = "cosine_law_find_cos"
    # TEST_PATTERN = "triangle_by_two_angles_and_side"

    # --- НАСТРОЙКИ ЗАПУСКА ---
    # Сколько случайных примеров показать
    TEST_LIMIT = 25

    # ----------------------------------------
    run_test(TEST_PATTERN, limit=TEST_LIMIT)
