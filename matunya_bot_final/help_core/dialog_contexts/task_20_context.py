from __future__ import annotations

from typing import Any, Dict, List, Optional

from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import register_context

# --- ИЗМЕНЕНИЕ: ИМПОРТИРУЕМ РОДНОЙ ПРОМПТ ЗАДАНИЯ 20 ---
from matunya_bot_final.help_core.prompts.task_20_dialog_prompts import get_task_20_dialog_prompt


@register_context("task_20")
async def handle_task_20_dialog(data: Dict[str, Any], history: List[Dict[str, Any]]) -> Optional[str]:
    """
    Формирует системный промпт для GPT-диалога по Заданию 20.
    """
    # Достаем данные из FSM
    task_data = data.get("task_20_data")
    solution_core = data.get("task_20_solution_core")

    if not isinstance(task_data, dict) or solution_core is None:
        return None

    # --- ИЗМЕНЕНИЕ: ВЫЗЫВАЕМ СПЕЦИАЛИЗИРОВАННУЮ ФУНКЦИЮ ---
    # (Она принимает task_data, solution_core, имя и пол)
    return get_task_20_dialog_prompt(
        task_data=task_data,
        solution_core=solution_core,
        student_name=data.get("student_name"),
        gender=data.get("gender"),
        # Если твой файл task_20_dialog_prompts поддерживает историю, раскомментируй:
        # dialog_history=history
    )


__all__ = ["handle_task_20_dialog"]
