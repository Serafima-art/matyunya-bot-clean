# matunya_bot_final/help_core/dispatchers/task_6/help_handler_6.py

import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.help_core.dispatchers.common import (
    call_dynamic_solver,
    send_solution_result,
    send_solver_not_found_message,
    send_solution_error,
    # Убираем лишние импорты, которые здесь не используются
)
# ★★★ ИСПРАВЛЕНО: Правильный импорт нашего "Декоратора" ★★★
from matunya_bot_final.help_core.humanizers.template_humanizers.task_6_humanizer import (
    humanize,
)
from matunya_bot_final.utils.message_manager import cleanup_messages_by_category

logger = logging.getLogger(__name__)


async def handle_task_6_help(
    callback: CallbackQuery,
    callback_data, # callback_data здесь нужен, чтобы не ломать сигнатуру
    bot: Bot,
    state: FSMContext,
) -> None:
    """Обрабатывает запрос помощи по задачам №6."""
    try:
        await callback.answer("Готовлю пошаговое решение...")

        task_type = 6
        state_data = await state.get_data()
        task_payload = state_data.get(f"task_{task_type}_data")

        logger.error("[DEBUG HELP6] task_payload: %s", task_payload)

        if not isinstance(task_payload, dict):
            await send_solver_not_found_message(callback, bot, task_type, "unknown")
            return

        # ★★★ ИСПРАВЛЕНО: Берем subtype из правильного места ★★★
        task_subtype = task_payload.get("subtype")
        if not task_subtype:
            logger.error("[Help6] В task_payload отсутствует ключ 'subtype'")
            await send_solver_not_found_message(callback, bot, task_type, "unknown")
            return

        # processing_message убрали, так как send_solution_result теперь редактирует сообщение

        # --- Вызов решателя ---
        solution_core = await call_dynamic_solver(str(task_type), task_subtype, task_payload)
        if not solution_core:
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        # --- Формирование текста решения ---
        try:
            # ★★★ ИСПРАВЛЕНО: Правильный вызов "Декоратора" ★★★
            humanized_solution = humanize(solution_core)
            # clean_html_tags не нужен, наш humanizer уже отдает чистый HTML
        except Exception as exc:
            logger.error("[Help6] Ошибка гуманизации: %s", exc, exc_info=True)
            # format_basic_solution можно убрать, так как наш humanize надежен
            await send_solution_error(callback, bot, "Ошибка при оформлении решения.")
            return

        # --- Сохраняем solution_core в state ---
        await state.update_data(task_6_solution_core=solution_core)

        # --- Отправляем итог пользователю ---
        await send_solution_result(
            callback,
            bot,
            state,
            humanized_solution,
            task_type,
            task_subtype,
        )

        logger.info("[Help6] Решение успешно сформировано для подтипа %s", task_subtype)

    except Exception as exc:
        logger.error("[Help6] Критическая ошибка: %s", exc, exc_info=True)
        await send_solution_error(callback, bot, f"Не удалось собрать подсказку: {exc}")
