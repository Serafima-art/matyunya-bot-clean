"""
Универсальный хендлер для обработки ответов пользователей на задачи
Работает с любыми типами задач, чьи task_ids сохранены в state
ДОБАВЛЕНА гибридная архитектура: сохранение деталей только для ошибочных задач
"""
import logging
import json
import random
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

# --- ИСПРАВЛЕННЫЕ И УПОРЯДОЧЕННЫЕ ИМПОРТЫ ---
from matunya_bot_final.states.states import TaskState
from matunya_bot_final.utils.db_manager import get_task_by_id, log_answer, get_user_id_by_telegram_id
from matunya_bot_final.utils.message_manager import (
    send_tracked_message,
    cleanup_messages_by_category,
    get_message_id_by_tag,
    track_existing_message,
)
from matunya_bot_final.utils.answer_utils import answers_equal
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import build_overview_keyboard
from matunya_bot_final.gpt.phrases.tasks.correct_answer_feedback import get_random_feedback
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
# ---------------------------------------------

logger = logging.getLogger(__name__)
router = Router()


@router.message(TaskState.waiting_for_answer, F.text)
async def process_user_answer(message: Message, state: FSMContext, session_maker: async_sessionmaker):
    """
    Универсальный хендлер для обработки ответов пользователей на задачи.
    ГИБРИДНАЯ АРХИТЕКТУРА: Сохраняет полные детали только для ошибочных задач

    Логика:
    1. Получает данные из state (current_task_index, task_ids)
    2. Извлекает эталонный ответ из БД
    3. Проверяет ответ пользователя
    4. Если ответ НЕПРАВИЛЬНЫЙ - собирает детали задачи в JSON
    5. Логирует результат в базу данных (с деталями для ошибок)
    6. Предоставляет обратную связь пользователю
    """

    await track_existing_message(
        state=state,
        message_id=message.message_id,
        message_tag=f"user_answer_{message.message_id}",
        category="user_answers"
    )

    user_answer = message.text.strip()
    telegram_id = message.from_user.id

    logger.info(f"📝 ANSWER HANDLER: Обрабатываем ответ от user {telegram_id}: '{user_answer}'")

    try:
        # 1. ПОЛУЧЕНИЕ ДАННЫХ ИЗ STATE
        user_data = await state.get_data()
        current_task_index = user_data.get("current_task_index", 0)
        task_ids = user_data.get("task_ids", [])
        task_type = user_data.get("task_type", "unknown")
        task_subtype = user_data.get("task_subtype", "unknown")

        if not task_ids:
            # Это не наши данные (возможно, пользователь решает задачу 6 или 8)
            # Просто выходим, чтобы дать сработать следующему хендлеру
            return

        if current_task_index >= len(task_ids):
            logger.error(f"❌ ANSWER HANDLER: Неверный индекс задачи: {current_task_index} >= {len(task_ids)}")
            await message.answer("❌ Ошибка: номер задачи некорректен.")
            return

        current_task_id = task_ids[current_task_index]

        if current_task_id is None:
            logger.error(f"❌ ANSWER HANDLER: task_id для индекса {current_task_index} равен None")
            await message.answer("❌ Ошибка: задача не зарегистрирована в системе.")
            return

        logger.info(f"🎯 ANSWER HANDLER: Проверяем ответ для задачи ID={current_task_id}, индекс={current_task_index}")

        async with session_maker() as session:
            # 2. ПОЛУЧЕНИЕ ЭТАЛОНА ИЗ БД
            task_obj = await get_task_by_id(session, current_task_id)

            if not task_obj:
                logger.error(f"❌ ANSWER HANDLER: Задача ID={current_task_id} не найдена в БД")
                await message.answer("❌ Ошибка: задача не найдена в базе данных.")
                return

            correct_answer = task_obj.answer
            logger.info(f"📋 ANSWER HANDLER: Эталонный ответ: '{correct_answer}'")

            # 3. ПРОВЕРКА ОТВЕТА
            is_correct = answers_equal(user_answer, correct_answer)
            logger.info(f"🔍 ANSWER HANDLER: Ответ {'ПРАВИЛЬНЫЙ' if is_correct else 'НЕПРАВИЛЬНЫЙ'}")

            # 4. ПОЛУЧЕНИЕ ВНУТРЕННЕГО USER_ID
            user_id = await get_user_id_by_telegram_id(session, telegram_id)

            if not user_id:
                logger.error(f"❌ ANSWER HANDLER: Пользователь telegram_id={telegram_id} не найден в БД")
                await message.answer("❌ Ошибка: пользователь не найден в системе.")
                return

            # 5. ГИБРИДНАЯ АРХИТЕКТУРА: Собираем детали только для ошибочных задач
            generated_task_details = None

            if not is_correct:
                # Собираем полную информацию об ошибочной задаче
                task_package = user_data.get("task_package", {})
                tasks = task_package.get("tasks", [])

                if tasks and current_task_index < len(tasks):
                    current_task_data = tasks[current_task_index]
                    plot_data = task_package.get("plot_data", {})

                    # Формируем JSON с полными данными задачи
                    task_details = {
                        "generated_text": current_task_data.get("text", ""),
                        "correct_answer": correct_answer,
                        "plot_data": plot_data,
                        "task_metadata": {
                            "skill_source_id": current_task_data.get("id", "unknown"),
                            "theme": task_subtype,
                            "task_type": task_type,
                            "generation_timestamp": datetime.utcnow().isoformat()
                        },
                        "additional_data": {
                            "intro": task_package.get("intro", ""),
                            "condition": task_package.get("condition", ""),
                            "table_html": task_package.get("table_html", "")
                        }
                    }

                    generated_task_details = json.dumps(task_details, ensure_ascii=False)
                    logger.info(f"💾 ANSWER HANDLER: Сохраняем детали ошибочной задачи (размер: {len(generated_task_details)} символов)")
                else:
                    logger.warning("⚠️ ANSWER HANDLER: Не удалось получить данные задачи для сохранения деталей")

            # 6. ЛОГИРОВАНИЕ РЕЗУЛЬТАТА с гибридной архитектурой
            answer_log = await log_answer(
                session=session,
                user_id=user_id,
                task_id=current_task_id,
                is_correct=is_correct,
                user_answer=user_answer,
                generated_task_details=generated_task_details  # Детали только для ошибок
            )

            if answer_log:
                if generated_task_details:
                    logger.info(f"📊 ANSWER HANDLER: Лог ошибочного ответа сохранен с деталями (ID={answer_log.id})")
                else:
                    logger.info(f"📊 ANSWER HANDLER: Лог правильного ответа сохранен (ID={answer_log.id})")
            else:
                logger.warning("⚠️ ANSWER HANDLER: Не удалось сохранить лог ответа")

        # 7. ОБРАТНАЯ СВЯЗЬ ПОЛЬЗОВАТЕЛЮ
        if is_correct:
            await _handle_correct_answer(message, state, current_task_index, user_answer)
        else:
            await _handle_incorrect_answer(message, state)

    except Exception as e:
        logger.error(f"❌ ANSWER HANDLER: Критическая ошибка при обработке ответа: {e}")
        import traceback
        traceback.print_exc()

        await message.answer(
            "❌ Произошла ошибка при проверке ответа. Попробуйте еще раз или обратитесь к администратору."
        )


