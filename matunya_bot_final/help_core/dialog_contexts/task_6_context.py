# matunya_bot_final/help_core/dialog_contexts/task_6_context.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import register_context
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set
from matunya_bot_final.help_core.prompts.dialog_prompts import get_help_dialog_prompt


@register_context("task_6")
async def handle_task_6_dialog(data: Dict[str, Any], history: List[Dict[str, Any]]) -> Optional[str]:
    """
    Контекст диалога для задания №6.
    Позволяет GPT давать помощь с учётом особенностей темы:
    дроби, десятичные числа, степени и смешанные выражения.
    """
    task_data = data.get("task_6_data")
    solution_core = data.get("task_6_solution_core")

    if not isinstance(task_data, dict) or solution_core is None:
        return None

    subtype = task_data.get("subtype") or ""
    golden_set = await get_golden_set(subtype, task_type=6)

    # 🌿 Дополнительные подсказки для GPT (мета-контекст)
    task_features = {
        "task_type": 6,
        "topic": "Арифметические действия с дробями и степенями",
        "common_errors": [
            "Путают порядок действий при смешанных операциях.",
            "Не приводят дроби к общему знаменателю перед сложением или вычитанием.",
            "Забывают, что минус при возведении в чётную степень исчезает.",
            "Пишут 0.5 вместо 1/2 — GPT должен понимать оба варианта.",
        ],
        "style_tip": (
            "Объясняй поэтапно, без громоздких терминов, как на уроке с учеником 9 класса. "
            "Проверяй, понял ли ученик ход решения. Если ответ верный — обязательно похвали."
        ),
    }

    return get_help_dialog_prompt(
        task_1_5_data=task_data,
        solution_core=solution_core,
        dialog_history=history,
        student_name=data.get("student_name"),
        gender=data.get("gender"),
        golden_set=golden_set,
        extra_context=task_features,  # ⬅️ передаём особенности задания
    )


__all__ = ["handle_task_6_dialog"]
