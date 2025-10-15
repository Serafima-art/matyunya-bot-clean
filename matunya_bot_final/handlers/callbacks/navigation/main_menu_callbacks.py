# handlers/callbacks/navigation/main_menu_handler.py
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

# --- ИМПОРТЫ ПОСЛЕ "УБОРКИ" ---
# Импортируем только то, что действительно нужно этому файлу
from matunya_bot_final.keyboards.navigation.main_menu import main_inline_menu
from matunya_bot_final.keyboards.inline_keyboards.help_menu_keyboard import help_menu_keyboard #Переместить в keyboards/navigation/
from matunya_bot_final.utils.message_manager import cleanup_all_messages
from matunya_bot_final.handlers import parts_handlers
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.keyboards.navigation.navigation import main_only_kb, back_and_main_kb

router = Router(name="main_menu_handler")

# 🏠 ЕДИНЫЙ УНИВЕРСАЛЬНЫЙ обработчик для возврата в Главное Меню
@router.callback_query(
    F.data.in_({
        "back_to_main_menu",
        "to_main_menu",
        "back_to_main"
    })
)
async def back_to_main_menu_universal_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    ЕДИНЫЙ УНИВЕРСАЛЬНЫЙ обработчик для возврата в Главное Меню.
    Очищает все сообщения и состояние.
    """
    await callback.answer()

    # Сначала удаляем сообщение с кнопкой "В главное меню"
    try:
        await callback.message.delete()
    except Exception:
        pass # Игнорируем, если уже удалено

    # Вызываем генеральную уборку всех отслеживаемых сообщений
    await cleanup_all_messages(bot=bot, state=state, chat_id=callback.from_user.id)

    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="🏠 Снова в главном меню!\n\nВыбирай, с чего начнём:",
        reply_markup=main_inline_menu
    )

    await state.clear()

# -----------------------------------------------------------------------------
# ⬅️ ВОЗВРАТ К ВЫБОРУ ЧАСТЕЙ ОГЭ (ИЗ ЛЮБОГО МЕСТА)
# -----------------------------------------------------------------------------
@router.callback_query(F.data == "back_to_parts")
async def back_to_parts_handler(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Обрабатывает нажатие кнопки "⬅️ Назад" из любой точки бота.

    🔹 Что делает:
    1. Удаляет текущее сообщение (например, карусель или задание).
    2. Полностью очищает чат от отслеживаемых сообщений (Генеральная уборка).
    3. Показывает экран выбора частей ОГЭ (Часть 1 / Часть 2).

    📦 Эта функция вызывается автоматически при нажатии кнопки из back_and_main_kb().
    """
    await callback.answer()

    # 1️⃣ Удаляем текущее сообщение с кнопкой "Назад"
    try:
        await callback.message.delete()
    except Exception:
        pass  # Если уже удалено — просто игнорируем

    # 2️⃣ Генеральная уборка — удаляем все отслеживаемые сообщения текущей сессии
    await cleanup_all_messages(bot=bot, state=state, chat_id=callback.from_user.id)

    # 3️⃣ Показываем экран выбора частей (Часть 1 / Часть 2)
    await parts_handlers.send_parts_choice(callback.message, state)

# 📤 Загрузить своё задание
@router.callback_query(F.data == "menu_upload_task")
async def upload_custom_task_callback(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(
        "📤 <b>Загрузить своё задание:</b>\n\n"
        "Просто отправь текст задания или загрузи фото/скрин, и я постараюсь помочь тебе его решить 🧮",
        reply_markup=main_only_kb()
    )

@router.callback_query(F.data == "menu_progress")
async def progress_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await callback.message.edit_text(
        "📊 Раздел 'Мой прогресс' находится в разработке.\n\n"
        "Скоро здесь можно будет увидеть подробную статистику по решенным заданиям! 📈",
        reply_markup=main_only_kb()
    )

# 💬 Болтовня (заглушка)
# 🤝 Помощь — переход к меню помощи
@router.callback_query(F.data == "menu_help")
async def open_help_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🤝 <b>Помощь:</b>\n\n"
        "👇 Выбери, что тебе нужно:",
        reply_markup=help_menu_keyboard
    )

# --- Обработчики для подменю "Помощь" ---

@router.callback_query(F.data == "help_how_to_use")
async def help_how_to_use_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💡 <b>Как пользоваться ботом:</b>\n\n"
        "1. Выбирай разделы в главном меню.\n"
        "2. Тренируйся на заданиях и используй подсказки.\n"
        "3. Следи за своим прогрессом в разделе 📊.\n\n"
        "Матюня всегда рядом, чтобы помочь! 🧮",
        reply_markup=help_menu_keyboard
    )

@router.callback_query(F.data == "help_how_it_works")
async def help_how_it_works_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🧭 <b>Как проходит обучение с Матюней:</b>\n\n"
        "Все задания созданы на основе структуры и стиля ОГЭ по математике и максимально приближены к сборнику Ященко 2025.\n\n"
        "Если у тебя есть конкретное задание из сборника — просто отправь его, и я помогу разобраться! ❤️",
        reply_markup=help_menu_keyboard
    )

@router.callback_query(F.data == "help_contact_teacher")
async def help_contact_teacher_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📲 <b>Связь с живым репетитором:</b>\n\n"
        "Если тебе или твоим родителям нужна личная консультация, напиши сюда:\n\n"
        "<i>📧 [почта]</i> или <i>📱 Telegram: [контакт]</i>",
        reply_markup=help_menu_keyboard
    )
