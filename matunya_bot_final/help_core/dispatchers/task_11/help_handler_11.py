"""
Обработчик помощи для задания №11.
Полностью повторяет оригинальную логику, но изолирован от других заданий.
"""

import logging
from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from matunya_bot_final.keyboards.inline_keyboards.help_core_keyboard import create_solution_keyboard
from matunya_bot_final.utils.message_manager import send_tracked_message, cleanup_messages_by_category
from matunya_bot_final.help_core.humanizers.template_humanizers.task_11_humanizer import humanize_solution_11
from matunya_bot_final.help_core.dispatchers.common import (
    call_dynamic_solver,
    clean_html_tags,
    format_basic_solution,
    send_processing_message,
    send_solution_result,
    send_solver_not_found_message,
    send_solution_error,
)
logger = logging.getLogger(__name__)


async def handle_task_11_help(callback: CallbackQuery, callback_data, bot: Bot, state: FSMContext):
    """
    Полная логика помощи для задания №11.
    """
    try:
        await callback.answer("🔄 Генерирую решение...")

        task_type = 11
        task_subtype = callback_data.subtype_key
        state_data = await state.get_data()
        task_payload = state_data.get(f"task_{task_type}_data")

        if not isinstance(task_payload, dict):
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        # 🟡 Сообщение "генерирую решение"
        processing_message = await send_processing_message(callback, bot, state, task_type, task_subtype)

        # 🧩 Вызываем динамический решатель
        solution_core = await call_dynamic_solver(str(task_type), task_subtype, task_payload)
        if not solution_core:
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        # 💬 Гуманизация решения
        try:
            humanized_solution = humanize_solution_11(solution_core)
            humanized_solution = clean_html_tags(humanized_solution)
        except Exception as e:
            logger.error(f"[Help11] Ошибка гуманизации: {e}")
            humanized_solution = format_basic_solution(solution_core)

        # 🧹 Убираем сообщение "генерирую решение"
        if processing_message:
            await cleanup_messages_by_category(bot, state, callback.message.chat.id, "solution_processing")

        # 🪄 Создаём клавиатуру окна помощи
        reply_markup = create_solution_keyboard(task_subtype, task_type)

        # 📬 Отправляем готовое решение с клавиатурой
        await send_tracked_message(
            bot=bot,
            chat_id=callback.message.chat.id,
            state=state,
            text=humanized_solution,
            reply_markup=reply_markup,
            category="solution_result",
            message_tag=f"solution_{task_subtype}"
        )

        logger.info(f"✅ Помощь успешно сгенерирована для task_11/{task_subtype}")

    except Exception as e:
        logger.error(f"[Help11] Критическая ошибка: {e}")
        await send_solution_error(callback, bot, f"Ошибка при обработке помощи: {e}")
