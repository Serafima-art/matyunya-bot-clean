"""
Универсальный хендлер для обработки ответов пользователей на задачи 1–5.
Работает с любыми типами задач, чьи task_ids сохранены в state.

✅ ГИБРИДНАЯ архитектура:
- полные детали задачи сохраняем ТОЛЬКО при ошибке (generated_task_details),
- при верном ответе логируем без тяжёлого JSON.

✅ UX:
- при верном ответе показываем отдельный "кадр результата" (notifications)
- и отправляем новый "пульт выбора заданий" (menus) с отмеченными решёнными.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from matunya_bot_final.states.states import TaskState
from matunya_bot_final.utils.db_manager import (
    get_task_by_id,
    get_user_id_by_telegram_id,
    log_answer,
)
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    get_message_id_by_tag,
    send_tracked_message,
    track_existing_message,
)
from matunya_bot_final.utils.answer_utils import answers_equal
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_1_5.after_task_1_5_keyboard import (
    build_overview_keyboard,
)
from matunya_bot_final.gpt.phrases.tasks.correct_answer_feedback import get_random_feedback
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.utils.fsm_guards import ensure_task_index

logger = logging.getLogger(__name__)
router = Router()


@router.message(TaskState.waiting_for_answer, F.text)
async def process_user_answer(message: Message, state: FSMContext, session_maker: async_sessionmaker):
    """
    1) Берём данные из state: current_task_index, task_ids, task_package и т.д.
    2) Берём эталонный ответ из БД по task_id
    3) Сравниваем ответ
    4) Пишем лог (и детали ТОЛЬКО при ошибке)
    5) UX: верно -> отдельный кадр результата + новый пульт / неверно -> кнопка помощи
    """

    # Трекаем сообщение пользователя (ответ)
    await track_existing_message(
        state=state,
        message_id=message.message_id,
        message_tag=f"user_answer_{message.message_id}",
        category="user_answers",
    )

    user_answer = (message.text or "").strip()
    telegram_id = message.from_user.id if message.from_user else None

    logger.info(f"📝 ANSWER HANDLER: Ответ от telegram_id={telegram_id}: '{user_answer}'")

    try:
        user_data = await state.get_data()

        current_task_index: int = int(user_data.get("current_task_index", 0))
        task_ids: List[int] = user_data.get("task_ids", []) or []
        task_type: str = user_data.get("task_type", "unknown")
        task_subtype: str = user_data.get("task_subtype", "unknown")

        # Если это не сессия 1–5 (или state пустой) — даём сработать другим хендлерам
        if not task_ids:
            return

        if current_task_index < 0 or current_task_index >= len(task_ids):
            logger.error(
                f"❌ ANSWER HANDLER: Некорректный current_task_index={current_task_index}, len(task_ids)={len(task_ids)}"
            )
            await message.answer("❌ Ошибка: номер задачи некорректен.")
            return

        current_task_id = task_ids[current_task_index]
        if current_task_id is None:
            logger.error(f"❌ ANSWER HANDLER: task_id=None для индекса {current_task_index}")
            await message.answer("❌ Ошибка: задача не зарегистрирована в системе.")
            return

        logger.info(f"🎯 ANSWER HANDLER: Проверяем task_id={current_task_id}, index={current_task_index}")

        async with session_maker() as session:
            # 1) Берём задачу из БД
            task_obj = await get_task_by_id(session, current_task_id)
            if not task_obj:
                logger.error(f"❌ ANSWER HANDLER: task_id={current_task_id} не найден в БД")
                await message.answer("❌ Ошибка: задача не найдена в базе данных.")
                return

            correct_answer = task_obj.answer
            logger.info(f"📋 ANSWER HANDLER: Эталон: '{correct_answer}'")

            # 2) Сравнение
            is_correct = answers_equal(user_answer, correct_answer)
            logger.info(f"🔍 ANSWER HANDLER: {'✅ ВЕРНО' if is_correct else '❌ НЕВЕРНО'}")

            # 3) Получаем внутренний user_id
            if telegram_id is None:
                await message.answer("❌ Ошибка: не удалось определить пользователя.")
                return

            user_id = await get_user_id_by_telegram_id(session, telegram_id)
            if not user_id:
                logger.error(f"❌ ANSWER HANDLER: Пользователь telegram_id={telegram_id} не найден в БД")
                await message.answer("❌ Ошибка: пользователь не найден в системе.")
                return

            # 4) Детали ТОЛЬКО при ошибке
            generated_task_details: Optional[str] = None

            if not is_correct:
                task_package: Dict[str, Any] = user_data.get("task_package", {}) or {}
                tasks = task_package.get("tasks", [])

                if isinstance(tasks, list) and current_task_index < len(tasks):
                    current_task_data = tasks[current_task_index] or {}
                    plot_data = task_package.get("plot_data", {}) or {}

                    task_details = {
                        "generated_text": current_task_data.get("text", ""),
                        "correct_answer": correct_answer,
                        "plot_data": plot_data,
                        "task_metadata": {
                            "skill_source_id": current_task_data.get("id", "unknown"),
                            "theme": task_subtype,
                            "task_type": task_type,
                            "generation_timestamp": datetime.utcnow().isoformat(),
                        },
                        "additional_data": {
                            "intro": task_package.get("intro", ""),
                            "condition": task_package.get("condition", ""),
                            "table_html": task_package.get("table_html", ""),
                        },
                    }

                    generated_task_details = json.dumps(task_details, ensure_ascii=False)
                    logger.info(
                        f"💾 ANSWER HANDLER: Сохраняем детали ошибочной задачи (len={len(generated_task_details)})"
                    )
                else:
                    logger.warning("⚠️ ANSWER HANDLER: tasks отсутствует/пустой — детали ошибки не собраны")

            # 5) Логируем результат
            answer_log = await log_answer(
                session=session,
                user_id=user_id,
                task_id=current_task_id,
                is_correct=is_correct,
                user_answer=user_answer,
                generated_task_details=generated_task_details,
            )

            if answer_log:
                logger.info(
                    f"📊 ANSWER HANDLER: Лог сохранён (ID={answer_log.id}), details={'yes' if generated_task_details else 'no'}"
                )
            else:
                logger.warning("⚠️ ANSWER HANDLER: log_answer вернул None")

        # 6) UX-ветки
        task_text_for_edit = (
            getattr(task_obj, "text", None)
            or getattr(task_obj, "task_text", None)
            or getattr(task_obj, "question", None)
            or user_data.get("current_task_text")
            or user_data.get("last_task_text")
            or ""
        )

        if is_correct:
            # ✅ ПРАВКА ЗДЕСЬ: меняем верхнее сообщение с заданием
            task_message_id = await get_message_id_by_tag(state, f"focused_task_{current_task_index + 1}")
            logger.info(f"🧪 EDIT TASK FRAME: focused_task_id={task_message_id}")

            if task_message_id:
                # 1) убираем строку "Если нужна подсказка ..."
                cleaned_lines = []
                for line in (task_text_for_edit or "").splitlines():
                    if "Если нужна подсказка" in line:
                        continue
                    cleaned_lines.append(line)
                clean_task_text = "\n".join(cleaned_lines).strip()

                edited_text = (
                    f"<b>Задание {current_task_index + 1}:</b>\n"
                    f"{clean_task_text}\n\n"
                    f"<i>Ответ:</i> ✅ <b>{user_answer}</b>"
                )

                try:
                    await message.bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=task_message_id,
                        text=edited_text,
                        parse_mode="HTML",
                    )
                    await message.bot.edit_message_reply_markup(
                        chat_id=message.chat.id,
                        message_id=task_message_id,
                        reply_markup=None,
                    )
                    logger.info("✅ EDIT TASK FRAME: задание обновлено (текст + убраны кнопки)")
                except Exception as e:
                    logger.warning(f"⚠️ EDIT TASK FRAME: не удалось отредактировать focused_task: {e}")
            else:
                logger.warning("⚠️ EDIT TASK FRAME: message_id по тегу focused_task_X не найден")

            # дальше — как было
            await _handle_correct_answer(
                message, state, current_task_index, user_answer, task_text_for_edit
            )
        else:
            await _handle_incorrect_answer(message, state)

    except Exception as e:
        logger.error(f"❌ ANSWER HANDLER: Критическая ошибка: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при проверке ответа. Попробуйте ещё раз.")


async def _handle_correct_answer(
    message: Message,
    state: FSMContext,
    current_task_index: int,
    user_answer: str,
    task_text_for_edit: str,
):
    """
    ✅ Верный ответ:
    1) (опционально) редактируем сообщение с заданием: дописываем "Ответ: ✅ ..."
       — если не удалось, UX всё равно продолжается.
    2) обновляем solved_tasks_indices
    3) чистим прошлые notifications (старые "кадры результата")
    4) показываем новый "кадр результата" (notifications)
    5) чистим menus (старые пульты)
    6) отправляем новый пульт (menus) с отметками решённых
    7) если все решены — финальная сцена
    """
    logger.info(f"✅ PLAN B: Верный ответ. task_num={current_task_index + 1}")
    bot = message.bot
    chat_id = message.chat.id
    user_data = await state.get_data()

    # --- 1) Аккуратное редактирование верхнего сообщения с заданием ---
    task_package: Dict[str, Any] = user_data.get("task_package", {}) or {}
    tasks = task_package.get("tasks")

    if isinstance(tasks, list) and current_task_index < len(tasks):
        logger.info(
            f"🧪 EDIT TASK FRAME: зашли в редактирование задания {current_task_index + 1}"
        )

        raw_task_text = (tasks[current_task_index] or {}).get("text", "Текст задания не найден")

        # 1️⃣ Убираем строку "Если нужна подсказка — жми ..."
        cleaned_lines = []
        for line in raw_task_text.splitlines():
            if "Если нужна подсказка" in line:
                continue
            cleaned_lines.append(line)
        clean_task_text = "\n".join(cleaned_lines).strip()

        # 2️⃣ Формируем финальный текст задания (как на эталонном скрине)
        edited_text = (
            f"<b>Задание {current_task_index + 1}:</b>\n"
            f"{clean_task_text}\n\n"
            f"<i>Ответ:</i> ✅ <b>{user_answer}</b>"
        )

        # 3️⃣ Меняем текст ИМЕННО того сообщения, которое мы сами отправляли как "focused_task_X"
        task_message_id = await get_message_id_by_tag(state, f"focused_task_{current_task_index + 1}")
        logger.info(f"🧪 EDIT TASK FRAME: focused_task_id={task_message_id}")

        if task_message_id:
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=task_message_id,
                    text=edited_text,
                    parse_mode="HTML",
                )
                # 4️⃣ Полностью убираем кнопки у этого сообщения
                await bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=task_message_id,
                    reply_markup=None,
                )
                logger.info("✅ EDIT TASK FRAME: сообщение задания успешно обновлено (текст + убраны кнопки).")
            except Exception as e:
                logger.warning(f"⚠️ EDIT TASK FRAME: не удалось отредактировать focused_task: {e}")
        else:
            logger.warning("⚠️ EDIT TASK FRAME: focused_task не найден в state (нет message_id по tag).")

    # --- 2) Обновляем solved_tasks_indices ---
    solved_tasks_indices: List[int] = user_data.get("solved_tasks_indices", []) or []
    if current_task_index not in solved_tasks_indices:
        solved_tasks_indices.append(current_task_index)
        await state.update_data(solved_tasks_indices=solved_tasks_indices)

    # --- 3) Чистим старые notifications (старые "кадры результата") ---
    await cleanup_messages_by_category(bot, state, chat_id, "notifications")

    # --- 5) Чистим только menus (пульты/карусели) ---
    await cleanup_messages_by_category(bot, state, chat_id, "menus")

    # --- 6) Новый пульт выбора заданий ---
    task_ids: List[int] = user_data.get("task_ids", []) or []
    subtype_key: str = user_data.get("task_subtype", "tires")

    overview_keyboard = build_overview_keyboard(
        tasks_count=len(task_ids),
        subtype_key=subtype_key,
        solved_indices=solved_tasks_indices,
    )

    student_name = user_data.get("student_name")
    gender = user_data.get("gender")
    feedback_text = get_random_feedback(name=student_name, gender=gender)

    new_overview_text = (
        f"{feedback_text}\n\n"
        f"👇 Выбери следующее задание или вернись в меню."
    )

    unique_overview_tag = f"overview_keyboard_{chat_id}"
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=new_overview_text,
        reply_markup=overview_keyboard,
        message_tag=unique_overview_tag,
        category="menus",
        parse_mode="HTML",
    )
    await state.update_data(current_overview_tag=unique_overview_tag)

    logger.info("✅ PLAN B: Новый пульт отправлен и зарегистрирован.")

    # --- 7) Если решены все ---
    if len(task_ids) > 0 and len(solved_tasks_indices) == len(task_ids):
        await _handle_all_tasks_solved(message, state)


async def _handle_incorrect_answer(message: Message, state: FSMContext):
    """
    ❌ Неверный ответ:
    - показываем сообщение
    - гарантируем FSM-контракт
    - даём кнопку 🆘 Помощь
    """
    idx = await ensure_task_index(state)
    logger.info(f"🧪 FSM GUARD TEST: ensure_task_index вернул → {idx}")
    logger.info("❌ V3.1: Неверный ответ — предлагаем помощь")

    state_data = await state.get_data()

    # 🛡 FSM CONTRACT GUARD
    if "index" not in state_data:
        # fallback: используем current_task_index, если он есть
        fallback_index = state_data.get("current_task_index")

        if fallback_index is None:
            logger.critical(
                "🚨 FSM CONTRACT BROKEN: incorrect_answer without index.\n"
                f"state_keys={list(state_data.keys())}"
            )
            return

        await state.update_data(index=fallback_index)

    # ⬇️ теперь FSM гарантированно валиден
    state_data = await state.get_data()

    subtype_base = state_data.get("task_subtype", "unknown")
    index = state_data["index"]

    # 🔐 НОРМАЛИЗАЦИЯ subtype ДЛЯ ПОМОЩИ
    if subtype_base == "tires":
        subtype_key = f"tires_q{index + 1}"
    else:
        subtype_key = subtype_base

    kb = InlineKeyboardBuilder()
    kb.button(
        text="🆘 Помощь",
        callback_data=TaskCallback(
            action="request_help",
            subtype_key=subtype_key,
            question_num=index + 1,
            task_type=index + 1,
        ).pack(),
    )

    await send_tracked_message(
        bot=message.bot,
        chat_id=message.chat.id,
        state=state,
        text="❌ Не совсем так. Попробуй ещё раз или воспользуйся подсказкой!",
        reply_markup=kb.as_markup(),
        message_tag="incorrect_answer_prompt",
        category="dialog_messages",
    )

async def _handle_all_tasks_solved(message: Message, state: FSMContext):
    """
    Финальный экран, когда решены все 5 задач.
    Есть защита от повторной отправки (session_completed).
    """
    user_data = await state.get_data()
    if user_data.get("session_completed"):
        logger.info("🏁 Финал уже был отправлен — пропускаем повтор.")
        return

    await state.update_data(session_completed=True)

    bot = message.bot
    chat_id = message.chat.id
    subtype_key = user_data.get("task_subtype", "tires")

    final_text = (
        "🎉🎉🎉 <b>ПОБЕДА!</b> 🎉🎉🎉\n\n"
        "Ты справился(ась) со всеми заданиями — это мощно!\n\n"
        "Каждый правильный ответ — шаг к уверенной пятёрке на ОГЭ 💪"
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="💪 Решить ещё один вариант!",
        callback_data=TaskCallback(action="1-5_select_subtype", subtype_key=subtype_key).pack(),
    )
    kb.button(
        text="↩️ Другой подтип",
        callback_data=TaskCallback(action="show_task_1_5_carousel").pack(),
    )
    kb.button(
        text="🔝 В главное меню",
        callback_data="back_to_main",
    )

    kb.adjust(1, 2)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=final_text,
        reply_markup=kb.as_markup(),
        message_tag="final_victory_message",
        category="final_screen",
        parse_mode="HTML",
    )

    logger.info("🏁 Финальная сцена отправлена.")
