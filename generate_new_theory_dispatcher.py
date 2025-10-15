from textwrap import dedent
from pathlib import Path
import difflib
import sys

new_text = dedent('''
# -*- coding: utf-8 -*-
"""
Диспетчеры блока помощи Matunya.

Назначение:
- строим навигацию по уровням подсказок;
- показываем меню помощи пользователю;
- очищаем служебные сообщения через MessageManager.

Файл: help_core/dispatchers/theory_dispatcher.py
"""

import logging
import random
import asyncio
from contextlib import suppress
from typing import Dict, Any, Optional

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from help_core.repository.theory_repository import get_help_data
from help_core.renderers.phrases import get_random_phrase
from utils.message_manager import send_tracked_message, cleanup_messages_by_category

# Логгер модуля
logger = logging.getLogger(__name__)

# Роутер для обработчиков помощи
theory_router = Router(name="theory_dispatcher")


# ========== Навигация по подсказкам ==========

def get_help_navigation_keyboard(next_level: Optional[str], task_subtype: str) -> InlineKeyboardMarkup:
    """Формирует навигационную клавиатуру для статических подсказок."""
    try:
        builder = InlineKeyboardBuilder()

        # Добавляем кнопку перехода к следующему уровню помощи
        if next_level:
            level_names = {
                "hint": "Подсказка",
                "partial": "Частичное решение",
                "step": "Пошаговый разбор",
                "solution": "Полное решение",
            }

            next_level_name = level_names.get(next_level, "Следующий уровень")

            builder.row(
                InlineKeyboardButton(
                    text=f"➡️ {next_level_name}",
                    callback_data=f"select_help_level:{task_subtype}:{next_level}"
                )
            )

        # Кнопка сворачивания меню помощи
        builder.row(
            InlineKeyboardButton(
                text="🚫 Скрыть помощь",
                callback_data=f"hide_help:{task_subtype}"
            )
        )

        return builder.as_markup()

    except Exception as e:
        logger.error(f"Не удалось построить клавиатуру навигации: {e}")
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🚫 Скрыть помощь",
                callback_data=f"hide_help:{task_subtype}"
            )
        ]])


def get_next_static_level(current_level: str) -> Optional[str]:
    """Возвращает следующий уровень статической помощи."""
    level_progression = {
        "hint": "partial",
        "partial": "step",
        "step": "solution",
    }

    return level_progression.get(current_level)


@theory_router.callback_query(F.data.startswith("request_help:"))
async def handle_help_request(callback: CallbackQuery, bot: Bot):
    """Показывает меню помощи в ответ на нажатие кнопки "🆘 Помощь"."""
    try:
        print(f"[DEBUG] Получен callback: {callback.data}")
        logger.info(f"Получен запрос меню помощи: {callback.data}")

        # Разбираем callback_data
        data_parts = callback.data.split(":")
        if len(data_parts) < 2:
            logger.error(f"Некорректный формат callback_data: {callback.data}")
            await callback.message.edit_text(
                "⚠️ <b>Ошибка</b>\n\nНе удалось обработать запрос помощи.",
                parse_mode="HTML"
            )
            return

        action = data_parts[0]
        task_subtype = data_parts[1]
        task_type = data_parts[2] if len(data_parts) > 2 else "11"

        logger.info(f"Отправляем меню помощи для задания {task_type}/{task_subtype}")

        help_menu_text = create_help_menu_text(task_type, task_subtype)
        help_menu_keyboard = create_help_menu_keyboard(task_subtype, task_type)

        try:
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=help_menu_text,
                parse_mode="HTML",
                reply_markup=help_menu_keyboard,
            )
            # Деактивируем клавиатуру у исходного сообщения
            with suppress(TelegramBadRequest):
                await callback.message.edit_reply_markup(reply_markup=None)
            logger.info(f"Меню помощи отправлено для {task_type}/{task_subtype}")

        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                logger.debug("Меню помощи уже соответствует актуальному состоянию")
            else:
                logger.error(f"Ошибка при отправке меню помощи: {e}")
                raise

    except Exception as e:
        logger.error(f"Сбой в handle_help_request: {e}")

        try:
            error_text = (
                "⚠️ <b>Произошла ошибка</b>\n\n"
                "Не удалось показать меню помощи.\n"
                "Попробуйте ещё раз чуть позже."
            )

            await callback.message.edit_text(
                error_text,
                parse_mode="HTML"
            )

        except Exception as edit_error:
            logger.error(f"Не удалось показать текст ошибки: {edit_error}")

    finally:
        # Завершаем callback, чтобы убрать «часики»
        with suppress(TelegramBadRequest):
            await callback.answer()


def create_help_menu_text(task_type: str, task_subtype: str) -> str:
    """Возвращает текст для меню помощи."""
    return (
        "🆘 <b>Меню помощи</b>\n\n"
        f"📘 <b>Тип задания:</b> №{task_type}\n"
        f"🔖 <b>Подтип:</b> {task_subtype}\n\n"
        "🪜 <b>Доступные уровни:</b>\n\n"
        "🔹 <b>Подсказка</b> — короткий намёк на решение\n"
        "🔹 <b>Частичное решение</b> — раскрываем ключевую идею\n"
        "🔹 <b>Пошаговый разбор</b> — объясняем последовательность действий\n"
        "🔹 <b>Полное решение</b> — итоговый ответ с пояснениями\n\n"
        "Выберите нужный вариант ниже 👇"
    )


def create_help_menu_keyboard(task_subtype: str, task_type: str) -> InlineKeyboardMarkup:
    """Строит клавиатуру с уровнями помощи."""
    builder = InlineKeyboardBuilder()

    # Кнопки уровней помощи (по две в строке)
    help_levels = [
        ("💡 Подсказка", "hint"),
        ("🧩 Частичное решение", "partial"),
        ("🪜 Пошаговый разбор", "step"),
        ("✅ Полное решение", "solution"),
    ]

    for i in range(0, len(help_levels), 2):
        row_buttons = []

        for j in range(2):
            if i + j < len(help_levels):
                emoji_text, level = help_levels[i + j]

                button = InlineKeyboardButton(
                    text=emoji_text,
                    callback_data=f"select_help_level:{task_subtype}:{level}:{task_type}"
                )
                row_buttons.append(button)

        builder.row(*row_buttons)

    # Кнопка для связи с наставником
    builder.row(
        InlineKeyboardButton(
            text="❓ Задать вопрос",
            callback_data=f"ask_question:{task_subtype}:{task_type}"
        )
    )

    return builder.as_markup()


@theory_router.callback_query(F.data.startswith("select_help_level:"))
async def handle_static_help_level(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Отправляет контент выбранного уровня статической помощи."""
    try:
        await callback.answer()

        # Разбираем callback_data
        data_parts = callback.data.split(":")
        if len(data_parts) < 3:
            logger.error(f"Некорректный формат callback_data: {callback.data}")
            return

        action = data_parts[0]
        task_subtype = data_parts[1]
        current_level = data_parts[2]
        task_type = data_parts[3] if len(data_parts) > 3 else "11"

        logger.info(
            f"Запрошен уровень помощи {current_level} для задания {task_type}/{task_subtype}"
        )

        # Допускаем только статические уровни
        static_levels = ["hint", "partial", "step"]
        if current_level not in static_levels:
            logger.warning(f"Уровень {current_level} недоступен, пропускаем запрос")
            return

        # Отправляем связующую фразу
        connecting_phrase = get_random_phrase(current_level)

        try:
            await send_tracked_message(
                bot=bot,
                chat_id=callback.message.chat.id,
                state=state,
                text=connecting_phrase,
                message_tag=f"help_phrase_{current_level}_{task_subtype}",
                category=f"help_{task_subtype}"
            )

            logger.debug(f"Отправили переходную фразу для уровня {current_level}")

        except Exception as e:
            logger.warning(f"Не удалось отправить переходную фразу: {e}")

        # Получаем данные помощи из репозитория
        try:
            task_type_int = int(task_type)
            help_data = await get_help_data(task_type_int, task_subtype)

            if not help_data:
                logger.warning(
                    f"Данные помощи не найдены для {task_type}/{task_subtype}"
                )
                await send_help_unavailable_message(callback, task_type, task_subtype)
                return

        except Exception as e:
            logger.error(f"Ошибка при загрузке данных помощи: {e}")
            await send_help_unavailable_message(callback, task_type, task_subtype)
            return

        # Извлекаем контент выбранного уровня
        level_data = help_data.get("levels", {}).get(current_level, {})
        variants = level_data.get("variants", [])

        if not variants:
            logger.warning(f"Нет вариантов подсказок для уровня {current_level}")
            await send_help_unavailable_message(callback, task_type, task_subtype)
            return

        selected_variant = random.choice(variants)
        next_level = get_next_static_level(current_level)
        navigation_keyboard = get_help_navigation_keyboard(next_level, task_subtype)

        level_name = level_data.get("name", current_level.title())
        help_text = f"🧠 <b>{level_name}</b>\n\n{selected_variant}"

        try:
            await send_tracked_message(
                bot=bot,
                chat_id=callback.message.chat.id,
                state=state,
                text=help_text,
                message_tag=f"help_content_{current_level}_{task_subtype}",
                reply_markup=navigation_keyboard,
                category=f"help_{task_subtype}"
            )

            logger.info(f"Показан контент уровня {current_level}")

        except Exception as e:
            logger.error(f"Ошибка при отправке контента уровня: {e}")

        await state.update_data({
            "task_type": task_type,
            "task_subtype": task_subtype,
            "current_level": current_level,
            "help_active": True,
        })

    except Exception as e:
        logger.error(f"Сбой в handle_static_help_level: {e}")


@theory_router.callback_query(F.data.startswith("hide_help:"))
async def handle_hide_help(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Скрывает подсказки и очищает служебные сообщения."""
    try:
        await callback.answer("Секундочку, убираю помощь…")

        # Разбираем callback_data
        data_parts = callback.data.split(":")
        task_subtype = data_parts[1] if len(data_parts) > 1 else ""

        logger.info(f"Пользователь закрыл помощь для {task_subtype}")

        # Очищаем tracked-сообщения категории help_*
        try:
            await cleanup_messages_by_category(
                bot=bot,
                state=state,
                chat_id=callback.message.chat.id,
                category=f"help_{task_subtype}"
            )
            logger.info(f"Сообщения категории help_{task_subtype} удалены")
        except Exception as e:
            logger.error(
                f"Ошибка при удалении сообщений help_{task_subtype}: {e}"
            )

        # Уведомляем пользователя
        try:
            success_message = await bot.send_message(
                chat_id=callback.message.chat.id,
                text="✅ <b>Помощь скрыта</b>\n\nЕсли нужно, откройте меню ещё раз.",
                parse_mode="HTML"
            )

            asyncio.create_task(
                delete_message_after_delay(
                    bot,
                    callback.message.chat.id,
                    success_message.message_id,
                    3,
                )
            )

        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление о скрытии помощи: {e}")

        await state.update_data({
            "help_active": False,
            "current_level": None,
        })

        logger.info(f"Состояние помощи сброшено для {task_subtype}")

    except Exception as e:
        logger.error(f"Сбой в handle_hide_help: {e}")

        try:
            await callback.message.edit_text(
                "⚠️ Не получилось скрыть подсказки.\nПопробуйте повторить позже.",
                parse_mode="HTML"
            )
        except Exception:
            pass


# ========== Служебные уведомления ==========

async def send_help_unavailable_message(callback: CallbackQuery, task_type: str, task_subtype: str):
    """Отправляет уведомление об отсутствии подсказок."""
    unavailable_text = (
        "😔 <b>Подсказки временно недоступны</b>\n\n"
        f"📘 Задание №<b>{task_type}</b> (<b>{task_subtype}</b>)\n\n"
        "Пока что для этого задания нет готовых подсказок.\n"
        "Мы уже работаем над их подготовкой!"
    )

    try:
        await callback.message.edit_text(
            unavailable_text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(
            f"Ошибка при показе уведомления об отсутствии подсказок: {e}"
        )


async def delete_message_after_delay(bot: Bot, chat_id: int, message_id: int, delay_seconds: int):
    """Удаляет сервисное сообщение после задержки."""
    try:
        await asyncio.sleep(delay_seconds)
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.debug(
            f"Удалили сервисное сообщение {message_id} через {delay_seconds} с."
        )
    except Exception as e:
        logger.debug(f"Не удалось удалить сервисное сообщение: {e}")


# ========== Экспорт ==========

__all__ = [
    "theory_router",
    "get_help_navigation_keyboard",
    "handle_static_help_level",
    "handle_hide_help",
]


# ========== Тестирование ==========

async def _test_static_help():
    """Простой тест для проверки статических подсказок."""
    print("🧪 Проверяем статические подсказки...")

    keyboard = get_help_navigation_keyboard("partial", "match_signs_a_c")
    print(f"ℹ️ Кнопок в клавиатуре: <b>{len(keyboard.inline_keyboard)}</b>")

    for level in ["hint", "partial", "step"]:
        next_level = get_next_static_level(level)
        print(f"➡️ Для уровня <b>{level}</b> следующий: <b>{next_level}</b>")

    from help_core.renderers.phrases import get_random_phrase
    for level in ["hint", "partial", "step"]:
        phrase = get_random_phrase(level)
        print(f"💬 Фраза для <b>{level}</b>: {phrase}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(_test_static_help())
''').lstrip('\n')

original_path = Path('matunya_bot_final/help_core/dispatchers/theory_dispatcher.py')
original_text = original_path.read_text(encoding='utf-8', errors='ignore')
if original_text.startswith('\ufeff'):
    original_text = original_text[1:]

diff = difflib.unified_diff(
    original_text.splitlines(keepends=True),
    new_text.splitlines(keepends=True),
    fromfile='a/matunya_bot_final/help_core/dispatchers/theory_dispatcher.py',
    tofile='b/matunya_bot_final/help_core/dispatchers/theory_dispatcher.py'
)

sys.stdout.buffer.write(''.join(diff).encode('utf-8'))
