import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from matunya_bot_final.help_core.dispatchers.common import (
    call_dynamic_solver,
    clean_html_tags,
    format_basic_solution,
    send_processing_message,
    send_solution_result,
    send_solver_not_found_message,
    send_solution_error,
)
from matunya_bot_final.help_core.humanizers.template_humanizers.task_11_humanizer import (
    humanize_solution_11,
)
from matunya_bot_final.utils.message_manager import cleanup_messages_by_category


logger = logging.getLogger(__name__)


async def handle_task_11_help(
    callback: CallbackQuery,
    callback_data,
    bot: Bot,
    state: FSMContext,
) -> None:
    """Обрабатывает запрос помощи по задачам №11."""
    try:
        await callback.answer("Готовлю решение...")

        task_type = 11
        task_subtype = callback_data.subtype_key
        state_data = await state.get_data()
        task_payload = state_data.get(f"task_{task_type}_data")

        if not isinstance(task_payload, dict):
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        processing_message = await send_processing_message(
            callback, bot, state, task_type, task_subtype
        )

        solution_core = await call_dynamic_solver(str(task_type), task_subtype, task_payload)
        if not solution_core:
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        try:
            humanized_solution = humanize_solution_11(solution_core)
            humanized_solution = clean_html_tags(humanized_solution)
        except Exception as exc:  # pragma: no cover
            logger.error("[Help11] Ошибка гуманизации: %s", exc)
            humanized_solution = format_basic_solution(solution_core)

        await state.update_data(task_11_solution_core=solution_core)

        if processing_message:
            await cleanup_messages_by_category(
                bot, state, callback.message.chat.id, "solution_processing"
            )

        await send_solution_result(
            callback,
            bot,
            state,
            humanized_solution,
            task_type,
            task_subtype,
        )

        logger.info("[Help11] Решение сформировано для подтипа %s", task_subtype)

    except Exception as exc:  # pragma: no cover
        logger.error("[Help11] Критическая ошибка: %s", exc)
        await send_solution_error(callback, bot, f"Не удалось собрать подсказку: {exc}")
