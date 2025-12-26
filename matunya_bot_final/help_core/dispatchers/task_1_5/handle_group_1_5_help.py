# -*- coding: utf-8 -*-
"""
"Старший официант" для заданий №1–5 (подтип "Шины" и др.)

Задача:
  • Обрабатывать нажатие кнопки 🆘 Помощь для заданий 1–5.
  • Найти нужный решатель (solver) через call_dynamic_solver.
  • Передать решение в GPT-гуманизатор (solution_humanizer.py).
  • Отправить ученику красивое решение с универсальной клавиатурой.

Автор: Матюня 🤖
Версия: Help v4.0
"""

import logging
import traceback
from typing import Any, Dict, Optional

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.utils.message_manager import cleanup_messages_by_category
from matunya_bot_final.help_core.humanizers.solution_humanizer import humanize_solution
from matunya_bot_final.utils.text_formatters import normalize_formula
from matunya_bot_final.help_core.dispatchers.common import (
    call_dynamic_solver,
    send_processing_message,
    send_solution_result,
    send_solver_not_found_message,
    send_solution_error,
)
logger = logging.getLogger(__name__)


# ==========================================================
# 🌿 ГЛАВНАЯ ФУНКЦИЯ ПОМОЩИ
# ==========================================================

async def handle_group_1_5_help(callback: CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext) -> None:
    """
    Обработка запросов помощи для заданий 1-5.
    Использует GPT-гуманизацию (solution_humanizer).
    """
    try:
        await callback.answer("🔄 Генерирую полное решение...")

        task_type = 1  # группа 1–5
        task_subtype = callback_data.subtype_key
        state_data = await state.get_data()
        task_payload_raw = state_data.get("task_1_5_data")

        if not isinstance(task_payload_raw, dict):
            logger.error("Отсутствуют данные задания для task_1_5")
            return

        # 🔐 FSM-INVARIANT: index ОБЯЗАН быть передан в solver
        index = state_data.get("index")
        if index is None:
            logger.critical(
                "🚨 FSM CONTRACT BROKEN: handle_group_1_5_help вызван без state['index']"
            )
            await send_solution_error(
                callback,
                bot,
                "Произошла внутренняя ошибка. Попробуй открыть задание ещё раз 🙏",
            )
            return

        # 🔑 ВАЖНО: делаем КОПИЮ и инжектим index
        task_payload = dict(task_payload_raw)
        task_payload["index"] = index

        # Отправляем сообщение о начале
        processing_message = await send_processing_message(callback, bot, state, task_type, task_subtype)

        # === ВЫЗОВ РЕШАТЕЛЯ ===
        try:
            solution_core = await call_dynamic_solver("1_5", task_subtype, task_payload)
            if not solution_core:
                await send_solver_not_found_message(callback, bot, task_type, task_subtype)
                return
        except Exception as solver_exc:
            logger.error(f"[Help 1-5] Ошибка решателя: {solver_exc}")
            await send_solution_error(callback, bot, f"Ошибка при вызове решателя: {solver_exc}")
            return

        # === ГУМАНИЗАЦИЯ ЧЕРЕЗ GPT ===
        try:
            student_name = state_data.get("student_name", "друг")
            student_gender = state_data.get("student_gender", "neutral")

            humanized_solution = await humanize_solution(solution_core, state, student_name, student_gender)
            if humanized_solution:
                humanized_solution = normalize_formula(humanized_solution)
        except Exception as hum_exc:
            logger.error(f"[Help 1-5] Ошибка гуманизации: {hum_exc}")
            humanized_solution = "😔 Не удалось преобразовать решение в понятный вид."

        await state.update_data(task_1_5_solution_core=solution_core)

        # Удаляем "генерирую решение"
        if processing_message:
            await cleanup_messages_by_category(bot, state, callback.message.chat.id, "solution_processing")

        # === ОТПРАВКА РЕЗУЛЬТАТА ===
        await send_solution_result(callback, bot, state, humanized_solution, task_type, task_subtype)
        logger.info(f"✅ Помощь успешно сгенерирована для task_1_5/{task_subtype}")

    except Exception as e:
        logger.error(f"[Help 1-5] Критическая ошибка: {e}")
        logger.error(traceback.format_exc())
        await send_solution_error(callback, bot, f"Ошибка при обработке помощи: {e}")


__all__ = ["handle_group_1_5_help"]
