"""
Лабораторный стенд для отладки РЕШАТЕЛЕЙ ТЕМ Задания 15.
Запускается локально, без Telegram.
Поддерживает вывод в файл (stdout + stderr), как у валидаторов.
"""

import json
import sys
import logging
import random
import argparse
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

# =============================================================
# sys.path — СНАЧАЛА (ОБЯЗАТЕЛЬНО)
# =============================================================
# _debug_solver.py -> task_15 -> solvers -> help_core -> matunya_bot_final -> PROJECT ROOT
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================
# ИМПОРТЫ ПРОЕКТА (ПОСЛЕ sys.path)
# =============================================================
# ⭐️ ВАЖНО: импортируем solve НАПРЯМУЮ из нужного солвера темы
#from matunya_bot_final.help_core.solvers.task_15.isosceles_triangles_solver import solve
from matunya_bot_final.help_core.solvers.task_15.right_triangles_solver import solve
from matunya_bot_final.help_core.humanizers.template_humanizers.task_15_humanizer import humanize


# =============================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ И АРГУМЕНТОВ
# =============================================================

def _parse_args(argv):
    parser = argparse.ArgumentParser(description="Debug solver for Task 15")
    parser.add_argument(
        "--to-file",
        action="store_true",
        help="Redirect stdout/stderr to file"
    )
    parser.add_argument(
        "--out-path",
        type=str,
        default=None,
        help="Path to output log file"
    )
    return vars(parser.parse_args(argv))


def _setup_logging(to_file: bool, out_path: str | None):
    if not to_file:
        return None

    if out_path:
        log_path = Path(out_path)
    else:
        log_path = Path.cwd() / "debug_solver_output.txt"

    log_path.parent.mkdir(parents=True, exist_ok=True)
    return log_path


def log_print(*args, **kwargs):
    print(*args, **kwargs)


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# =============================================================
# ЗАГРУЗКА БАЗЫ ЗАДАЧ
# =============================================================

def load_db_tasks() -> list:
    try:
        current_path = Path(__file__).resolve()
        project_root = current_path
        while project_root.name != "matunya_bot_final":
            project_root = project_root.parent

        db_path = project_root / "data" / "tasks_15" / "tasks_15.json"

        if not db_path.exists():
            logger.error(f"❌ Файл БД не найден: {db_path}")
            return []

        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        logger.error(f"❌ Ошибка чтения JSON: {e}")
        return []


# =============================================================
# ЗАПУСК ТЕСТА
# =============================================================

def run_test(target_pattern: str, limit: int = 3):
    log_print(f"\n_> 🔍 ТЕСТИРОВАНИЕ ПАТТЕРНА: '{target_pattern}' (до {limit} примеров)")
    log_print("-" * 70)

    all_tasks = load_db_tasks()
    if not all_tasks:
        return

    candidates = [t for t in all_tasks if t.get("pattern") == target_pattern]

    if not candidates:
        logger.warning(f"⚠️ Не найдено задач с паттерном '{target_pattern}'.")
        return

    log_print(f"✅ Найдено задач: {len(candidates)}")
    random.shuffle(candidates)

    for i, task in enumerate(candidates[:limit]):
        log_print(f"\n{'='*25} ПРИМЕР #{i+1} (ID: {task.get('id')}) {'='*25}")
        log_print(f"Условие: {task.get('text')}\n")

        # SOLVER
        try:
            solution_core = solve(task)
        except Exception as e:
            logger.error(f"❌ CRASH SOLVER: {e}", exc_info=True)
            continue

        # HUMANIZER
        try:
            final_text = humanize(solution_core)
        except Exception as e:
            logger.error(f"❌ CRASH HUMANIZER: {e}", exc_info=True)
            continue

        log_print("--- РЕЗУЛЬТАТ РЕШЕНИЯ ---")
        log_print(final_text)
        log_print("=" * 70)


# =============================================================
# MAIN
# =============================================================
if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    log_file = _setup_logging(args["to_file"], args["out_path"])

    def main():
        # =============================================================
        # === СПИСОК ПАТТЕРНОВ ДЛЯ ТЕСТИРОВАНИЯ ===
        # Просто раскомментируй нужный
        # =============================================================

        # -------------------------------------------------------------
        # ТЕМА 1: УГЛЫ
        # -------------------------------------------------------------
        # TEST_PATTERN = "triangle_external_angle"
        # TEST_PATTERN = "angle_bisector_find_half_angle"

        # -------------------------------------------------------------
        # ТЕМА 2: ТРЕУГОЛЬНИКИ ОБЩЕГО ВИДА
        # -------------------------------------------------------------
        # TEST_PATTERN = "triangle_area_by_midpoints"
        # TEST_PATTERN = "triangle_area_by_sin"
        # TEST_PATTERN = "triangle_area_by_dividing_point"
        # TEST_PATTERN = "triangle_area_by_parallel_line"
        # TEST_PATTERN = "cosine_law_find_cos"
        # TEST_PATTERN = "triangle_by_two_angles_and_side"
        # TEST_PATTERN = "trig_identity_find_trig_func"
        # TEST_PATTERN = "triangle_medians_intersection"

        # -------------------------------------------------------------
        # ТЕМА 3: РАВНОБЕДРЕННЫЕ И РАВНОСТОРОННИЕ ТРЕУГОЛЬНИКИ
        # -------------------------------------------------------------
        # TEST_PATTERN = "isosceles_triangle_angles"
        # TEST_PATTERN = "equilateral_height_to_side"
        # TEST_PATTERN = "equilateral_side_to_element"

        # -------------------------------------------------------------
        # ТЕМА 4: ПРЯМОУГОЛЬНЫЕ ТРЕУГОЛЬНИКИ
        # -------------------------------------------------------------
        # TEST_PATTERN = "right_triangle_angles_sum"
        #TEST_PATTERN = "pythagoras_find_leg"
        # TEST_PATTERN = "pythagoras_find_hypotenuse"
        TEST_PATTERN = "find_cos_sin_tg_from_sides"
        # TEST_PATTERN = "find_side_from_trig_ratio"
        # TEST_PATTERN = "right_triangle_median_to_hypotenuse"

        # -------------------------------------------------------------
        # НАСТРОЙКИ ЗАПУСКА
        # -------------------------------------------------------------

        TEST_LIMIT = 35

        run_test(TEST_PATTERN, limit=TEST_LIMIT)

    if log_file:
        with open(log_file, "w", encoding="utf-8") as f, \
             redirect_stdout(f), redirect_stderr(f):
            log_print(f"📝 Лог будет сохранён в файл: {log_file}")
            main()
    else:
        main()
