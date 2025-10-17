# -*- coding: utf-8 -*-
"""
"Старший официант" для заданий №1–5 (подтип "Шины" и др.)

Задача:
  • Обрабатывать нажатие кнопки 🆘 Помощь для заданий 1–5.
  • Найти нужный решатель (solver) через SOLVER_DISPATCHER или динамически.
  • Передать решение в GPT-гуманизатор (solution_humanizer.py).
  • Отправить ученику красивое решение с универсальной клавиатурой.

Автор: Матюня 🤖
Версия: Help v4.0
"""

import importlib
import inspect
import logging
import traceback
from typing import Any, Dict, Optional

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
)
from matunya_bot_final.help_core.humanizers.solution_humanizer import humanize_solution
from matunya_bot_final.help_core.dispatchers.task_1_5.help_handler_1_5 import SOLVER_DISPATCHER
from matunya_bot_final.keyboards.inline_keyboards.help_core_keyboard import create_solution_keyboard

logger = logging.getLogger(__name__)


# ==========================================================
# 🌿 ГЛАВНАЯ ФУНКЦИЯ ПОМОЩИ
# ==========================================================

async def handle_group_1_5_help(callback: CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext) -> None:
    """
    Обработка запросов помощи для заданий 1–5.
    Использует GPT-гуманизацию (solution_humanizer).
    """
    try:
        await callback.answer("🔄 Генерирую полное решение...")

        task_type = 1  # группа 1–5
        task_subtype = callback_data.subtype_key
        state_data = await state.get_data()
        task_payload = state_data.get("task_1_5_data")

        if not isinstance(task_payload, dict):
            logger.error("Отсутствуют данные задания для task_1_5")
            return

        # Отправляем сообщение о начале
        processing_message = await send_processing_message(callback, bot, state, task_type, task_subtype)

        # === ВЫЗОВ РЕШАТЕЛЯ ===
        try:
            solution_core = await call_dynamic_solver("1_5", task_subtype, task_payload)
            if not solution_core:
                logger.warning(f"Решатель не найден для подтипа {task_subtype}")
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
        except Exception as hum_exc:
            logger.error(f"[Help 1-5] Ошибка гуманизации: {hum_exc}")
            humanized_solution = "😔 Не удалось преобразовать решение в понятный вид."

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


# ==========================================================
# 🔧 ДИНАМИЧЕСКИЙ ВЫЗОВ РЕШАТЕЛЯ
# ==========================================================

async def call_dynamic_solver(task_type: str, task_subtype: str, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Динамически подтягивает модуль решателя и возвращает результат.
    """
    try:
        # Если subtype начинается с tires — направляем в соответствующий solver
        if task_subtype.startswith("tires"):
            path_task_type = "1_5"
            main_subtype = "tires"
            solver_module_path = f"matunya_bot_final.help_core.solvers.task_{path_task_type}.{main_subtype}.{task_subtype}_solver"
        else:
            solver_module_path = f"matunya_bot_final.help_core.solvers.task_{task_type}.{task_subtype}_solver"

        logger.debug(f"Попытка загрузки решателя: {solver_module_path}")
        solver_module = importlib.import_module(solver_module_path)

        if not hasattr(solver_module, 'solve'):
            logger.error(f"Модуль {solver_module_path} не содержит solve()")
            return None

        solve_fn = getattr(solver_module, 'solve')
        return await solve_fn(task_data) if inspect.iscoroutinefunction(solve_fn) else solve_fn(task_data)

    except ModuleNotFoundError:
        # Попробуем через SOLVER_DISPATCHER
        question_num = task_data.get("question_num")
        if question_num in SOLVER_DISPATCHER:
            logger.info(f"Используется SOLVER_DISPATCHER для вопроса {question_num}")
            return SOLVER_DISPATCHER[question_num](task_data)
        logger.warning(f"Решатель не найден для подтипа {task_subtype}")
        return None

    except Exception as e:
        logger.error(f"Ошибка вызова решателя {task_subtype}: {e}")
        logger.error(traceback.format_exc())
        return None


# ==========================================================
# 💬 ОТПРАВКА СООБЩЕНИЙ
# ==========================================================

async def send_processing_message(callback: CallbackQuery, bot: Bot, state: FSMContext,
                                  task_type: int, task_subtype: str) -> Optional[Any]:
    """Отправляет сообщение о начале обработки решения."""
    try:
        text = (
            f"🔄 <b>Генерирую решение...</b>\n\n"
            f"📋 Задание №<b>{task_type}</b> (<b>{task_subtype}</b>)\n\n"
            f"⏳ <i>Подбираю решатель и анализирую задачу...</i>"
        )
        return await send_tracked_message(
            bot=bot,
            chat_id=callback.message.chat.id,
            state=state,
            text=text,
            category="solution_processing",
            message_tag=f"processing_{task_subtype}"
        )
    except Exception as e:
        logger.warning(f"Не удалось отправить сообщение о процессе: {e}")
        return None


async def send_solution_result(callback: CallbackQuery, bot: Bot, state: FSMContext,
                               solution_text: str, task_type: int, task_subtype: str) -> None:
    """Отправляет готовое решение пользователю."""
    try:
        keyboard = create_solution_keyboard(task_subtype, task_type)
        await send_tracked_message(
            bot=bot,
            chat_id=callback.message.chat.id,
            state=state,
            text=solution_text,
            reply_markup=keyboard,
            category="solution_result",
            message_tag=f"solution_{task_subtype}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки решения: {e}")


async def send_solution_error(callback: CallbackQuery, bot: Bot, error_message: str) -> None:
    """Отправляет сообщение об ошибке при генерации решения."""
    try:
        await callback.message.edit_text(
            f"😔 <b>Ошибка генерации решения</b>\n\n{error_message}\n\n"
            f"💡 Попробуй ещё раз или позже.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения об ошибке: {e}")


__all__ = ["handle_group_1_5_help"]
