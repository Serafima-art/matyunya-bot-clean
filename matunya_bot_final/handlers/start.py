# handlers/start.py
from contextlib import suppress
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
import logging

# --- ИСПРАВЛЕННЫЕ ИМПОРТЫ ---
from matunya_bot_final.states.states import NameGenderState
from matunya_bot_final.keyboards.navigation.main_menu import main_inline_menu
from matunya_bot_final.keyboards.inline_keyboards.onboarding.gender_keyboard import gender_keyboard # Новый путь
from matunya_bot_final.keyboards.inline_keyboards.onboarding.onboarding_keyboard import skip_onboarding_keyboard # Новый путь

# Импортируем функции для работы с БД
from matunya_bot_final.utils.db_manager import add_or_update_user, get_user_by_telegram_id

logger = logging.getLogger(__name__)
start_router = Router(name="start")
router = start_router

# 👉 Стартовое сообщение и начало знакомства
@start_router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext, session_maker: async_sessionmaker):
    await state.clear()

    telegram_id = message.from_user.id
    username = message.from_user.full_name or "Пользователь"
    
    async with session_maker() as session:
        user = await add_or_update_user(session, telegram_id, username)
        if user:
            logger.info(f"Пользователь зарегистрирован/найден в БД: {user}")
        else:
            logger.error(f"Ошибка при регистрации пользователя telegram_id={telegram_id}")

    welcome_msg = await message.answer(
        "Привет! Я Матюня — твой добрый репетитор по математике 🧠\n\n"
        "Давай сначала познакомимся!\n\n"
        "Как ты хочешь, чтобы я к тебе обращался?",
        reply_markup=skip_onboarding_keyboard
    )
    await state.update_data(welcome_text_id=welcome_msg.message_id)
    await state.set_state(NameGenderState.waiting_for_name)

# 👉 Обработка кнопки "Можно без имени"
@start_router.callback_query(F.data == "skip_onboarding")
async def skip_onboarding_handler(callback: CallbackQuery, state: FSMContext, session_maker: async_sessionmaker):
    await callback.answer()
    user_data = await state.get_data()
    telegram_id = callback.from_user.id
    # Обновляем профиль в БД через новую функцию, имя — "Друг"
    async with session_maker() as session:
        await add_or_update_user(session, telegram_id, "Друг")

    welcome_msg_id = user_data.get("welcome_text_id")
    if welcome_msg_id:
        with suppress(Exception):
            await callback.bot.delete_message(callback.message.chat.id, welcome_msg_id)

    await callback.message.answer(
        "Хорошо, без проблем! 😊\n\n👇 Выбери, с чего начнём:",
        reply_markup=main_inline_menu
    )
    await state.clear()

# 👉 Приём имени ученика
@start_router.message(NameGenderState.waiting_for_name)
async def save_name_handler(message: Message, state: FSMContext, session_maker: async_sessionmaker):
    name = message.text.strip().capitalize()
    telegram_id = message.from_user.id

    # Обновляем профиль в БД через новую функцию
    async with session_maker() as session:
        await add_or_update_user(session, telegram_id, name)

    # Сохраняем имя в state для приветствия
    await state.update_data(student_name=name)

    gender_msg = await message.answer(
        "А теперь нажми, кто ты — 👧 Девочка или 👦 Мальчик",
        reply_markup=gender_keyboard
    )
    await state.update_data(gender_prompt_id=gender_msg.message_id)
    await state.set_state(NameGenderState.waiting_for_gender)

# 👉 Обработка пола и переход в главное меню
@start_router.callback_query(F.data.startswith("gender_"), NameGenderState.waiting_for_gender)
async def save_gender_handler(callback: CallbackQuery, state: FSMContext, session_maker: async_sessionmaker):
    await callback.answer()
    user_data = await state.get_data()
    name = user_data.get("student_name", "Друг")
    gender = "девочка" if callback.data.split("_")[1] == "female" else "мальчик"
    telegram_id = callback.from_user.id

    # Обновляем профиль в БД, добавляя пол через новую функцию
    async with session_maker() as session:
        await add_or_update_user(session, telegram_id, name, gender=gender)

    # Обновляем пол в FSM для текущей сессии
    await state.update_data(gender=gender)

    # 🧹 Удаляем старые сообщения
    ids_to_delete = [
        user_data.get("welcome_text_id"), 
        user_data.get("gender_prompt_id"), 
        callback.message.message_id
    ]
    for msg_id in ids_to_delete:
        if msg_id:
            with suppress(Exception):
                await callback.bot.delete_message(callback.message.chat.id, msg_id)

    # 👋 Тёплое приветствие
    greeting = f"Приятно познакомиться, {name}! 🌸" if gender == "девочка" else f"Привет, {name}! Рад знакомству 😎"

    await callback.message.answer(
        f"{greeting}\n\n👇 Выбери, с чего начнём:",
        reply_markup=main_inline_menu
    )
    # Состояние очищать не обязательно, т.к. NameGenderState завершился,
    # но можно и очистить, если в `state` больше ничего не нужно.
    # Мы оставим, т.к. там лежат имя и пол.
# 👉 Команда /menu — возвращение в главное меню
@start_router.message(Command("menu"))
async def back_to_main_command(message: Message):
    await message.answer("🏠 Возвращаемся в главное меню!", reply_markup=main_inline_menu)


# 👉 Дополнительная команда для проверки профиля пользователя (для отладки)
@start_router.message(Command("profile"))
async def show_profile(message: Message, session_maker: async_sessionmaker):
    """Показать информацию о пользователе из новой БД"""
    
    telegram_id = message.from_user.id
    
    async with session_maker() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        
        if user:
            profile_text = f"👤 <b>Твой профиль в системе:</b>\n\n"
            profile_text += f"📝 Имя: {user.name or 'Не указано'}\n"
            profile_text += f"🆔 Telegram ID: {user.telegram_id}\n"
            profile_text += f"🔢 ID в системе: {user.id}"
        else:
            profile_text = "❌ Профиль не найден в новой системе. Попробуй команду /start"
    
    await message.answer(profile_text)


# 👉 Команда для проверки статистики БД (для администраторов)
@start_router.message(Command("dbstats"))
async def show_db_stats(message: Message, session_maker: async_sessionmaker):
    """Показать статистику базы данных"""
    
    from matunya_bot_final.utils.db_manager import get_database_stats
    
    async with session_maker() as session:
        stats = await get_database_stats(session)
        
        if stats:
            stats_text = f"📊 <b>Статистика базы данных:</b>\n\n"
            stats_text += f"👥 Пользователей: {stats.get('users_count', 0)}\n"
            stats_text += f"🎯 Типов навыков: {stats.get('skill_types_count', 0)}\n"
            stats_text += f"📝 Задач: {stats.get('tasks_count', 0)}\n"
            stats_text += f"📈 Логов ответов: {stats.get('answer_logs_count', 0)}"
        else:
            stats_text = "❌ Ошибка при получении статистики БД"
    
    await message.answer(stats_text)