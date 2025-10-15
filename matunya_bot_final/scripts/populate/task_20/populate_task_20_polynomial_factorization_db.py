"""Populate storage for task 20 polynomial_factorization subtype."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Set

from matunya_bot_final.task_generators.task_20.generators import generate_task_20_by_subtype
from matunya_bot_final.task_generators.task_20.validators import (
    validate_task_20_polynomial_factorization,
)

TARGET_PATH = Path("matunya_bot_final/data/tasks_20/tasks_20.json")
TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)


def _cleanup_outputs() -> None:
    """Remove stale bytecode files to avoid outdated imports."""
    cleanup_roots = [
        Path("matunya_bot_final/task_generators/task_20"),
        Path("matunya_bot_final/scripts/populate"),
    ]
    for root in cleanup_roots:
        if not root.exists():
            continue
        for pyc_file in root.rglob("*.pyc"):
            try:
                pyc_file.unlink()
            except OSError:
                continue


def _serialize_tasks(tasks: List[Dict[str, Any]]) -> None:
    TARGET_PATH.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_existing_tasks() -> List[Dict[str, Any]]:
    """Load current dataset; return empty list if file not found or invalid."""
    if not TARGET_PATH.exists():
        return []
    try:
        content = json.loads(TARGET_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        print(f"[WARN] Unable to parse existing dataset {TARGET_PATH}: {exc}")
        return []
    if not isinstance(content, list):
        print(f"[WARN] Existing dataset {TARGET_PATH} is not a list, ignoring its content.")
        return []
    return content


def main() -> None:
    """Generate fresh set of validated tasks and merge with existing storage."""
    _cleanup_outputs()
    existing_tasks = _load_existing_tasks()

    preserved_tasks: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()
    seen_questions: Set[str] = set()

    for task in existing_tasks:
        if not isinstance(task, dict):
            continue
        task_id = task.get("id")
        if isinstance(task_id, str):
            seen_ids.add(task_id)

        if task.get("subtype") == "polynomial_factorization":
            # Skip obsolete entries for this subtype; they will be regenerated below.
            continue

        question_text = task.get("question_text")
        if isinstance(question_text, str):
            seen_questions.add(question_text)
        preserved_tasks.append(task)

    target_amount = 20
    max_attempts = target_amount * 100

    tasks: List[Dict[str, Any]] = []
    pattern_counter: Counter[str] = Counter()

    attempts = 0
    while len(tasks) < target_amount and attempts < max_attempts:
        attempts += 1
        task = generate_task_20_by_subtype("polynomial_factorization")

        if task["id"] in seen_ids:
            continue
        if task["question_text"] in seen_questions:
            continue

        try:
            validate_task_20_polynomial_factorization(task)
        except ValueError:
            continue

        seen_ids.add(task["id"])
        seen_questions.add(task["question_text"])
        tasks.append(task)

        pattern = task["variables"].get("solution_pattern", "unknown")
        pattern_counter[pattern] += 1

        # Progress logging after each successful append
        print(f"[add] {len(tasks)}/{target_amount} (attempt {attempts}) id={task['id']} pattern={pattern}")

        # Progress logging every 100 attempts
        if attempts % 100 == 0:
            print(f"[search] {len(tasks)}/{target_amount} ready; attempt {attempts}/{max_attempts}")

    if len(tasks) < target_amount:
        print(f"[done] Generated {len(tasks)} of {target_amount} in {attempts} attempts, saved to {TARGET_PATH}.")
        raise RuntimeError(
            f"Not enough unique tasks generated: {len(tasks)} of {target_amount}."
        )

    tasks.sort(key=lambda item: item["id"])
    combined_tasks = preserved_tasks + tasks
    combined_tasks.sort(key=lambda item: item.get("id", ""))
    _serialize_tasks(combined_tasks)
    print(
        f"[done] Generated {len(tasks)} new tasks (total {len(combined_tasks)}) "
        f"in {attempts} attempts, saved to {TARGET_PATH}."
    )
    print(
        "Pattern breakdown: "
        + ", ".join(f"{label}={pattern_counter.get(label, 0)}" for label in ("common_poly", "diff_squares", "grouping"))
    )


if __name__ == "__main__":
    main()
