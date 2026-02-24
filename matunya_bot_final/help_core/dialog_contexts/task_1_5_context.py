from __future__ import annotations

from typing import Any, Dict, List, Optional

from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import (
    register_context,
)
from matunya_bot_final.help_core.prompts.task_1_5_dialog_prompts import (
    get_task_1_5_dialog_prompt,
)


@register_context("task_1_5")
async def handle_task_1_5_dialog(
    data: Dict[str, Any],
    history: List[Dict[str, Any]],
) -> Optional[str]:
    """
    Формирует системный промпт для GPT-диалога по заданиям 1–5 (Практика).
    Архитектура: non_generators → source of truth = solution_core.
    """

    # --------------------------------------------------
    # 1️⃣ Достаём данные из state
    # --------------------------------------------------
    task_data = data.get("task_1_5_data")
    solution_core = data.get("task_1_5_solution_core")

    if not isinstance(task_data, dict) or not isinstance(solution_core, dict):
        return None

    # --------------------------------------------------
    # 2️⃣ Собираем текст, который видел ученик
    # --------------------------------------------------
    # display_scenario — это то, что реально показывалось в чате
    main_parts: List[str] = []

    display_scenario = task_data.get("display_scenario", [])
    if isinstance(display_scenario, list):
        for item in display_scenario:
            if isinstance(item, dict) and item.get("type") == "text":
                content = item.get("content")
                if isinstance(content, str) and content.strip():
                    main_parts.append(content.strip())

    main_condition = "\n\n".join(main_parts)

    # --------------------------------------------------
    # 3️⃣ Определяем текущий вопрос
    # --------------------------------------------------
    current_q_number = data.get("current_question_number")
    if isinstance(current_q_number, str) and current_q_number.isdigit():
        current_q_number = int(current_q_number)

    task_text = ""
    tasks = task_data.get("tasks", [])

    if isinstance(tasks, list):
        for q in tasks:
            if (
                isinstance(q, dict)
                and q.get("q_number") == current_q_number
            ):
                qt = q.get("question_text")
                if isinstance(qt, str):
                    task_text = qt
                break

    # fallback — если номер не найден
    if not task_text and isinstance(tasks, list) and tasks:
        first = tasks[0]
        if isinstance(first, dict):
            qt = first.get("question_text")
            if isinstance(qt, str):
                task_text = qt

    # --------------------------------------------------
    # 4️⃣ subtype (paper / ovens / apartments / ...)
    # --------------------------------------------------
    subtype = (
        task_data.get("metadata", {}).get("subtype")
        or task_data.get("subtype")
        or ""
    )

    # Подкладываем поля, которые ждёт prompt
    prepared_task_data = dict(task_data)
    prepared_task_data["main_condition"] = main_condition
    prepared_task_data["task_text"] = task_text
    prepared_task_data["subtype"] = subtype

    # --------------------------------------------------
    # 5️⃣ Определяем narrative текущего вопроса
    # --------------------------------------------------
    current_narrative = None

    if isinstance(tasks, list):
        for q in tasks:
            if isinstance(q, dict) and q.get("q_number") == current_q_number:
                current_narrative = q.get("narrative")
                break

    prepared_task_data["current_narrative"] = current_narrative or ""

    # --------------------------------------------------
    # 6️⃣ Подключаем стратегию для subtype
    # --------------------------------------------------
    dialog_strategy = ""

    if subtype == "paper" and current_narrative:
        try:
            from matunya_bot_final.help_core.dialog_strategies.task_1_5.paper_strategies import (
                PAPER_DIALOG_STRATEGIES,
            )
            dialog_strategy = PAPER_DIALOG_STRATEGIES.get(current_narrative, "")
        except Exception:
            dialog_strategy = ""

    # --------------------------------------------------
    # 7️⃣ Формируем системный промпт
    # --------------------------------------------------
    return get_task_1_5_dialog_prompt(
        task_1_5_data=prepared_task_data,
        solution_core=solution_core,
        dialog_history=history,
        student_name=data.get("student_name"),
        gender=data.get("gender"),
        dialog_strategy=dialog_strategy,
    )


__all__ = ["handle_task_1_5_dialog"]
