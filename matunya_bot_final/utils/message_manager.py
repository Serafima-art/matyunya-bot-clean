# utils/message_manager.py
"""
Система "Интеллектуальная Уборка" - Архитектура "Контейнеров Памяти"
Рефакторинг: переход от простых именных бирок к категорийному управлению сообщениями
"""

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest
from contextlib import suppress
from typing import Optional
from uuid import uuid4

# --- НОВАЯ УТИЛИТА ДЛЯ ПОИСКА ---
async def get_message_id_by_tag(state: FSMContext, tag: str) -> int | None:
    """
    НОВАЯ ВЕРСИЯ: Находит message_id по его уникальной именной бирке (тегу).
    Работает с существующей структурой 'tracked_messages'.
    """
    data = await state.get_data()
    tracked_messages = data.get("tracked_messages", {})

    # Просто ищем тег в основном словаре отслеживания.
    # Этот словарь имеет вид {'тег': ID}
    return tracked_messages.get(tag)

# --- "ВОЛШЕБНАЯ ПАЛОЧКА" №1 ДЛЯ ТЕКСТОВЫХ СООБЩЕНИЙ ---
async def send_tracked_message(
    bot: Bot,
    chat_id: int,
    state: FSMContext,
    text: str,
    message_tag: str,
    reply_markup: InlineKeyboardMarkup = None,
    category: Optional[str] = None,
    parse_mode: Optional[str] = "HTML"
    ) -> Message:
    """
    Отправляет текстовое сообщение с именной биркой и категорийным управлением

    Args:
        bot: Экземпляр бота
        chat_id: ID чата
        state: FSM контекст
        text: Текст сообщения
        message_tag: Уникальная именная бирка для сообщения
        reply_markup: Клавиатура (опционально)
        category: Категория сообщения для группового управления (опционально)

    Returns:
        Отправленное сообщение
    """
    sent_message = await bot.send_message(
    chat_id=chat_id,
    text=text,
    reply_markup=reply_markup,
    parse_mode=parse_mode
    )

    data = await state.get_data()

    # Получаем структуры отслеживания из state
    tracked_messages = data.get("tracked_messages", {})
    message_tags_by_category = data.get("message_tags_by_category", {})

    # Всегда добавляем сообщение в основной словарь отслеживания
    tracked_messages[message_tag] = sent_message.message_id

    # Если указана категория, добавляем тег в соответствующий контейнер
    if category:
        if category not in message_tags_by_category:
            message_tags_by_category[category] = []
        message_tags_by_category[category].append(message_tag)

    # Обновляем state
    await state.update_data(
        tracked_messages=tracked_messages,
        message_tags_by_category=message_tags_by_category
    )

    return sent_message

# --- "ВОЛШЕБНАЯ ПАЛОЧКА" №2 ДЛЯ ФОТОГРАФИЙ ---

async def track_existing_message(
    state: FSMContext,
    message_id: int,
    message_tag: str,
    category: Optional[str] = None,
) -> None:
    """Register already-sent message so cleanup routines can delete it later."""
    data = await state.get_data()
    tracked_messages = data.get("tracked_messages", {})
    message_tags_by_category = data.get("message_tags_by_category", {})

    tracked_messages[message_tag] = message_id

    if category:
        message_tags_by_category.setdefault(category, []).append(message_tag)

    await state.update_data(
        tracked_messages=tracked_messages,
        message_tags_by_category=message_tags_by_category,
    )

async def send_tracked_photo(
    bot: Bot,
    chat_id: int,
    state: FSMContext,
    photo: str | BufferedInputFile,
    message_tag: str,
    caption: str = None,
    category: Optional[str] = None,
    parse_mode: Optional[str] = "HTML" # 1. Добавляем аргумент с HTML по умолчанию
) -> Message:
    """
    Отправляет фото с именной биркой и категорийным управлением

    Args:
        bot: Экземпляр бота
        chat_id: ID чата
        state: FSM контекст
        photo: Фото для отправки
        message_tag: Уникальная именная бирка для сообщения
        caption: Подпись к фото (опционально)
        category: Категория сообщения для группового управления (опционально)

    Returns:
        Отправленное сообщение
    """
    sent_message = await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        parse_mode=parse_mode # 2. Используем переданный аргумент
    )

    data = await state.get_data()

    # Получаем структуры отслеживания из state
    tracked_messages = data.get("tracked_messages", {})
    message_tags_by_category = data.get("message_tags_by_category", {})

    # Всегда добавляем сообщение в основной словарь отслеживания
    tracked_messages[message_tag] = sent_message.message_id

    # Если указана категория, добавляем тег в соответствующий контейнер
    if category:
        if category not in message_tags_by_category:
            message_tags_by_category[category] = []
        message_tags_by_category[category].append(message_tag)

    # Обновляем state
    await state.update_data(
        tracked_messages=tracked_messages,
        message_tags_by_category=message_tags_by_category
    )

    return sent_message

