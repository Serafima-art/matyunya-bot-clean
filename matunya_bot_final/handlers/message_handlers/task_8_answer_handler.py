"""
Handler for Task 8 User Answers.
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

# Форматтеры для восстановления текста задачи
from matunya_bot_final.help_core.solvers.task_8.task_8_text_formatter import render_node, fmt_number
from matunya_bot_final.keyboards.inline_keyboards.tasks.task_8.task_8_carousel import get_current_theme_name

router = Router()

@router.message(TaskState.waiting_for_answer, F.text)
async def handle_task_8_answer(message: Message, state: FSMContext, bot: Bot):
    """
    Обрабатывает ответ пользователя на Задание 8.
    """
    user_answer = message.text.strip()
    chat_id = message.chat.id

    # 1. Чистим сообщение пользователя и старые диалоги
    try:
        await message.delete()
    except Exception:
        pass

    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")
    await cleanup_messages_by_category(bot, state, chat_id, "answer_feedback") # Удаляем старый фидбек

    # 2. Получаем данные
    data = await state.get_data()
    task_data = data.get("task_8_data")

    # Если это не 8 задание (проверка на всякий случай, если state общий)
    if not task_data or str(task_data.get("task_number")) != "8":
        return

    # 3. Проверка ответа
    correct_answer = str(task_data.get("answer", ""))
    is_correct = answers_equal(user_answer, correct_answer)

    # 4. Визуальное обновление исходного сообщения (эффект "вписал в тетрадь")
    task_msg_id = await get_message_id_by_tag(state, "task_8_main_text")

    if task_msg_id:
        # Пересобираем текст задачи + вставляем ответ
        new_text = _rebuild_task_text_with_answer(task_data, user_answer, is_correct, state)

        # Определяем клавиатуру
        subtype = task_data.get("subtype", "default")
        if is_correct:
            # Если верно -> Кнопки "Следующая", "Меню"
            keyboard = get_task_completed_keyboard(task_number=8, task_subtype=subtype)
        else:
            # Если неверно -> Оставляем "Помощь", "Теория"
            keyboard = get_after_task_keyboard(task_number=8, task_subtype=subtype)

        try:
            # Редактируем сообщение с задачей
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=task_msg_id,
                text=new_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            # Если текст не изменился или ошибка
            pass

    # 5. Отправка обратной связи (отдельным сообщением внизу)
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

        # Сбрасываем состояние ожидания ответа (чтобы не спамил в решенную задачу)
        await state.set_state(None) # Или переводим в состояние выбора

    else:
        # ОШИБКА
        # Клавиатуру помощи дублируем в сообщении с ошибкой для удобства (опционально)
        # Но так как мы оставили её в основном сообщении, тут можно просто текст.

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
    Заново собирает текст задачи, но вместо 'Ответ: ____' ставит ответ пользователя с галочкой/крестиком.
    """
    # 1. Восстанавливаем условие (копируем логику из handler.py)
    tree = task_data.get("expression_tree")
    expr_str = render_node(tree)

    if tree.get("type") == "range_query":
        main_text = f"Посчитай, сколько целых чисел находится между <b>{expr_str}</b>?"
    else:
        main_text = f"Вычисли значение выражения:\n\n<b>{expr_str}</b>"

        vars_disp = task_data.get("variables_display") or task_data.get("variables")
        if vars_disp:
            vars_list = [f"{k} = {fmt_number(v)}" for k, v in vars_disp.items()]
            vars_str = ", ".join(vars_list)
            main_text += f"\n\nпри <b>{vars_str}</b>"

    # 2. Формируем строку ответа
    icon = "✅" if is_correct else "❌"
    # Экранируем ответ пользователя на всякий случай
    safe_answer = str(user_answer).replace("<", "&lt;").replace(">", "&gt;")
    answer_line = f"Ответ: <b>{safe_answer}</b> {icon}"

    # 3. Подвал (статистика) - нужно await, так как compose... асинхронная
    footer_text = await compose_after_task_message_from_state(state)

    # Сборка
    topic_key = task_data.get("subtype") or "default"
    topic_name = get_current_theme_name(topic_key)

    final_text = (
        f"<b>Задание 8:</b> {topic_name}\n"
        f"\n"
        f"{main_text}\n"
        f"\n"
        f"{answer_line}\n" # Вставленный ответ
        f"\n"
        f"{footer_text}"
    )

    return final_text
