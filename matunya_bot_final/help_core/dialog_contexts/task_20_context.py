from __future__ import annotations

from typing import Any, Dict, List, Optional

from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import register_context
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set
from matunya_bot_final.help_core.prompts.dialog_prompts import get_help_dialog_prompt


@register_context("task_20")
async def handle_task_20_dialog(data: Dict[str, Any], history: List[Dict[str, Any]]) -> Optional[str]:
    task_data = data.get("task_20_data")
    solution_core = data.get("task_20_solution_core")
    if not isinstance(task_data, dict) or solution_core is None:
        return None

    subtype = task_data.get("subtype") or ""
    golden_set = await get_golden_set(subtype, task_type=20)

    return get_help_dialog_prompt(
        task_1_5_data=task_data,
        solution_core=solution_core,
        dialog_history=history,
        student_name=data.get("student_name"),
        gender=data.get("gender"),
        golden_set=golden_set,
    )


__all__ = ["handle_task_20_dialog"]
