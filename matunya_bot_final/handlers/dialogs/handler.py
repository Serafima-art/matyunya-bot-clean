# handlers\dialogs\handler.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import logging
from typing import Dict, List, Any

# --- Наши Инструменты ---
from matunya_bot_final.gpt.gpt_utils import ask_gpt_with_history
from matunya_bot_final.utils.message_manager import send_tracked_message, cleanup_messages_by_category
from matunya_bot_final.states.states import DialogState
from matunya_bot_final.keyboards.navigation.help_dialog_navigation import get_gpt_dialog_keyboard

# CTA-фразы для окна «Помощь»
from matunya_bot_final.gpt.phrases.cta_help_phrases import cta_done_from_fsm, cta_more_from_fsm

# Создаем роутер
router = Router()
logger = logging.getLogger(__name__)

# Максимальная длина истории диалога (количество пар вопрос-ответ)
MAX_DIALOG_HISTORY = 5

# Мягкий лимит на «Ещё вопрос» в одной сессии помощи
HELP_MORE_LIMIT = 5


@router.message(DialogState.in_dialog, F.text)
async def handle_dialog_message(message: Message, state: FSMContext, bot: Bot):
    """
    Универсальный обработчик диалоговых сообщений с контекстом задачи

    Обрабатывает текстовые сообщения пользователя в состоянии DialogState.in_dialog
    Поддерживает два режима:
    - "help_for_task" - диалог в рамках помощи по заданию
    - "chat_mode" - обычная болтовня
    """
    try:
        # Получаем контекст диалога из state
        data = await state.get_data()
        dialog_context = data.get("dialog_context")

        if not dialog_context:
            logger.error("❌ Отсутствует dialog_context в state")
            await message.answer("❌ Произошла ошибка в диалоге. Попробуй начать заново.")
            return

        # === ИЗВЛЕЧЕНИЕ КОНТЕКСТА ЗАДАЧИ ===
        task_context = data.get("task_context")  # Получаем контекст задачи
        # ===============================

        # Получаем или инициализируем историю диалога
        dialog_history = data.get("dialog_history", [])

        # Текст пользователя
        user_question = message.text

        # Данные ученика
        student_name = data.get("student_name", "")
        gender = data.get("gender", "")

        # Обрезаем историю до максимального размера ПЕРЕД вызовом GPT
        if len(dialog_history) > MAX_DIALOG_HISTORY * 2:  # *2: один обмен = 2 сообщения
            dialog_history = dialog_history[-(MAX_DIALOG_HISTORY * 2):]

        logger.info(f"📊 Размер dialog_history в state: {len(dialog_history)} сообщений")

        # Формируем системный промпт с учетом контекста задачи
        if dialog_context == "help_for_task":
            system_prompt = _build_enhanced_help_prompt(
                student_name=student_name,
                gender=gender,
                task_context=task_context,  # Передаем контекст задачи
                dialog_history=dialog_history
            )
        elif dialog_context == "chat_mode":
            # Для режима болтовни используем стандартный промпт
            from matunya_bot_final.help_core.prompts.dialog_prompts import get_chatter_dialog_prompt
            system_prompt = get_chatter_dialog_prompt(
                student_name=student_name,
                gender=gender,
                dialog_history=dialog_history
            )
        else:
            logger.error(f"❌ Неизвестный dialog_context: {dialog_context}")
            await message.answer("❌ Неизвестный режим диалога.")
            return

        # Обращение к GPT
        logger.info(f"🤖 Обращение к GPT в режиме '{dialog_context}'")
        gpt_response, updated_history = await ask_gpt_with_history(
            user_prompt=user_question,
            dialog_history=dialog_history,
            system_prompt=system_prompt
        )

        if not gpt_response:
            await message.answer("❌ Не удалось получить ответ. Попробуй переформулировать вопрос.")
            return

        # Сохраняем сообщение пользователя как диалоговое
        await send_tracked_message(
            bot=bot,
            chat_id=message.chat.id,
            state=state,
            text=f"👤 {user_question}",
            message_tag=f"user_message_{len(dialog_history)}",
            category="dialog_messages"
        )

        # Удаляем исходное сообщение пользователя (чтобы чат оставался аккуратным)
        await message.delete()

        # Ответ бота (БЕЗ клавиатуры)
        await send_tracked_message(
            bot=bot,
            chat_id=message.chat.id,
            state=state,
            text=f"🤖 {gpt_response}",
            message_tag=f"bot_response_{len(dialog_history)}",
            category="dialog_messages"
        )

        # Отдельное мотивирующее сообщение С клавиатурой (только в режиме помощи)
        if dialog_context == "help_for_task":
            try:
                cta_done = cta_done_from_fsm(data)
                cta_more = cta_more_from_fsm(data)
                motivation_text = f"{cta_done}\n{cta_more}"

                # Клавиатура диалога
                dialog_keyboard = get_gpt_dialog_keyboard()

                await send_tracked_message(
                    bot=bot,
                    chat_id=message.chat.id,
                    state=state,
                    text=motivation_text,
                    reply_markup=dialog_keyboard,  # Клавиатура здесь
                    message_tag=f"motivation_{len(dialog_history)}",
                    category="dialog_messages"
                )
            except Exception as e:
                logger.warning(f"⚠️ Не удалось сформировать CTA-фразы: {e}")
                # Fallback: отправляем клавиатуру без мотивации
                dialog_keyboard = get_gpt_dialog_keyboard()
                await send_tracked_message(
                    bot=bot,
                    chat_id=message.chat.id,
                    state=state,
                    text="Что дальше?",
                    reply_markup=dialog_keyboard,
                    message_tag=f"fallback_keyboard_{len(dialog_history)}",
                    category="dialog_messages"
                )
        else:
            # Для режима "chat_mode" просто добавляем клавиатуру
            dialog_keyboard = get_gpt_dialog_keyboard()
            await send_tracked_message(
                bot=bot,
                chat_id=message.chat.id,
                state=state,
                text="Продолжаем?",
                reply_markup=dialog_keyboard,
                message_tag=f"chat_keyboard_{len(dialog_history)}",
                category="dialog_messages"
            )

        # Обновляем историю в state
        await state.update_data(dialog_history=updated_history)

        # Оставляем состояние для дальнейшей беседы
        await state.set_state(DialogState.in_dialog)

        logger.info(f"✅ Обработан диалог, история: {len(updated_history)} сообщений")

    except Exception as e:
        logger.error(f"❌ Ошибка в диалоговом хендлере: {e}")
        import traceback
        traceback.print_exc()

        await message.answer(
            "❌ Произошла ошибка при обработке твоего сообщения. "
            "Попробуй переформулировать вопрос или завершить диалог."
        )


