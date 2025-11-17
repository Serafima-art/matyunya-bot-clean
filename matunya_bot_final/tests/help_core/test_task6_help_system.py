# matunya_bot_final/tests/help_core/test_task6_help_system.py

import json
from pathlib import Path

import pytest

from matunya_bot_final.help_core.solvers.task_6 import (
    common_fractions_solver,
    decimal_fractions_solver,
    mixed_fractions_solver,
    powers_solver,
)
from matunya_bot_final.help_core.humanizers.template_humanizers.task_6_humanizer import (
    humanize,
)


# ---------------------------------------------------------
#  Загрузка БД задания 6
# ---------------------------------------------------------

# PROJECT_ROOT = matunya_bot_final
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TASKS_6_PATH = PROJECT_ROOT / "data" / "tasks_6" / "tasks_6.json"


with TASKS_6_PATH.open("r", encoding="utf-8") as f:
    _TASKS_RAW = json.load(f)

# Оставляем только те, у кого есть variables.expression_tree
TASKS_6 = [
    t for t in _TASKS_RAW
    if isinstance(t, dict)
    and t.get("variables", {}).get("expression_tree") is not None
]


# ---------------------------------------------------------
#  Маппинг "подтип → решатель"
# ---------------------------------------------------------

SOLVER_BY_SUBTYPE = {
    "common_fractions": common_fractions_solver.solve,
    "decimal_fractions": decimal_fractions_solver.solve,
    "mixed_fractions": mixed_fractions_solver.solve,
    "powers": powers_solver.solve,
}


def _get_solver_for_task(task: dict):
    subtype = task.get("subtype")
    solver = SOLVER_BY_SUBTYPE.get(subtype)
    assert solver is not None, f"Не найден решатель для подтипа '{subtype}'"
    return solver


# ---------------------------------------------------------
#  Параметризация по всем задачам 6
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "task_data",
    TASKS_6,
    ids=lambda t: f"{t.get('id')}|{t.get('subtype')}|{t.get('pattern')}",
)
def test_task6_help_pipeline_for_all_tasks(task_data):
    """
    Прогоняет ПОЛНУЮ цепочку Помощи по всем задачам 6:
    JSON из БД → solver → solution_core → humanizer.

    Проверяем только:
    - что ничего не падает,
    - что структура solution_core валидная,
    - что humanize возвращает текст.
    """

    task_id = task_data.get("id")
    subtype = task_data.get("subtype")
    pattern = task_data.get("pattern")

    solver = _get_solver_for_task(task_data)

    # ---------- 1. Запуск решателя ----------
    try:
        solution_core = solver(task_data)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(
            f"Solver упал для задачи {task_id} "
            f"(subtype='{subtype}', pattern='{pattern}'): {type(exc).__name__}: {exc}"
        )

    # Базовые структурные проверки solution_core
    assert isinstance(solution_core, dict), (
        f"solver вернул не dict для задачи {task_id}"
    )

    # Должны быть либо calculation_steps, либо calculation_paths
    steps = solution_core.get("calculation_steps")
    paths = solution_core.get("calculation_paths")

    assert steps or paths, (
        f"В solution_core нет ни calculation_steps, ни calculation_paths "
        f"для задачи {task_id}"
    )

    # Финальный ответ обязателен
    final_answer = solution_core.get("final_answer")
    assert isinstance(final_answer, dict), (
        f"В solution_core отсутствует final_answer или это не dict "
        f"для задачи {task_id}"
    )
    assert "value_display" in final_answer, (
        f"В final_answer нет ключа 'value_display' для задачи {task_id}"
    )

    # ---------- 2. Запуск humanizer ----------
    try:
        html = humanize(solution_core)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(
            f"humanize упал для задачи {task_id} "
            f"(subtype='{subtype}', pattern='{pattern}'): {type(exc).__name__}: {exc}"
        )

    assert isinstance(html, str), (
        f"humanize вернул не строку для задачи {task_id}"
    )
    assert html.strip(), (
        f"humanize вернул пустую строку для задачи {task_id}"
    )
