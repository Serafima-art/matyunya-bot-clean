from __future__ import annotations

import random
import logging
from pathlib import Path
import json

from matunya_bot_final.loader import TASKS_DB, DATA_DIR

logger = logging.getLogger(__name__)

# ==============================================================
# Пути к Paper-ассетам
# ==============================================================

PAPER_INTRO_PATH = DATA_DIR / "tasks_1_5" / "paper" / "paper_intro.json"

NON_GEN_ASSETS_DIR = (
    DATA_DIR.parent
    / "non_generators"
    / "task_1_5"
    / "paper"
    / "assets"
)


# ==============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (перенос 1:1)
# ==============================================================

def _sort_key_paper_id(item: dict) -> int:
    import re
    m = re.search(r"_var_(\d+)$", str(item.get("id", "")))
    return int(m.group(1)) if m else 10**9


def _load_paper_intro() -> list[dict]:
    if not PAPER_INTRO_PATH.exists():
        return []

    raw = json.loads(PAPER_INTRO_PATH.read_text(encoding="utf-8"))

    if isinstance(raw, dict) and "paper_intro" in raw:
        intro_block = raw["paper_intro"]

        title = intro_block.get("title", "").strip()
        text = intro_block.get("text", "").strip()

        content = ""
        if title:
            content += f"<b>{title}</b>\n\n"
        if text:
            content += text

        return [
            {
                "type": "image",
                "path": str(NON_GEN_ASSETS_DIR / "task_paper_formats.png"),
                "caption": None,
            },
            {
                "type": "text",
                "content": content,
            },
        ]

    if isinstance(raw, list):
        return raw

    return []


def _attach_intro_assets(display_scenario: list[dict]) -> list[dict]:
    out = []
    for el in display_scenario:
        if not isinstance(el, dict):
            continue

        if el.get("type") == "image":
            p = el.get("path", "")
            path_obj = Path(p)
            if not path_obj.is_absolute():
                path_obj = NON_GEN_ASSETS_DIR / path_obj.name
            el = {**el, "path": str(path_obj)}

        out.append(el)

    return out


# ==============================================================
# ОСНОВНАЯ ФУНКЦИЯ LOADER
# ==============================================================

async def load_paper_variant() -> dict | None:
    variants = TASKS_DB.get("1_5_paper") or []
    if not variants:
        logger.error("❌ TASKS_DB['1_5_paper'] пуст")
        return None

    variants_sorted = sorted(variants, key=_sort_key_paper_id)
    chosen = random.choice(variants_sorted)

    questions = chosen.get("questions", [])
    table_context = chosen.get("table_context")
    image_file = chosen.get("image_file")

    intro = _attach_intro_assets(_load_paper_intro())

    if intro and not any(el.get("type") == "image" for el in intro):
        if image_file:
            intro = [
                {
                    "type": "image",
                    "path": str(NON_GEN_ASSETS_DIR / image_file),
                    "caption": None,
                }
            ] + intro

    return {
        "id": chosen.get("id"),
        "image_file": image_file,
        "table_context": table_context,
        "display_scenario": intro,
        "tasks": questions,
        "metadata": {"subtype": "paper"},
    }
