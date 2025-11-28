"""
Handler for Task 6 User Answers.
Checks the answer, updates the task message visually, and manages flow.
"""

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# Утилиты и состояния
from matunya_bot_final.states.states import TaskState
from matunya_bot_final.utils.answer_utils import answers_equal
from matunya_bot_final.utils.message_manager import (
    send_tracked_message,
    cleanup_messages_by_category,
    get_message_id_by_tag,
    track_existing_message
)
from matunya_bot_final.keyboards.inline_keyboards.after_task_keyboard import (
    get_after_task_keyboard,
    get_task_completed_keyboard,
    compose_after_task_message_from_state
)
from matunya_bot_final.gpt.phrases.tasks.correct_answer_feedback import get_random_feedback

# Форматтеры для текста
from matunya_bot_final.utils.text_formatters import cleanup_math_for_display
try:
    from matunya_bot_final.utils.text_formatters import format_math_text as _fmt_math
except ImportError:
    _fmt_math = lambda s: s

# Для заголовка темы
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_6.task_6_carousel import get_current_theme_name

router = Router()

@router.message(TaskState.waiting_for_answer, F.text)
async def handle_task_6_answer(message: Message, state: FSMContext, bot: Bot):
    """
    Обрабатывает ответ пользователя на Задание 6.
    """
    user_answer = message.text.strip()
    chat_id = message.chat.id

    # 1. Чистим сообщение пользователя и старые диалоги
    try:
        await message.delete()
    except Exception:
        pass

    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")
    await cleanup_messages_by_category(bot, state, chat_id, "answer_feedback")

    # 2. Получаем данные
    data = await state.get_data()
    task_data = data.get("task_6_data")

    # Если это не 6 задание - выходим (пусть ловит другой хендлер)
    # Проверяем либо наличие данных, либо явный флаг номера
    if not task_data:
        return

    # Дополнительная проверка: если в task_data есть task_number, сверяем его.
    # Если нет - полагаемся на наличие ключа task_6_data в state.
    if str(task_data.get("task_number", "6")) != "6":
        return

    # 3. Проверка ответа
    correct_answer = str(task_data.get("answer", ""))
    is_correct = answers_equal(user_answer, correct_answer)

    # 4. Визуальное обновление исходного сообщения
    task_msg_id = await get_message_id_by_tag(state, "task_6_main_text")

    if task_msg_id:
        # Пересобираем текст задачи + вставляем ответ
        new_text = await _rebuild_task_text_with_answer(task_data, user_answer, is_correct, state)

        # Определяем клавиатуру
        # В Task 6 subtype может лежать в 'subtype' или 'topic'
        subtype = task_data.get("subtype") or task_data.get("topic") or "common_fractions"

        if is_correct:
            keyboard = get_task_completed_keyboard(task_number=6, task_subtype=subtype)
        else:
            keyboard = get_after_task_keyboard(task_number=6, task_subtype=subtype)

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=task_msg_id,
                text=new_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception:
            pass

    # 5. Отправка обратной связи
    if is_correct:
        # ПОБЕДА
        feedback_text = get_random_feedback(
            name=data.get("student_name"),
            gender=data.get("gender")
        )

        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=feedback_text,
            category="answer_feedback",
            message_tag="feedback_success"
        )

        # Сбрасываем состояние
        await state.set_state(None)

    else:
        # ОШИБКА
        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text=f"❌ <b>Неверно.</b> Ты написал: {user_answer}\nПопробуй еще раз или нажми «🆘 Помощь»!",
            category="answer_feedback",
            message_tag="feedback_error"
        )


async def _rebuild_task_text_with_answer(task_data: dict, user_answer: str, is_correct: bool, state: FSMContext) -> str:
    """
    Заново собирает текст задачи 6, добавляя ответ пользователя.
    """
    # 1. Восстанавливаем условие
    raw_text = (
        task_data.get("question_text")
        or task_data.get("text")
        or task_data.get("question")
        or ""
    )
    # Форматируем математику (дроби и т.д.)
    question_text = _fmt_math(raw_text)

    # 2. Формируем строку ответа
    icon = "✅" if is_correct else "❌"
    safe_answer = str(user_answer).replace("<", "&lt;").replace(">", "&gt;")
    answer_line = f"Ответ: <b>{safe_answer}</b> {icon}"

    # 3. Подвал (статистика)
    footer_text = await compose_after_task_message_from_state(state)

    # 4. Заголовок темы
    topic_key = task_data.get("topic") or task_data.get("subtype") or "default"
    topic_name = get_current_theme_name(topic_key)

    # Сборка
    final_text = (
        f"<b>Задание 6:</b> {topic_name}\n"
        f"\n"
        f"{question_text}\n"
        f"\n"
        f"{answer_line}\n"
        f"\n"
        f"{footer_text}"
    )

    # Финальная чистка (умножение, пробелы)
    final_text = cleanup_math_for_display(final_text)
    final_text = final_text.replace("·", "<code>·</code>") # Для красоты, как в основном хендлере

    return final_text
