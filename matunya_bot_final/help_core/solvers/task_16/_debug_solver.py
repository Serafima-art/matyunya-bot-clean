"""
Лабораторный стенд для отладки РЕШАТЕЛЕЙ ТЕМ Задания 16.
Запускается локально, без Telegram.
Поддерживает асинхронный запуск решателей.

UPD: Добавлена умная выборка (по N задач из КАЖДОГО нарратива).
"""

import json
import sys
import logging
import random
import argparse
import asyncio
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, List

# =============================================================
# sys.path — СНАЧАЛА (ОБЯЗАТЕЛЬНО)
# =============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================
# ИМПОРТЫ ПРОЕКТА
# =============================================================
# Импорт Решателя темы
#from matunya_bot_final.help_core.solvers.task_16.central_and_inscribed_angles_solver import solve
from matunya_bot_final.help_core.solvers.task_16.circle_elements_relations_solver import solve

# Импорт Хьюмонайзера (ЖЕСТКИЙ ИМПОРТ, ЧТОБЫ ВИДЕТЬ ОШИБКИ)
from matunya_bot_final.help_core.humanizers.template_humanizers.task_16_humanizer import humanize

# Если вдруг humanize не импортируется, скрипт упадет с Traceback,
# и мы увидим, где именно ошибка (в имени файла, в коде или в путях).


# =============================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ И АРГУМЕНТОВ
# =============================================================

def _parse_args(argv):
    parser = argparse.ArgumentParser(description="Debug solver for Task 16")
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
        log_path = Path.cwd() / "debug_solver_16_output.txt"

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
        db_path = PROJECT_ROOT / "matunya_bot_final" / "data" / "tasks_16" / "tasks_16.json"

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

async def run_test_async(target_pattern: str, limit_per_narrative: int = 3):
    log_print(f"\n_> 🔍 ТЕСТИРОВАНИЕ ПАТТЕРНА: '{target_pattern}'")
    log_print(f"   Лимит: до {limit_per_narrative} задач из КАЖДОГО нарратива")
    log_print("-" * 70)

    all_tasks = load_db_tasks()
    if not all_tasks:
        return

    # 1. Фильтруем по паттерну
    pattern_tasks = [t for t in all_tasks if t.get("pattern") == target_pattern]

    if not pattern_tasks:
        logger.warning(f"⚠️ Не найдено задач с паттерном '{target_pattern}'.")
        return

    # 2. Группируем по нарративам
    tasks_by_narrative = {}
    for task in pattern_tasks:
        narr = task.get("narrative", "unknown")
        if narr not in tasks_by_narrative:
            tasks_by_narrative[narr] = []
        tasks_by_narrative[narr].append(task)

    # 3. Набираем кандидатов (равномерно)
    final_candidates = []

    log_print("📊 Статистика выборки:")
    for narr, tasks in tasks_by_narrative.items():
        count_total = len(tasks)
        random.shuffle(tasks)
        selected = tasks[:limit_per_narrative]
        final_candidates.extend(selected)
        log_print(f"   🔹 Нарратив '{narr}': всего {count_total} -> выбрано {len(selected)}")

    log_print(f"✅ Итого к проверке: {len(final_candidates)} задач")
    log_print("-" * 70)

    # 4. Прогоняем тесты
    for i, task in enumerate(final_candidates, start=1):
        log_print(f"\n{'='*25} ПРИМЕР #{i} (ID: {task.get('id')}) {'='*25}")
        log_print(f"Нарратив: {task.get('narrative')}")
        log_print(f"Условие: {task.get('question_text')}\n")

        # SOLVER (Асинхронный вызов)
        solution_core = None
        try:
            solution_core = await solve(task)
        except Exception as e:
            logger.error(f"❌ CRASH SOLVER: {e}", exc_info=True)
            continue

        # HUMANIZER (Синхронный вызов)
        try:
            final_text = humanize(solution_core)
        except Exception as e:
            logger.error(f"❌ CRASH HUMANIZER: {e}", exc_info=True)
            continue

        log_print("--- РЕЗУЛЬТАТ (Текст решения) ---")
        log_print(final_text)
        log_print("=" * 70)


def run_test(target_pattern: str, limit: int):
    asyncio.run(run_test_async(target_pattern, limit))


# =============================================================
# MAIN
# =============================================================
if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    log_file = _setup_logging(args["to_file"], args["out_path"])

    def main():
        # =============================================================
        # НАСТРОЙКИ ЗАПУСКА
        # =============================================================

        # -------------------------------------------------------------
        # 🟩 ТЕМА 1: Центральные и вписанные углы (central_and_inscribed_angles)
        # -------------------------------------------------------------
        # TEST_PATTERN = "cyclic_quad_angles"
        # TEST_PATTERN = "central_inscribed"
        # TEST_PATTERN = "radius_chord_angles"
        # TEST_PATTERN = "arc_length_ratio"
        # TEST_PATTERN = "diameter_right_triangle"
        # TEST_PATTERN = "two_diameters_angles"

        # -------------------------------------------------------------
        # 🟨 ТЕМА 2. Касательная, хорда, секущая, радиус (circle_elements_relations)
        # -------------------------------------------------------------
        # TEST_PATTERN = "secant_similarity"
        # TEST_PATTERN = "tangent_trapezoid_properties"
        # TEST_PATTERN = "tangent_quad_sum"
        # TEST_PATTERN = "tangent_arc_angle"
        # TEST_PATTERN = "angle_tangency_center"
        # TEST_PATTERN = "sector_area"
        TEST_PATTERN = "power_point"


        # Сколько случайных задач брать ИЗ КАЖДОГО нарратива
        TEST_LIMIT_PER_NARRATIVE = 10

        run_test(TEST_PATTERN, limit=TEST_LIMIT_PER_NARRATIVE)

    if log_file:
        with open(log_file, "w", encoding="utf-8") as f, \
             redirect_stdout(f), redirect_stderr(f):
            log_print(f"📝 Лог будет сохранён в файл: {log_file}")
            main()
    else:
        main()
