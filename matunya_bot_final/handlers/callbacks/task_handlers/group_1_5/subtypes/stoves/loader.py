from matunya_bot_final.loader import TASKS_DB
import random
import logging

logger = logging.getLogger(__name__)

async def load_stoves_variant() -> dict | None:
    variants = TASKS_DB.get("1_5_stoves") or []
    if not variants:
        logger.error("❌ TASKS_DB['1_5_stoves'] пуст")
        return None

    chosen = random.choice(variants)

    questions = chosen.get("questions", [])
    table_context = chosen.get("table_context")
    room_context = chosen.get("room_context")

    return {
        "id": chosen.get("id"),
        "room_context": room_context,   # ← ВОТ ЭТА СТРОКА НУЖНА
        "table_context": table_context,
        "display_scenario": [],
        "tasks": questions,
        "metadata": {"subtype": "stoves"},
    }
