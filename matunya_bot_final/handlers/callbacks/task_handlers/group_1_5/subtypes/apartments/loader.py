import json
from pathlib import Path


async def load_apartments_variant():

    json_path = Path(
        "matunya_bot_final/data/tasks_1_5/apartments/tasks_1_5_apartments.json"
    )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data[0]
