"""Utility: show summary of tasks grouped by subtype and internal patterns."""

from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import defaultdict


def main(task_number: int | None = None) -> None:
    base_path = Path("matunya_bot_final/data/tasks_20/tasks_20.json")
    if not base_path.exists():
        print(f"❌ File not found: {base_path}")
        return

    with open(base_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    if task_number:
        tasks = [t for t in tasks if int(t.get("task_number", 0)) == int(task_number)]

    if not tasks:
        print(f"⚠️ No tasks found for №{task_number}.")
        return

    # --- Группируем по subtype и внутренним паттернам ---
    grouped: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for task in tasks:
        subtype = task.get("subtype", "unknown")
        variables = task.get("variables", {})
        pattern = variables.get("solution_pattern", "—")
        grouped[subtype][pattern] += 1

    # --- Печатаем сводку ---
    print(f"\n📊 Задания №{task_number or 'ALL'}")
    print(f"Всего задач: {len(tasks)}")

    for subtype, patterns in grouped.items():
        subtype_total = sum(patterns.values())
        print(f"— {subtype}: {subtype_total}")

        # Выводим внутренние паттерны с отступом
        for pattern, count in patterns.items():
            print(f"     • {pattern}: {count}")

    print()  # пустая строка для красоты


if __name__ == "__main__":
    task_number = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(task_number)