# --- ПРОФЕССИОНАЛЬНАЯ "КЛИНИНГОВАЯ СЛУЖБА" - АРХИТЕКТУРА "КОНТЕЙНЕРОВ ПАМЯТИ" ---

async def cleanup_messages_by_category(bot: Bot, state: FSMContext, chat_id: int, category: str):
    """
    Категорийная очистка: удаляет сообщения определенной категории

    Args:
        bot: Экземпляр бота
        state: FSM контекст
        chat_id: ID чата
        category: Категория сообщений для удаления
    """
    data = await state.get_data()

    tracked_messages = data.get("tracked_messages", {})
    message_tags_by_category = data.get("message_tags_by_category", {})

    # Получаем теги сообщений в указанной категории
    tags_to_remove = message_tags_by_category.get(category, [])

    print(f"--- DEBUG: Категорийная очистка '{category}'. Тегов к удалению: {len(tags_to_remove)}")
    print(f"--- DEBUG: Теги: {tags_to_remove}")

    # Удаляем сообщения по тегам из указанной категории
    for tag in tags_to_remove:
        if tag in tracked_messages:
            message_id = tracked_messages[tag]
            print(f"--- DEBUG: Удаляем сообщение категории '{category}': '{tag}' (ID: {message_id})")

            # Удаляем сообщение
            with suppress(TelegramBadRequest):
                await bot.delete_message(chat_id=chat_id, message_id=message_id)

            # Удаляем запись из основного словаря отслеживания
            del tracked_messages[tag]

    # Очищаем список тегов для данной категории
    if category in message_tags_by_category:
        del message_tags_by_category[category]

    # Обновляем state
    await state.update_data(
        tracked_messages=tracked_messages,
        message_tags_by_category=message_tags_by_category
    )

    print(f"--- DEBUG: Категорийная очистка '{category}' завершена. Осталось сообщений: {len(tracked_messages)}")

async def cleanup_all_messages(bot: Bot, state: FSMContext, chat_id: int):
    """
    Полная очистка: удаляет ВСЕ отслеживаемые сообщения всех категорий

    Args:
        bot: Экземпляр бота
        state: FSM контекст
        chat_id: ID чата
    """
    data = await state.get_data()

    tracked_messages = data.get("tracked_messages", {})

    print(f"--- DEBUG: Полная очистка всех отслеживаемых сообщений. Всего: {len(tracked_messages)}")

    # Удаляем все отслеживаемые сообщения
    for tag, message_id in tracked_messages.items():
        print(f"--- DEBUG: Удаляем сообщение '{tag}' (ID: {message_id})")
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=chat_id, message_id=message_id)

    # Полностью очищаем систему отслеживания в state
    await state.update_data(
        tracked_messages={},
        message_tags_by_category={}
    )

    print(f"--- DEBUG: Полная очистка завершена. Все сообщения удалены.")

# --- LEGACY ФУНКЦИЯ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ ---
async def cleanup_tracked_messages(bot: Bot, chat_id: int, messages_to_delete: list[int]):
    """
    УСТАРЕВШАЯ ФУНКЦИЯ для обратной совместимости
    Используйте cleanup_messages_by_category() или cleanup_all_messages()

    Принимает список ID сообщений и аккуратно удаляет их все.
    Игнорирует ошибки, если сообщение уже было удалено.
    """
    print(f"--- WARNING: Используется устаревшая функция cleanup_tracked_messages")
    print(f"--- DEBUG: Удаляем сообщения с ID: {messages_to_delete}")

    for message_id in messages_to_delete:
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
