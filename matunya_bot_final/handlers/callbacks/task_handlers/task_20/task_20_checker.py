"""Checker for task 20: polynomial factorization with interactive verification."""

import logging
from typing import Any, Dict, Tuple
from uuid import uuid4

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.help_core.dispatchers.help_handler import (
    call_dynamic_solver,
    clean_html_tags,
    format_basic_solution,
)
from matunya_bot_final.help_core.humanizers.template_humanizers.task_20_humanizer import (
    humanize_solution_20,
)
from matunya_bot_final.help_core.prompts.task_20_dialog_prompts import get_task_20_dialog_prompt
from matunya_bot_final.keyboards.navigation.help_dialog_navigation import (
    get_help_panel_keyboard,
)
from matunya_bot_final.states.states import GPState, TaskState
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
)
from matunya_bot_final.utils.gpt_answer_parser import parse_math_answer_with_gpt

logger = logging.getLogger(__name__)
router = Router(name="task_20_router")

_HELP_PANEL_TAG = "task_20_help_panel"


@router.callback_query(TaskCallback.filter(F.action == "20_send_task"))
async def send_task_20(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """Send polynomial factorization task and wait for text answer."""

    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await callback.answer()

    data = await state.get_data()
    task_data = data.get("task_20_data")

    if not isinstance(task_data, dict):
        logger.error("Task 20: task_20_data is missing in FSM state")
        await bot.send_message(chat_id, "Ошибка: данные задания не найдены.")
        return

    # Формируем текст задания
    variables = task_data.get("variables", {})
    polynomial = variables.get("polynomial", "многочлен")

    task_text = (
        f"📋 <b>Задание 20: Разложение многочлена на множители</b>\n\n"
        f"Разложите на множители многочлен:\n"
        f"<code>{polynomial}</code>\n\n"
        f"💬 <b>Напишите ответ в виде произведения множителей.</b>\n"
        f"Например: <code>(x-5)(x+2)</code> или <code>3(x+1)(x-1)</code>"
    )

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=task_text,
        reply_markup=None,  # Без кнопки "Помощь" - сначала ждем ответ
        message_tag=f"task_20_{uuid4().hex}",
        category="task_messages",
    )

    # Переводим в состояние ожидания ответа
    await state.set_state(TaskState.waiting_task_20_answer)
    logger.info("Task 20 sent, waiting for student answer")


@router.message(TaskState.waiting_task_20_answer, F.text)
async def handle_task_20_answer(message: Message, bot: Bot, state: FSMContext) -> None:
    """Process student's text answer for task 20."""

    chat_id = message.chat.id
    student_answer = message.text.strip()

    data = await state.get_data()
    task_data = data.get("task_20_data")

    if not isinstance(task_data, dict):
        logger.error("Task 20 answer: task_20_data missing")
        await message.answer("Ошибка: не найдены данные задания.")
        return

    correct_answer = task_data.get("answer", [])

    # Парсим ответ ученика с помощью GPT
    try:
        parsed_answer = await parse_math_answer_with_gpt(student_answer, expected_format="factors")
        logger.info(f"Task 20: parsed answer = {parsed_answer}")
    except Exception as exc:
        logger.exception("Task 20: GPT parsing failed", exc_info=exc)
        parsed_answer = None

    # Сравниваем ответы
    is_correct = _compare_answers(parsed_answer, correct_answer)

    if is_correct:
        # Правильный ответ
        await send_tracked_message(
            bot=bot,
            chat_id=chat_id,
            state=state,
            text="🎉 <b>Отлично!</b> Ты правильно разложил многочлен на множители!",
            reply_markup=None,
            message_tag=f"task_20_success_{uuid4().hex}",
            category="task_messages",
        )
        await state.set_state(None)  # Завершаем задание
        logger.info("Task 20: correct answer received")

    else:
        # Неправильный ответ - показываем разбор
        await _show_solution_and_dialog_option(message, bot, state, task_data)