async def _handle_correct_answer(message: Message, state: FSMContext, current_task_index: int, user_answer: str):
    """
    ПЛАН Б: Обрабатывает правильный ответ. Надежно, но просто.
    Удаляет старый пульт и присылает новый.
    """
    logger.info(f"✅ ПЛАН Б: Обрабатываем ПРАВИЛЬНЫЙ ответ для задачи {current_task_index + 1}")
    bot = message.bot
    chat_id = message.chat.id
    user_data = await state.get_data()

    # --- 1. Редактируем сообщение с заданием (это работает отлично) ---
    task_package = user_data.get("task_package", {})
    tasks = task_package.get("tasks", [])
    if not tasks or current_task_index >= len(tasks):
        logger.error("❌ ПЛАН Б: Не найдены задачи.")
        return
    task = tasks[current_task_index]
    task_text = task.get('text', 'Текст задания не найден')
    new_text = (
        f"<b>Задание {current_task_index + 1}:</b>\n{task_text}\n\n"
        f"<i>Ответ: ✅ <b>{user_answer}</b></i>"
    )
    from matunya_bot_final.utils.message_manager import get_message_id_by_tag
    task_message_id = await get_message_id_by_tag(state, f"focused_task_{current_task_index + 1}")
    if task_message_id:
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=task_message_id, text=new_text)
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=task_message_id, reply_markup=None)
        except Exception:
            pass

    # --- 2. Обновляем состояние ---
    solved_tasks_indices = user_data.get("solved_tasks_indices", [])
    if current_task_index not in solved_tasks_indices:
        solved_tasks_indices.append(current_task_index)
        await state.update_data(solved_tasks_indices=solved_tasks_indices)

    # Чистим ВСЕ старые меню и уведомления
    await cleanup_messages_by_category(bot, state, chat_id, "menus")
    await cleanup_messages_by_category(bot, state, chat_id, "notifications")

    # Собираем новую клавиатуру
    task_ids = user_data.get("task_ids", [])
    subtype_key = user_data.get("task_subtype", "tires")
    overview_keyboard = build_overview_keyboard(len(task_ids), subtype_key, solved_indices=solved_tasks_indices)

    # Собираем новый текст
    student_name = user_data.get("student_name")
    gender = user_data.get("gender")
    feedback_text = get_random_feedback(name=student_name, gender=gender)
    new_overview_text = (
        f"{feedback_text}\n\n"
        f"👇 Выбери следующее задание или вернись в меню."
    )

    # ОТПРАВЛЯЕМ НОВЫЙ ПУЛЬТ И СНОВА РЕГИСТРИРУЕМ ЕГО
    unique_overview_tag = f"overview_keyboard_{chat_id}"
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=new_overview_text,
        reply_markup=overview_keyboard,
        message_tag=unique_overview_tag,
        category="menus"
    )
    await state.update_data(current_overview_tag=unique_overview_tag)
    logger.info("✅ ПЛАН Б: Старый пульт удален, новый отправлен и зарегистрирован.")

    # --- 4. Проверяем, не решены ли все задачи ---
    if len(solved_tasks_indices) == len(task_ids):
        await _handle_all_tasks_solved(message, state)


