from __future__ import annotations

from typing import Any, Dict, List, Optional

from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import register_context
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set
# Импортируем конструктор промптов для 8 задания (его напишем следующим)
from matunya_bot_final.help_core.prompts.task_8_dialog_prompts import get_task_8_dialog_prompt


@register_context("task_8")
async def handle_task_8_dialog(data: Dict[str, Any], history: List[Dict[str, Any]]) -> Optional[str]:
    """
    Формирует системный промпт для GPT-диалога по Заданию 8.
    """
    # Получаем данные, которые мы сохранили в хендлерах
    task_data = data.get("task_8_data")
    solution_core = data.get("task_8_solution_core")

    if not isinstance(task_data, dict) or solution_core is None:
        return None

    subtype = task_data.get("subtype") or ""

    # Получаем эталонные примеры (если есть)
    golden_set = await get_golden_set(subtype, task_type=8)

    # Вызываем конструктор промпта
    return get_task_8_dialog_prompt(
        task_data=task_data,
        solution_core=solution_core,
        dialog_history=history,
        student_name=data.get("student_name"),
        gender=data.get("gender"),
        golden_set=golden_set,
    )


__all__ = ["handle_task_8_dialog"]
