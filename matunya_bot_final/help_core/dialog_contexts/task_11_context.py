from __future__ import annotations

from typing import Any, Dict, List, Optional

from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import register_context
from matunya_bot_final.help_core.prompts.task_11_dialog_prompts import get_task_11_dialog_prompt
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set


@register_context('task_11')
async def handle_task_11_dialog(data: Dict[str, Any], history: List[Dict[str, Any]]) -> Optional[str]:
    task_data = data.get('task_11_data') or {}
    subtype = task_data.get('subtype') or ''
    task_type = task_data.get('task_type')
    golden_set = await get_golden_set(subtype, task_type=task_type or 11)
    solution_core = data.get('task_11_solution_core')

    system_prompt = get_task_11_dialog_prompt(
        solution_core=solution_core,
        student_name=data.get('student_name'),
        gender=data.get('gender'),
        golden_set=golden_set,
    )
    if not system_prompt:
        system_prompt = data.get('gpt_system_prompt')
    return system_prompt


__all__ = ['handle_task_11_dialog']
