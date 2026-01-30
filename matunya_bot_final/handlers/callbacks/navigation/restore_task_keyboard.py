from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from matunya_bot_final.utils.message_manager import cleanup_messages_by_category
from matunya_bot_final.keyboards.navigation.emergency import emergency_nav_kb

# 👇 импортируем карусель задания 16
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_16.task_16_carousel import (
    generate_task_16_overview_text,
    get_task_16_carousel_keyboard,
)
from matunya_bot_final.handlers.callbacks.task_handlers.task_16.task_16_handler import (
    THEMES_16,
    THEMES_ORDER,
)

logger = logging.getLogger(__name__)
router = Router(name="restore_task_keyboard")


@router.callback_query(F.data == "restore_task_keyboard")
async def restore_task_keyboard_handler(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
):
    """
    🔙 Аварийный возврат.

    Логика:
    1) Пытаемся восстановить клавиатуру задания (если есть данные)
    2) Если невозможно — честно возвращаем пользователя в карусель задания 16
    """

    await callback.answer()
    chat_id = callback.message.chat.id

    # ------------------------------------------------------------------
    # 1. Убираем сообщения помощи / решений
    # ------------------------------------------------------------------
    try:
        await cleanup_messages_by_category(
            bot=bot,
            state=state,
            chat_id=chat_id,
            category="solution_result",
        )
    except Exception as e:
        logger.warning(
            "[restore_task_keyboard] Не удалось очистить сообщения помощи: %s",
            e,
        )

    state_data = await state.get_data()
    restore_payload = state_data.get("keyboard_to_restore")

    # ------------------------------------------------------------------
    # 2. ПЫТАЕМСЯ восстановить задание
    # ------------------------------------------------------------------
    if restore_payload:
        chat_id_restore = restore_payload.get("chat_id")
        message_id = restore_payload.get("message_id")
        reply_markup = restore_payload.get("reply_markup")

        if chat_id_restore and message_id and reply_markup:
            try:
                await bot.edit_message_reply_markup(
                    chat_id=chat_id_restore,
                    message_id=message_id,
                    reply_markup=reply_markup,
                )

                # удаляем аварийное сообщение
                try:
                    await callback.message.delete()
                except Exception:
                    pass

                logger.info("[restore_task_keyboard] Клавиатура задания восстановлена")
                return

            except Exception as e:
                logger.warning(
                    "[restore_task_keyboard] Не удалось восстановить задание: %s",
                    e,
                )

    # ------------------------------------------------------------------
    # 3. FALLBACK — возвращаем в карусель задания 16
    # ------------------------------------------------------------------
    logger.info(
        "[restore_task_keyboard] Fallback: возврат в карусель задания 16",
    )

    # чистим всё, что могло остаться
    await cleanup_messages_by_category(bot, state, chat_id, "tasks")
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    current_theme = state_data.get("current_theme") or THEMES_ORDER[0]

    overview_text = (
        "❗ <b>Решение для этого задания сейчас недоступно.</b>\n\n"
        "Пожалуйста, выбери другое задание 👇\n\n"
        + generate_task_16_overview_text(THEMES_16, current_theme)
    )

    keyboard = get_task_16_carousel_keyboard(THEMES_16, current_theme)

    try:
        await callback.message.edit_text(
            overview_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    except Exception:
        await bot.send_message(
            chat_id=chat_id,
            text=overview_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
