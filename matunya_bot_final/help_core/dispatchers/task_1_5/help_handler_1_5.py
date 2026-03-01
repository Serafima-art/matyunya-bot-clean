# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import pprint
from typing import Any, Dict, Optional

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.help_core.dispatchers.common import (
    call_dynamic_solver,
    send_solution_result,
    send_solver_not_found_message,
    send_solution_error,
)

logger = logging.getLogger(__name__)


async def handle_task_1_5_help(
    callback: CallbackQuery,
    callback_data,
    bot: Bot,
    state: FSMContext,
) -> None:
    try:
        await callback.answer("Готовлю пошаговое решение...")

        task_type = "1_5"
        state_data = await state.get_data()

        # --------------------------------------------------
        # 1️⃣ Payload (variant)
        # --------------------------------------------------
        task_payload = state_data.get("task_1_5_data")
        logger.warning("STATE task_1_5_data = %s", task_payload)

        if not isinstance(task_payload, dict):
            logger.error("[Help1_5] task_1_5_data отсутствует или не dict")
            await send_solver_not_found_message(callback, bot, 1, "unknown")
            return

        subtype = task_payload.get("subtype") or task_payload.get("metadata", {}).get("subtype")
        if not subtype:
            logger.error("[Help1_5] Нет subtype (ни task_payload.subtype, ни task_payload.metadata.subtype)")
            await send_solver_not_found_message(callback, bot, 1, "unknown")
            return

        # --------------------------------------------------
        # 2️⃣ Определяем q_number и task (конкретный вопрос)
        # --------------------------------------------------
        q_number_raw = getattr(callback_data, "question_num", None) or getattr(callback_data, "task_id", None)
        try:
            q_number = int(q_number_raw) if q_number_raw is not None else 1
        except (TypeError, ValueError):
            q_number = 1

        tasks = task_payload.get("tasks", [])
        task = None
        if isinstance(tasks, list):
            task = next((t for t in tasks if isinstance(t, dict) and t.get("q_number") == q_number), None)

        if not isinstance(task, dict):
            logger.error("[Help1_5] Не найден task для q_number=%s", q_number)
            await send_solver_not_found_message(callback, bot, q_number, subtype)
            return

        pattern = task.get("pattern") or subtype

        # --------------------------------------------------
        # 3️⃣ Solver payload
        # --------------------------------------------------
        solver_payload: Dict[str, Any] = {
            "variant": task_payload,  # весь вариант (контекст таблицы, форматы и т.д.)
            "task": task,             # конкретный вопрос (Q1..Q5)
        }

        # --------------------------------------------------
        # 4️⃣ Solver
        # --------------------------------------------------
        result = await call_dynamic_solver(
            task_type=task_type,
            task_subtype=subtype,
            task_data=solver_payload,
        )

        if not isinstance(result, dict):
            await send_solver_not_found_message(callback, bot, q_number, subtype)
            return

        solution_core = result.get("solution_core")
        help_image = result.get("help_image")

        if not isinstance(solution_core, dict):
            await send_solver_not_found_message(callback, bot, q_number, subtype)
            return

        # --------------------------------------------------
        # 5️⃣ Humanizer (разная логика для subtype)
        # --------------------------------------------------
        try:
            # 📄 Paper
            if subtype == "paper":
                from matunya_bot_final.help_core.humanizers.template_humanizers.task_1_5.paper_humanizer import humanize
                humanized_solution = humanize(solution_core)

            # 🔥 Stoves (новый non-generator)
            elif subtype == "stoves":
                from matunya_bot_final.help_core.humanizers.template_humanizers.task_1_5.stoves_humanizer import humanize
                humanized_solution = humanize(solution_core)

            # 🛞 Tires (legacy GPT)
            elif subtype.startswith("tires"):
                from matunya_bot_final.help_core.humanizers.solution_humanizer import humanize_solution
                student_name = state_data.get("student_name", "ученик")
                humanized_solution = await humanize_solution(solution_core, state, student_name)

            else:
                logger.error("[Help1_5] Неизвестный subtype=%s", subtype)
                await send_solver_not_found_message(callback, bot, q_number, subtype)
                return

        except Exception as exc:
            logger.error("[Help1_5] Ошибка гуманизации: %s", exc, exc_info=True)
            await send_solution_error(callback, bot, "Ошибка при оформлении решения.")
            return

        # --------------------------------------------------
        # 6️⃣ Сохраняем в state
        # --------------------------------------------------
        await state.update_data(
            task_1_5_help_text=humanized_solution,
            task_1_5_solution_core=solution_core,
            help_image=help_image,
            help_opened=True,
        )

        # --------------------------------------------------
        # 7️⃣ Отправляем
        # --------------------------------------------------
        await send_solution_result(
            callback,
            bot,
            state,
            humanized_solution,
            q_number,   # важно: число, чтобы красиво показывалось "Задание №..."
            subtype,    # важно: subtype как task_subtype
        )

        logger.info("[Help1_5] Решение успешно сформировано (subtype=%s, q=%s)", subtype, q_number)

    except Exception as exc:
        logger.error("[Help1_5] Критическая ошибка: %s", exc, exc_info=True)
        await send_solution_error(callback, bot, f"Не удалось собрать подсказку: {exc}")