async def _handle_incorrect_answer(message: Message, state: FSMContext):
    """
    НОВАЯ ЛОГИКА V3.0: Обрабатывает неправильный ответ, предлагая помощь.
    ОТЛАЖЕНО: Правильно формирует TaskCallback для кнопки помощи.
    """
    logger.info(f"❌ V3.0: Обрабатываем НЕПРАВИЛЬНЫЙ ответ")

    # --- НАШЕ ИСПРАВЛЕНИЕ ---
    # 1. Достаем нужные данные из state
    user_data = await state.get_data()
    subtype_key = user_data.get("task_subtype", "unknown")
    current_task_index = user_data.get("current_task_index", 0)

    help_keyboard = InlineKeyboardBuilder()

    # 3. Правильно формируем CallbackData со ВСЕМИ обязательными полями
    help_keyboard.button(
        text="🆘 Помощь",
        callback_data=TaskCallback(
            action="request_help",
            subtype_key=subtype_key,
            question_num=current_task_index + 1,
            task_type=current_task_index + 1,
        ).pack()
    )
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

    # Отправляем временное сообщение, которое потом будет удалено
    await send_tracked_message(
        bot=message.bot,
        chat_id=message.chat.id,
        state=state,
        text="❌ Не совсем так. Попробуй еще раз или воспользуйся подсказкой!",
        reply_markup=help_keyboard.as_markup(),
        message_tag="incorrect_answer_prompt",
        category="dialog_messages"
    )


async def _handle_all_tasks_solved(message: Message, state: FSMContext):
    """
    ФИНАЛЬНАЯ ВЕРСИЯ V3.0: Запускается, когда все 5 заданий решены.
    - Добавлена защита от повторной отправки.
    - Утвержденная клавиатура 1+2.
    """
    # --- 1. ЗАЩИТА ОТ ПОВТОРНОГО ВЫЗОВА ---
    user_data = await state.get_data()
    if user_data.get("session_completed"):
        logger.info("🏁 Сессия уже была завершена. Финальное сообщение не отправляется повторно.")
        return

    await state.update_data(session_completed=True)

    logger.info("🎉 ФИНАЛ: Все 5 заданий решены! Запускаем финальную сцену.")
    bot = message.bot
    chat_id = message.chat.id

    # --- 3. Генерируем "живое" поздравление ---
    final_text = (
        "🎉🎉🎉 **ПОБЕДА!** 🎉🎉🎉\n\n"
        "Ты просто brilliantly справился со всеми заданиями! Это было великолепно!\n\n"
        "Каждый правильный ответ — это шаг к твоей уверенной пятерке на ОГЭ. "
        "Продолжай в том же духе, и результат не заставит себя ждать!"
    )
    subtype_key = user_data.get("task_subtype", "tires")

    final_keyboard = InlineKeyboardBuilder()

    # Ряд 1: Основное действие
    final_keyboard.button(
        text="💪 Решить еще один вариант!",
        callback_data=TaskCallback(action="1-5_select_subtype", subtype_key=subtype_key).pack()
    )

    # Ряд 2: Навигация
    final_keyboard.button(
        text="↩️ Другой подтип",
        callback_data=TaskCallback(action="show_task_1_5_carousel").pack()
    )
    final_keyboard.button(
        text="🔝 В главное меню",
        callback_data="back_to_main"
    )

    # Располагаем кнопки по схеме 1 - 2
    final_keyboard.adjust(1, 2)
    # --- КОНЕЦ БЛОКА С КЛАВИАТУРОЙ ---

    # --- 5. Отправляем финальное сообщение ---
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=final_text,
        reply_markup=final_keyboard.as_markup(),
        message_tag="final_victory_message",
        category="final_screen"
    )

    logger.info("🏁 Финальная сцена отправлена. Состояние сохранено.")

