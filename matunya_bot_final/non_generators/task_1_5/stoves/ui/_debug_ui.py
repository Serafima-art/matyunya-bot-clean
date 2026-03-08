# -*- coding: utf-8 -*-
"""
Debug-скрипт для проверки UI-текстов Печей.

Проверяет builders, которые формируют тексты "на лету",
и записывает результат в файл:

matunya_bot_final/non_generators/task_1_5/stoves/ui/debug_stoves_ui.txt
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------
# Добавляем корень проекта в PYTHONPATH
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------
# Импорты builders
# ---------------------------------------------------------

from matunya_bot_final.non_generators.task_1_5.stoves.ui.intro_builder import (
    build_stoves_intro,
)
from matunya_bot_final.non_generators.task_1_5.stoves.ui.q4_builder import (
    build_q4_text,
)
from matunya_bot_final.non_generators.task_1_5.stoves.ui.q5_builder import (
    build_q5_text,
)

# ---------------------------------------------------------
# Пути
# ---------------------------------------------------------

MATYUNYA_ROOT = Path(__file__).resolve().parents[4]

DB_PATH = (
    MATYUNYA_ROOT
    / "data"
    / "tasks_1_5"
    / "stoves"
    / "tasks_1_5_stoves.json"
)

OUTPUT_PATH = Path(__file__).resolve().parent / "debug_stoves_ui.txt"

# ---------------------------------------------------------
# Registry builders
# ---------------------------------------------------------
# 0 = intro (если захочешь отдельно прокинуть интро-данные)
# 4 = Q4
# 5 = Q5
# ---------------------------------------------------------

BUILDERS = {
    0: build_stoves_intro,
    4: build_q4_text,
    5: build_q5_text,
}


def _load_tasks_from_db(db_path: Path) -> List[Dict[str, Any]]:
    """
    Загружает задачи из JSON.
    Поддерживает оба формата:
    1) list[dict]
    2) {"variants": [...]}
    """
    with open(db_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    if isinstance(raw_data, list):
        return raw_data

    if isinstance(raw_data, dict):
        variants = raw_data.get("variants", [])
        if isinstance(variants, list):
            return variants

    raise ValueError(f"Неподдерживаемая структура JSON в файле: {db_path}")


def _safe_pretty(value: Any) -> str:
    """
    Безопасно превращает значение в строку для debug-отчёта.
    """
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except Exception:
        return repr(value)


def run_debug() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"База не найдена: {DB_PATH}")

    variants = _load_tasks_from_db(DB_PATH)

    lines: List[str] = []
    lines.append("DEBUG STOVES UI")
    lines.append("")
    lines.append(f"Файл базы: {DB_PATH}")
    lines.append(f"Всего записей: {len(variants)}")
    lines.append("")

    total_ok = 0
    total_errors = 0
    total_skipped = 0

    for variant in variants:

        variant_id = variant.get("id")
        questions = variant.get("questions", [])

        lines.append("============================================================")
        lines.append(f"VARIANT: {variant_id}")
        lines.append("============================================================")

        for task in questions:

            q_number = task.get("q_number")
            pattern = task.get("pattern")
            narrative = task.get("narrative")

            builder = BUILDERS.get(q_number)

            lines.append(f"\nQ{q_number} | {pattern} | {narrative}")
            lines.append(f"INPUT DATA: {task.get('input_data')}")
            lines.append(f"TASK KEYS: {list(task.keys())}")

            if not builder:
                lines.append("⏭ BUILDER НЕ НАЗНАЧЕН\n")
                total_skipped += 1
                continue

            try:

                text = builder(task)

                lines.append("✔ OK")
                lines.append(text)
                lines.append("")

                total_ok += 1

            except Exception as e:

                lines.append("❌ ERROR")
                lines.append(str(e))
                lines.append(traceback.format_exc())

                total_errors += 1

    lines.append("=" * 60)
    lines.append("ИТОГ")
    lines.append("=" * 60)
    lines.append(f"OK: {total_ok}")
    lines.append(f"ERRORS: {total_errors}")
    lines.append(f"SKIPPED: {total_skipped}")
    lines.append("")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("DEBUG завершён.")
    print(f"Отчёт записан: {OUTPUT_PATH}")


if __name__ == "__main__":
    run_debug()