def _build_enhanced_help_prompt(student_name: str, gender: str, task_context: dict, dialog_history: list) -> str:
    """
    Создает улучшенный системный промпт с контекстом конкретной задачи
    """
    base_prompt = (
        "Ты — дружелюбный и умный помощник 'Матюня', который помогает ученикам "
        "решать задачи ОГЭ по математике. Ты терпеливый, понятно объясняешь и "
        "всегда стараешься помочь разобраться в материале."
    )

    # Если есть контекст задачи - добавляем его
    if task_context:
        context_section = (
            "\n\n🎯 ВАЖНЕЙШИЙ КОНТЕКСТ ТЕКУЩЕЙ ЗАДАЧИ:\n"
            f"Ученик сейчас решает задачу типа: {task_context.get('task_type', 'Неизвестно')}\n"
            f"Номер задания: {task_context.get('task_number', 'Неизвестно')}\n\n"
        )

        # Добавляем основное условие, если есть
        main_condition = task_context.get('main_condition', '')
        if main_condition:
            context_section += f"Общее условие задачи:\n{main_condition}\n\n"

        # Добавляем конкретный текст вопроса
        task_text = task_context.get('task_text', '')
        if task_text:
            context_section += f"Конкретный вопрос, с которым нужна помощь:\n{task_text}\n\n"

        # Добавляем информацию о таблицах, если есть
        if task_context.get('allowed_sizes_table'):
            context_section += "В задаче есть таблица размеров шин для справки.\n"

        if task_context.get('service_table'):
            context_section += "В задаче есть таблица цен автосервисов.\n"

        context_section += (
            "\n🎯 ТВОЯ ГЛАВНАЯ ЗАДАЧА:\n"
            "Помогай ученику разобраться ИМЕННО с этим конкретным заданием. "
            "Всегда отталкивайся от данного контекста в своих объяснениях. "
            "Не решай задачу полностью - помогай понять логику и подходы к решению."
        )

        base_prompt += context_section

    # Добавляем персонализацию
    if student_name:
        base_prompt += f"\n\nИмя ученика: {student_name}"

    # Добавляем инструкции по стилю общения
    base_prompt += (
        "\n\nСТИЛЬ ОБЩЕНИЯ:\n"
        "- Отвечай кратко и по делу (2-3 абзаца максимум)\n"
        "- Используй простой, понятный язык\n"
        "- Приводи конкретные примеры из данной задачи\n"
        "- Задавай уточняющие вопросы, если что-то неясно\n"
        "- Будь дружелюбным, но не заискивающим"
    )

    return base_prompt
