from __future__ import annotations

from typing import Any, Dict, List, Optional

from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import register_context
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set
from matunya_bot_final.help_core.prompts.task_15_dialog_prompts import (
    get_task_15_dialog_prompt,
)


@register_context("task_15")
async def handle_task_15_dialog(
    data: Dict[str, Any],
    history: List[Dict[str, Any]],
) -> Optional[str]:
    """
    Формирует системный промпт для GPT-диалога по Заданию 15 (Планиметрия).
    """

    # Данные задания
    task_data = data.get("task_15_data")
    solution_core = data.get("task_15_solution_core")

    # Жёсткая валидация, как в task_8
    if not isinstance(task_data, dict) or not isinstance(solution_core, list):
        return None

    subtype = task_data.get("subtype") or ""

    # Golden set (если есть)
    golden_set = await get_golden_set(subtype, task_type=15)

    # Формируем системный промпт
    return get_task_15_dialog_prompt(
        task_data=task_data,
        solution_core=solution_core,
        dialog_history=history,
        student_name=data.get("student_name"),
        gender=data.get("gender"),
        golden_set=golden_set,
    )


__all__ = ["handle_task_15_dialog"]