async def _build_task_20_solution(task_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    # Create formatted help text and solution_core for task 20 using unified solver.
    task_subtype = task_data.get('subtype') or task_data.get('topic') or 'polynomial_factorization'
    solution_core = await call_dynamic_solver('20', task_subtype, task_data)
    if solution_core is None:
        raise RuntimeError(f'Solver returned no data for subtype {task_subtype!r}')
    try:
        help_text = humanize_solution_20(solution_core)
        help_text = clean_html_tags(help_text)
    except Exception as exc:
        logger.exception('Task 20: humanizer failed', exc_info=exc)
        help_text = format_basic_solution(solution_core)
    return help_text, solution_core
async def _show_solution_and_dialog_option(
    message: Message,
    bot: Bot,
    state: FSMContext,
    task_data: Dict[str, Any]
) -> None:
    """Show solution breakdown and offer dialog with GPT."""

    chat_id = message.chat.id

    # Очищаем старые сообщения помощи
    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")
    await cleanup_messages_by_category(bot, state, chat_id, "help_panels")

    # Получаем эталонное решение
    try:
        help_text, solution_core = await _build_task_20_solution(task_data)
    except Exception as exc:
        logger.exception("Task 20: failed to build solution", exc_info=exc)
        await message.answer("Не удалось построить решение. Попробуй еще раз.")
        return

    # Сохраняем solution_core в state
    await state.update_data(task_20_solution_core=solution_core)

    # Отправляем сообщение об ошибке
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text="❌ <b>Не совсем так...</b> Давай разберём правильное решение:",
        reply_markup=None,
        message_tag=f"task_20_wrong_{uuid4().hex}",
        category="dialog_messages",
    )

    # Отправляем эталонное решение
    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=help_text,
        reply_markup=None,
        message_tag=_HELP_PANEL_TAG,
        category="help_panels",
    )

    # Предлагаем задать вопрос
    keyboard = get_help_panel_keyboard(task_num="20", question_num=20)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text=(
            "📚 <b>Сравни свои шаги с эталонным решением.</b>\n\n"
            "Если что-то осталось непонятно — смело жми <b>❓ Задать вопрос</b>, "
            "и я помогу разобраться!"
        ),
        reply_markup=keyboard,
        message_tag=f"task_20_dialog_invite_{uuid4().hex}",
        category="dialog_messages",
    )

    await state.set_state(None)  # Выходим из состояния ожидания ответа
    logger.info("Task 20: solution shown, dialog option offered")


@router.callback_query(TaskCallback.filter(F.action == "20_ask_gpt"))
async def handle_task_20_ask_gpt(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """Start GPT dialog for task 20 after showing solution."""

    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await callback.answer()

    await cleanup_messages_by_category(bot, state, chat_id, "dialog_messages")

    data = await state.get_data()
    task_data = data.get("task_20_data")

    if not isinstance(task_data, dict):
        logger.error("Task 20 ask_gpt: task_20_data missing")
        await bot.send_message(chat_id, "Не удалось найти данные задания.")
        return

    solution_core = data.get("task_20_solution_core")
    if solution_core is None:
        try:
            _, solution_core = await _build_task_20_solution(task_data)
        except Exception as exc:
            logger.exception("Task 20 ask_gpt: solver failed", exc_info=exc)
            await bot.send_message(chat_id, "Не удалось подготовить решение для обсуждения.")
            return
        await state.update_data(task_20_solution_core=solution_core)

    student_name = data.get("student_name")
    gender = data.get("gender")

    # Генерируем системный промпт для GPT
    system_prompt = get_task_20_dialog_prompt(
        task_data=task_data,
        solution_core=solution_core,
        student_name=student_name,
        gender=gender,
    )

    previous_state = await state.get_state()

    await state.update_data(
        gpt_dialog_context="task_20",
        gpt_system_prompt=system_prompt,
        gpt_dialog_history=[],
        gpt_previous_state=previous_state,
    )
    await state.set_state(GPState.in_dialog)

    await send_tracked_message(
        bot=bot,
        chat_id=chat_id,
        state=state,
        text="🤔 <b>На каком шаге у тебя возникли трудности?</b>\n\nОпиши, что именно непонятно.",
        reply_markup=None,
        message_tag=f"task_20_gpt_start_{uuid4().hex}",
        category="dialog_messages",
    )

    logger.info("Task 20: GPT dialog started")


def _compare_answers(parsed_answer: Any, correct_answer: list) -> bool:
    """
    Compare student's parsed answer with correct answer.

    Args:
        parsed_answer: Parsed answer from GPT (could be list, string, or None)
        correct_answer: Correct answer from task_data

    Returns:
        True if answers match
    """
    if parsed_answer is None:
        return False

    # Нормализуем оба ответа к спискам строк
    if isinstance(parsed_answer, str):
        parsed_answer = [parsed_answer]
    if not isinstance(parsed_answer, list):
        return False

    # Сортируем и сравниваем
    parsed_sorted = sorted([str(x).strip() for x in parsed_answer])
    correct_sorted = sorted([str(x).strip() for x in correct_answer])

    return parsed_sorted == correct_sorted


__all__ = ["router"]
