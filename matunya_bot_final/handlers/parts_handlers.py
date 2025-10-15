# handlers/parts_handlers.py
import random
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

# --- ИМПОРТИРУЕМ ВСЕ НУЖНЫЕ ПУЛЫ ФРАЗ ---
from matunya_bot_final.gpt.phrases.parts_choice_phrases import (
    PARTS_CHOICE_PHRASES,
    PART_1_TASK_CHOICE_PHRASES,
    PART_2_TASK_CHOICE_PHRASES
)
# --- ИМПОРТИРУЕМ КЛАВИАТУРЫ ---
from matunya_bot_final.keyboards.inline_keyboards.gpt_parts_keyboard import (
    parts_menu,
    part1_tasks_menu,
    part2_tasks_menu
)

from matunya_bot_final.utils.message_manager import send_tracked_message, cleanup_messages_by_category

__all__ = ("router", "send_parts_choice")

router = Router()

async def send_parts_choice(message: Message, state: FSMContext):
    """Отправляет сообщение с выбором частей ОГЭ."""
    data = await state.get_data()
    gender = data.get("gender")

    student_name = data.get("student_name")
    name_to_use = student_name.strip().capitalize() if student_name else "Друг"

    phrase_template = random.choice(PARTS_CHOICE_PHRASES)
    phrase = phrase_template.format(name=name_to_use)

    if gender == "female":
        phrase = phrase.replace("(а)", "а")
    else:
        phrase = phrase.replace("(а)", "")

    await send_tracked_message(
    bot=message.bot,
    chat_id=message.chat.id,
    state=state,
    text=phrase,
    reply_markup=parts_menu(),
    message_tag="parts_menu",
    category="menus"
)

# =================================================================
# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (ДЛЯ ЭТОГО ФАЙЛА) ---
# =================================================================

async def _send_formatted_message(message: Message, state: FSMContext, phrase_pool: list, keyboard, bot: Bot):
    """
    Универсальный помощник: получает данные, форматирует фразу, УДАЛЯЕТ старое сообщение и ОТПРАВЛЯЕТ новое.
    """
    # --- БЛОК ФОРМАТИРОВАНИЯ (остается без изменений) ---
    data = await state.get_data()
    gender = data.get("gender")
    student_name = data.get("student_name")
    name_to_use = student_name.strip().capitalize() if student_name else "Друг"

    phrase_template = random.choice(phrase_pool)
    phrase = phrase_template.format(name=name_to_use)

    if gender == "female":
        phrase = phrase.replace("(а)", "а")
    else: # male или None
        phrase = phrase.replace("(а)", "")
    # ----------------------------------------------------

    # --- НАША ГЛАВНАЯ ПРАВКА ---
    # 1. Сначала удаляем старое сообщение
    try:
        await message.delete()
    except Exception:
        pass # Игнорируем, если уже удалено

    # 2. Потом отправляем новое
    await send_tracked_message(
    bot=bot,
    chat_id=message.chat.id,
    state=state,
    text=phrase,
    reply_markup=keyboard,
    message_tag="parts_menu",
    category="menus"
    )

# =================================================================
# --- ХЕНДЛЕРЫ ---
# =================================================================

# 🔹 0. Меню выбора части
@router.callback_query(F.data.in_(["menu_gpt_tasks", "gpt_tasks"]))
async def open_gpt_parts(cb: CallbackQuery, state: FSMContext, bot: Bot):
    """Вход в меню выбора частей."""
    await cb.answer()
    await cleanup_messages_by_category(bot, state, cb.from_user.id, "menus")

    await _send_formatted_message(cb.message, state, PARTS_CHOICE_PHRASES, parts_menu(), bot=bot)

# 🔹 1. Часть 1
@router.callback_query(F.data == "part_1")
async def open_part1(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await cb.answer()

    data = await state.get_data()
    student_name = (data.get("student_name") or "Друг").strip().capitalize()
    gender = data.get("gender")
    phrase_template = random.choice(PART_1_TASK_CHOICE_PHRASES)
    phrase = phrase_template.format(name=student_name)
    if gender == "female":
        phrase = phrase.replace("(а)", "а")
    else:
        phrase = phrase.replace("(а)", "")

    await cleanup_messages_by_category(bot, state, cb.from_user.id, "menus")

    await send_tracked_message(
        bot=bot,
        chat_id=cb.message.chat.id,
        state=state,
        text=phrase,
        reply_markup=part1_tasks_menu(),
        message_tag="part1_tasks_menu",
        category="menus"
    )

# 🔹 2. Часть 2
@router.callback_query(F.data == "part_2")
async def open_part2(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await cb.answer()

    data = await state.get_data()
    student_name = (data.get("student_name") or "Друг").strip().capitalize()
    gender = data.get("gender")
    phrase_template = random.choice(PART_2_TASK_CHOICE_PHRASES)
    phrase = phrase_template.format(name=student_name)
    if gender == "female":
        phrase = phrase.replace("(а)", "а")
    else:
        phrase = phrase.replace("(а)", "")

    await cleanup_messages_by_category(bot, state, cb.from_user.id, "menus")

    await send_tracked_message(
        bot=bot,
        chat_id=cb.message.chat.id,
        state=state,
        text=phrase,
        reply_markup=part2_tasks_menu(),
        message_tag="part2_tasks_menu",
        category="menus"
    )
