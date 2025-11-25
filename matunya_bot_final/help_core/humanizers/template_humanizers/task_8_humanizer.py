"""Рыба humanizer'а для задания 8 (integer_expressions)."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


IDEA_PLACEHOLDER = "{{IDEA_TEXT}}"
ATTENTION_TIPS: List[str] = [
    "{{ATTENTION_TIP_1}}",
    "{{ATTENTION_TIP_2}}",
    "{{ATTENTION_TIP_3}}",
]
KNOWLEDGE_TIPS: List[str] = [
    "{{KNOWLEDGE_TIP_1}}",
    "{{KNOWLEDGE_TIP_2}}",
    "{{KNOWLEDGE_TIP_3}}",
]


def render_task_8(solution_core: Dict[str, Any]) -> str:
    """Собирает HTML-строку по solution_core без наполнения текстом."""
    parts: List[str] = []

    idea_text = str(solution_core.get("explanation_idea") or IDEA_PLACEHOLDER)
    parts.append(_render_idea(idea_text))

    steps = solution_core.get("calculation_steps") or []
    parts.append(_render_steps(steps))

    final_answer_value = str(
        (solution_core.get("final_answer") or {}).get("value_display", "{{FINAL_ANSWER}}")
    )
    parts.append(_render_final_answer(final_answer_value))

    attention_items = _extract_list(solution_core.get("attention_tips"), ATTENTION_TIPS)
    parts.append(_render_attention_block(attention_items))

    knowledge_items = _extract_list(solution_core.get("knowledge_tips"), KNOWLEDGE_TIPS)
    parts.append(_render_knowledge_block(knowledge_items))

    return "\n".join(parts)


def _render_idea(idea_text: str) -> str:
    return (
        "💡 <b>Идея решения:</b>\n"
        f"{idea_text}\n"
    )


def _render_steps(steps: Iterable[Dict[str, Any]]) -> str:
    rendered: List[str] = []
    rendered.append("🪜 <b>Пошаговое решение</b>")
    for step in steps:
        rendered.append(_render_step(step))
    return "\n".join(rendered)


def _render_step(step: Dict[str, Any]) -> str:
    number = step.get("step_number", "{{STEP_NUMBER}}")
    description = str(step.get("description") or "{{STEP_DESCRIPTION}}")
    formula = step.get("formula_calculation")

    lines = [f"<b>Шаг {number}.</b> {description}"]
    if formula:
        lines.append(f"➡️ <b>{formula}</b>")
    return "\n".join(lines)


def _render_final_answer(value_display: str) -> str:
    return f"🎯Ответ: <b>{value_display}</b>"


def _render_attention_block(tips: Iterable[str]) -> str:
    lines = ["✨ <b>Обрати внимание:</b>"]
    for tip in tips:
        lines.append(str(tip))
    return "\n".join(lines)


def _render_knowledge_block(tips: Iterable[str]) -> str:
    lines = ["✨ <b>Полезно знать</b>", "<tg-spoiler>"]
    for tip in tips:
        lines.append(str(tip))
    lines.append("</tg-spoiler>")
    return "\n".join(lines)


def _extract_list(value: Any, fallback: List[str]) -> List[str]:
    if isinstance(value, list) and value:
        return [str(item) for item in value]
    return list(fallback)
