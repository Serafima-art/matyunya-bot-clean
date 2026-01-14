from __future__ import annotations

from typing import Any, Dict, List, Optional

from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import (
    register_context,
)
from matunya_bot_final.help_core.knowledge.golden_set_reader import get_golden_set
from matunya_bot_final.help_core.prompts.task_16_dialog_prompts import (
    get_task_16_dialog_prompt,
)


@register_context("task_16")
async def handle_task_16_dialog(
    data: Dict[str, Any],
    history: List[Dict[str, Any]],
) -> Optional[str]:
    """
    Формирует системный промпт для GPT-диалога по Заданию 16 (Окружность).

    Архитектурные принципы:
    - GPT НЕ видит изображение
    - GPT НЕ анализирует текст задачи
    - GPT работает строго по solution_core
    - Геометрическая схема передаётся как ФАКТ через help_image
    """

    # ------------------------------------------------------------------
    # 1️⃣ Данные задания и решения
    # ------------------------------------------------------------------
    task_data = data.get("task_16_data")
    solution_core = data.get("task_16_solution_core")

    # Уже показанный текст помощи (humanizer)
    help_text = data.get("task_16_help_text")

    # ------------------------------------------------------------------
    # 2️⃣ Жёсткая валидация
    # ------------------------------------------------------------------
    if not isinstance(task_data, dict) or not isinstance(solution_core, dict):
        return None

    pattern = task_data.get("pattern") or ""

    # ------------------------------------------------------------------
    # 3️⃣ Golden set (если есть)
    # ------------------------------------------------------------------
    golden_set = await get_golden_set(pattern, task_type=16)

    # ------------------------------------------------------------------
    # 4️⃣ Извлечение help_image → описание схемы
    # ------------------------------------------------------------------
    help_image = solution_core.get("help_image")
    image_description: Optional[str] = None

    if isinstance(help_image, dict):
        schema = help_image.get("schema")
        params = help_image.get("params")

        if schema and isinstance(params, dict):
            # ⚠️ ВАЖНО:
            # Здесь мы НЕ формируем красивый текст.
            # Мы передаём GPT строгие факты, чтобы он НЕ ФАНТАЗИРОВАЛ.
            image_description = (
                "Известна следующая геометрическая схема, "
                "которая была показана ученику:\n"
                f"Схема: {schema}\n"
                f"Факты схемы: {params}\n"
                "Эти данные считаются достоверными и не требуют уточнений."
            )

    # ------------------------------------------------------------------
    # 5️⃣ Формирование системного промпта
    # ------------------------------------------------------------------
    return get_task_16_dialog_prompt(
        task_data=task_data,
        solution_core=solution_core,
        dialog_history=history,
        student_name=data.get("student_name"),
        gender=data.get("gender"),
        golden_set=golden_set,
        help_text=help_text,
        image_description=image_description,  # 👈 ключевое изменение
    )


__all__ = ["handle_task_16_dialog"]
