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

from matunya_bot_final.handlers.callbacks.task_handlers.task_15.task_15_handler import (
    PATTERN_TO_THEME,
)


# Humanizer для Задания 15
from matunya_bot_final.help_core.humanizers.template_humanizers.task_15_humanizer import (
    humanize,
)

logger = logging.getLogger(__name__)


async def handle_task_15_help(
    callback: CallbackQuery,
    callback_data,
    bot: Bot,
    state: FSMContext,
) -> None:
    """
    Обрабатывает запрос помощи по Заданию №15 (Планиметрия).
    """
    try:
        await callback.answer("Готовлю пошаговое решение...")

        task_type = 15
        state_data = await state.get_data()

        # Достаём данные задания
        state_data = await state.get_data()

        task_payload = state_data.get("task_15_data")

        if not isinstance(task_payload, dict):
            await send_solver_not_found_message(callback, bot, task_type, "unknown")
            return

        # ✅ pattern берём из payload
        pattern = task_payload.get("pattern")
        if not pattern:
            logger.error("[Help15] В task_payload отсутствует ключ 'pattern'")
            await send_solver_not_found_message(callback, bot, task_type, "unknown")
            return

        # ✅ theme определяем через PATTERN_TO_THEME
        theme_key = PATTERN_TO_THEME.get(pattern)
        if not theme_key:
            logger.error("[Help15] Не найдена тема для pattern=%s", pattern)
            await send_solver_not_found_message(callback, bot, task_type, "unknown")
            return

        # --- 1. Вызов динамического решателя ---
        solution_core = await call_dynamic_solver(
            str(task_type),   # "15"
            theme_key,        # 👈 ВАЖНО: передаём ТЕМУ
            task_payload,
        )

        if not isinstance(solution_core, list) or not solution_core:
            await send_solver_not_found_message(callback, bot, task_type)
            return

        # --- 2. Гуманизация решения ---
        try:
            humanized_solution = humanize(solution_core)
        except Exception as exc:
            logger.error("[Help15] Ошибка гуманизации: %s", exc, exc_info=True)
            await send_solution_error(callback, bot, "Ошибка при оформлении решения.")
            return

        await state.update_data(task_15_help_text=humanized_solution)

        # --- 3. Сохраняем solution_core в state ---
        await state.update_data(task_15_solution_core=solution_core)

        # --- 4. Отправляем результат ---
        await send_solution_result(
            callback,
            bot,
            state,
            humanized_solution,
            task_type,
            theme_key,
        )

        # ✅ ВАЖНО: фиксируем, что помощь ОТКРЫТА
        await state.update_data(help_opened=True)

        logger.info(
            "[Help15] Решение успешно сформировано для темы %s",
            theme_key,
        )

    except Exception as exc:
        logger.error("[Help15] Критическая ошибка: %s", exc, exc_info=True)
        await send_solution_error(
            callback,
            bot,
            f"Не удалось собрать подсказку: {exc}",
        )
