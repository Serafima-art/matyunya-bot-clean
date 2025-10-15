from __future__ import annotations
import random
from typing import Optional, Tuple

from .task_6 import MAIN_PROMPT, SUBTYPES
from ...gpt_utils import ask_gpt_with_history  # асинхронная функция без истории

def list_task6_subtypes() -> list[str]:
    """Список доступных подтипов (ключи SUBTYPES)."""
    return list(SUBTYPES.keys())

def _pick_subtype(subtype_key: Optional[str]) -> str:
    """Проверка/выбор подтипа. Если не задан — берём случайный."""
    keys = list_task6_subtypes()
    if not keys:
        raise ValueError("В SUBTYPES пока пусто: добавь хотя бы один подтип для задания №6.")
    if subtype_key is None:
        return random.choice(keys)
    if subtype_key not in SUBTYPES:
        raise ValueError(f"Неизвестный подтип: {subtype_key}. Доступно: {', '.join(keys)}")
    return subtype_key

def build_task6_prompt(subtype_key: Optional[str] = None, examples_limit: int = 2) -> Tuple[str, str]:
    """
    Собирает финальный промпт для GPT.
    Возвращает (prompt_text, used_subtype_key).
    """
    used = _pick_subtype(subtype_key)
    info = SUBTYPES[used]

    # примеры — только как ориентир по стилю, не копировать!
    examples = info.get("examples", [])[:max(0, examples_limit)]
    examples_block = ""
    if examples:
        examples_block = (
            "Примеры по этому подтипу (не копируй числа и формулировки, они только для ориентира стиля):\n"
            + "\n\n".join(examples) + "\n\n"
        )

    prompt = (
        f"{MAIN_PROMPT}"
        f"Подтип: {used}\n"
        f"Описание подтипа: {info.get('description','')}\n\n"
        f"{examples_block}"
        "Сгенерируй строго ОДНО новое задание №6 по указанному подтипу. "
        "Числа и выражения придумай заново."
    )
    return prompt, used

async def generate_task_6(subtype_key: Optional[str] = None) -> Tuple[str, str]:
    """
    Генерирует задание №6.
    Возвращает (text, used_subtype_key).
    """
    prompt, used = build_task6_prompt(subtype_key=subtype_key)
    text = await ask_gpt_with_history(prompt)
    return text, used