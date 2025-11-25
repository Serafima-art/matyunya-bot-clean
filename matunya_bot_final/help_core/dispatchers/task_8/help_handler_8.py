import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.help_core.dispatchers.common import (
    call_dynamic_solver,
    send_solution_result,
    send_solver_not_found_message,
    send_solution_error,
)

# ИСПРАВЛЕНО: Импортируем 'humanize', а не 'render_task_8'
from matunya_bot_final.help_core.humanizers.template_humanizers.task_8_humanizer import (
    humanize,
)

logger = logging.getLogger(__name__)


async def handle_task_8_help(
    callback: CallbackQuery,
    callback_data,
    bot: Bot,
    state: FSMContext,
) -> None:
    """Обрабатывает запрос помощи по задачам №8 (Алгебра)."""
    try:
        await callback.answer("Готовлю пошаговое решение...")

        task_type = 8
        state_data = await state.get_data()

        # Достаем данные именно для 8 задания
        task_payload = state_data.get(f"task_{task_type}_data")

        if not isinstance(task_payload, dict):
            await send_solver_not_found_message(callback, bot, task_type, "unknown")
            return

        # Определяем подтип
        task_subtype = task_payload.get("subtype")
        if not task_subtype:
            logger.error("[Help8] В task_payload отсутствует ключ 'subtype'")
            await send_solver_not_found_message(callback, bot, task_type, "unknown")
            return

        # --- 1. Вызов динамического решателя ---
        solution_core = await call_dynamic_solver(str(task_type), task_subtype, task_payload)

        if not solution_core:
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        # --- 2. Формирование текста решения (Хьюманизация) ---
        try:
            # ИСПРАВЛЕНО: Вызов правильной функции
            humanized_solution = humanize(solution_core)
        except Exception as exc:
            logger.error("[Help8] Ошибка гуманизации: %s", exc, exc_info=True)
            await send_solution_error(callback, bot, "Ошибка при оформлении решения.")
            return

        # --- 3. Сохраняем solution_core в state ---
        await state.update_data(task_8_solution_core=solution_core)

        # --- 4. Отправляем итог пользователю ---
        await send_solution_result(
            callback,
            bot,
            state,
            humanized_solution,
            task_type,
            task_subtype,
        )

        logger.info("[Help8] Решение успешно сформировано для подтипа %s", task_subtype)

    except Exception as exc:
        logger.error("[Help8] Критическая ошибка: %s", exc, exc_info=True)
        await send_solution_error(callback, bot, f"Не удалось собрать подсказку: {exc}")
