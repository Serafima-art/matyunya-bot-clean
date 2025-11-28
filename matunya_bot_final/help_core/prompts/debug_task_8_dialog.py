"""
Лабораторный стенд для проверки Промпта (Контекста) GPT для Задания 8.
Позволяет увидеть, какую инструкцию получит нейросеть, не тратя токены API.
"""

import json
import sys
import logging
import random
from pathlib import Path

# --- НАСТРОЙКА ПУТЕЙ ---
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

# --- ИМПОРТЫ ---
try:
    from matunya_bot_final.help_core.solvers.task_8.powers_and_roots_solver import solve as solve_powers
    from matunya_bot_final.help_core.solvers.task_8.integer_expressions_solver import solve as solve_integers
    from matunya_bot_final.help_core.prompts.task_8_dialog_prompts import get_task_8_dialog_prompt
except ImportError as e:
    print(f"🔴 Ошибка импорта: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def load_db_tasks() -> list:
    db_path = project_root / "matunya_bot_final" / "data" / "tasks_8" / "tasks_8.json"
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка чтения JSON: {e}")
        return []


def get_solver_for_task(task: dict):
    """Выбирает правильный солвер в зависимости от подтипа."""
    subtype = task.get("subtype")
    if subtype == "powers_and_roots":
        return solve_powers
    elif subtype == "integer_expressions":
        return solve_integers
    return None


def run_prompt_test(target_pattern: str = None):
    print(f"\n🤖 --- ТЕСТ ГЕНЕРАЦИИ ПРОМПТА GPT (Task 8) ---\n")

    all_tasks = load_db_tasks()

    # Фильтрация
    if target_pattern:
        candidates = [t for t in all_tasks if t.get("pattern") == target_pattern]
        print(f"🎯 Фильтр по паттерну: '{target_pattern}'")
    else:
        candidates = all_tasks
        print(f"🎲 Случайный выбор из всех задач")

    if not candidates:
        logger.warning("Задачи не найдены.")
        return

    task = random.choice(candidates)
    print(f"📝 Задача ID: {task.get('id')} | Subtype: {task.get('subtype')}")

    # 1. РЕШЕНИЕ (SOLVER)
    solver_func = get_solver_for_task(task)
    if not solver_func:
        logger.error("Не найден солвер для этого типа!")
        return

    try:
        solution_core = solver_func(task)
        print("✅ Решение сгенерировано.")
    except Exception as e:
        logger.error(f"Ошибка солвера: {e}", exc_info=True)
        return

    # 2. ИМИТАЦИЯ ИСТОРИИ ДИАЛОГА
    # Представим, что бот уже выдал решение, а ученик задает вопрос
    fake_history = [
        {"role": "user", "content": "Помоги решить"},
        {"role": "assistant", "content": "[Бот выдал решение...]"},
        {"role": "user", "content": "Я не понял, почему в шаге 2 мы делим степень на 2? Откуда это правило?"}
    ]

    # 3. ГЕНЕРАЦИЯ ПРОМПТА
    try:
        system_prompt = get_task_8_dialog_prompt(
            task_data=task,
            solution_core=solution_core,
            dialog_history=fake_history,
            student_name="Алекс",
            gender="male"
        )
    except Exception as e:
        logger.error(f"Ошибка генерации промпта: {e}", exc_info=True)
        return

    # 4. ВЫВОД
    print("\n" + "="*30 + " SYSTEM PROMPT " + "="*30)
    print(system_prompt)
    print("="*75)
    print("\n👀 Проверь:\n1. Есть ли условие задачи?\n2. Есть ли эталонное решение (шаги)?\n3. Нормально ли выглядят формулы (без HTML мусора)?")


if __name__ == "__main__":
    # Выбери паттерн для теста или оставь None для случайного

    # PATTERN = "radical_product"
    # PATTERN = "alg_power_fraction"
    PATTERN = "numeric_power_fraction" # Проверим наших "шпионов"

    run_prompt_test(PATTERN)
