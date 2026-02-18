# matunya_bot_final/help_core/solvers/task_1_5/paper/_debug_solver.py

import json
from pathlib import Path
from typing import Dict, Any

from matunya_bot_final.help_core.solvers.task_1_5.paper.paper_solver import solve_paper
from matunya_bot_final.help_core.humanizers.template_humanizers.task_1_5.paper_humanizer import humanize


# =============================================================================
# НАСТРОЙКИ
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[4]
# parents[4] = matunya_bot_final

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "tasks_1_5"
    / "paper"
    / "tasks_1_5_paper.json"
)

OUTPUT_FILE = Path(__file__).parent / "debug_solver_1_5_paper_output.txt"


# =============================================================================
# ЗАПУСК
# =============================================================================

def run_debug() -> None:

    print(f"Лог будет сохранён в файл: {OUTPUT_FILE}\n")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        variants = json.load(f)

    lines = []

    example_counter = 1

    for variant in variants:

        variant_id = variant.get("id")
        questions = variant.get("questions", [])

        for question in questions:

            q_number = question.get("q_number")
            narrative = question.get("narrative")

            lines.append("=" * 70)
            lines.append(f"ПРИМЕР #{example_counter} (Variant: {variant_id}, Q: {q_number})")
            lines.append(f"Нарратив: {narrative}\n")

            try:
                solution_core = solve_paper({
                    "task": question,
                    "variant": variant
                })

                humanized_text = humanize(solution_core)

            except Exception as e:
                humanized_text = f"❌ ОШИБКА: {e}"

            lines.append("--- РЕЗУЛЬТАТ (Текст решения) ---\n")
            lines.append(humanized_text)
            lines.append("\n")

            example_counter += 1

    print("Длина lines:", len(lines))
    print("OUTPUT_FILE:", OUTPUT_FILE)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Файл записан.")

    print("Готово.")

if __name__ == "__main__":
    run_debug()
