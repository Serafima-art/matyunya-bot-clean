# -*- coding: utf-8 -*-
"""
Специализированный обработчик помощи для Заданий 1-5 ("Шины").

Этот модуль знает ТОЛЬКО об особенностях блока заданий 1-5 и работает
с вложенной структурой решателей (task_1_5/tires/*.py).

Автор: Матюня 🤖
Расположение: help_core/dispatchers/help_handler_1_5.py
"""

import logging
import importlib
import traceback
from typing import Dict, Any, Optional

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Импорты системы помощи
from matunya_bot_final.utils.message_manager import send_tracked_message, cleanup_messages_by_category
from matunya_bot_final.help_core.humanizers.solution_humanizer import humanize_solution

# Импорт универсального CallbackData
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback

# Настраиваем логгер
logger = logging.getLogger(__name__)

# Создаем роутер для Заданий 1-5
router = Router(name="help_handler_1_5")


# ========== ГЛАВНЫЙ ХЕНДЛЕР ДЛЯ ЗАДАНИЙ 1-5 ==========

@router.callback_query(TaskCallback.filter(
    (F.action == "request_help") & (F.question_num.in_({1, 2, 3, 4, 5}))
))
async def handle_help_request_task_1_5(callback: CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext):
    """
    Специализированный хендлер для Заданий 1-5 ("Шины").

    Реагирует только на запросы помощи для question_num in {1, 2, 3, 4, 5}.
    Знает о вложенной структуре: task_1_5/tires/{subtype}_solver.py

    Args:
        callback: CallbackQuery от нажатия кнопки "🆘 Помощь"
        callback_data: Структурированные данные TaskCallback
        bot: Экземпляр бота
        state: FSM контекст с данными о задании
    """
    try:
        await callback.answer("🔄 Генерирую решение для задания о шинах...")

        task_subtype = callback_data.subtype_key
        task_type = callback_data.question_num  # 1, 2, 3, 4 или 5

        logger.info(f"[Задания 1-5] Запрос помощи: question_num={task_type}, subtype={task_subtype}")

        # Отправляем сообщение о начале обработки
        processing_message = await send_processing_message(callback, bot, state, task_type, task_subtype)

        # Отправляем рандомную фразу-связку
        try:
            from matunya_bot_final.help_core.humanizers.phrases import get_random_phrase
            help_phrase = get_random_phrase("solution")

            await send_tracked_message(
                bot=bot,
                chat_id=callback.message.chat.id,
                state=state,
                text=help_phrase,
                message_tag=f"help_phrase_{task_subtype}",
                category=f"help_{task_subtype}"
            )

            logger.debug(f"[Задания 1-5] Отправлена фраза-связка")

        except Exception as e:
            logger.warning(f"[Задания 1-5] Не удалось отправить фразу-связку: {e}")

        # Получаем данные о задании из состояния
        task_data_from_state = await state.get_data()

        # Извлекаем ВЕСЬ task_package и передаем его решателю
        task_package = task_data_from_state.get("task_package", {})

        # ДИНАМИЧЕСКИЙ ВЫЗОВ "РЕШАТЕЛЯ" ДЛЯ ЗАДАНИЙ 1-5
        # Передаем ВЕСЬ task_package целиком
        solution_core = await call_solver_task_1_5(task_subtype, task_package)

        if solution_core is None:
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        # Сохраняем solution_core для будущих диалогов
        await state.update_data(solution_core=solution_core)

        # ВЫЗОВ "ОЖИВИТЕЛЯ"
        humanized_solution = await call_humanizer(solution_core, state, task_data_from_state)

        # Удаляем сообщение о процессе
        if processing_message:
            try:
                await cleanup_messages_by_category(
                    bot=bot,
                    state=state,
                    chat_id=callback.message.chat.id,
                    category="solution_processing"
                )
            except Exception as e:
                logger.warning(f"[Задания 1-5] Не удалось удалить сообщение о процессе: {e}")

        # Отправляем готовое решение
        await send_solution_result(callback, bot, state, humanized_solution, task_type, task_subtype)

        logger.info(f"[Задания 1-5] Успешно сгенерировано решение для {task_subtype}")

    except Exception as e:
        logger.error(f"[Задания 1-5] Критическая ошибка: {e}")
        logger.error(traceback.format_exc())
        await send_solution_error(callback, bot, f"Произошла ошибка при генерации решения: {str(e)}")


# ========== ВЫЗОВ РЕШАТЕЛЯ ДЛЯ ЗАДАНИЙ 1-5 ==========

async def call_solver_task_1_5(task_subtype: str, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Вызывает решателя для Заданий 1-5 ("Шины").

    Использует вложенную структуру: task_1_5/tires/{subtype}_solver

    Args:
        task_subtype: Подтип задания (например, "tires_q1", "tires_q2")
        task_data: Данные о задании из FSM состояния

    Returns:
        solution_core от решателя или None при ошибке
    """
    try:
        # Определяем главную категорию (пока только "tires")
        if task_subtype.startswith("tires"):
            main_subtype = "tires"
        else:
            logger.error(f"[Задания 1-5] Неизвестный подтип: {task_subtype}")
            return None

        # Формируем вложенный путь: task_1_5/tires/{subtype}_solver
        solver_module_path = f"matunya_bot_final.help_core.solvers.task_1_5.{main_subtype}.{task_subtype}_solver"

        logger.debug(f"[Задания 1-5] Попытка импорта: {solver_module_path}")

        # Динамический импорт модуля
        solver_module = importlib.import_module(solver_module_path)

        # Проверяем наличие функции solve()
        if not hasattr(solver_module, 'solve'):
            logger.error(f"[Задания 1-5] Модуль {solver_module_path} не содержит функцию solve()")
            return None

        # Вызываем функцию solve()
        solve_function = getattr(solver_module, 'solve')

        # Определяем, асинхронная ли функция
        import inspect
        if inspect.iscoroutinefunction(solve_function):
            solution_core = await solve_function(task_data)
        else:
            solution_core = solve_function(task_data)

        logger.info(f"[Задания 1-5] Решатель {solver_module_path} успешно выполнен")
        return solution_core

    except ModuleNotFoundError as e:
        logger.warning(f"[Задания 1-5] Решатель не найден: {solver_module_path} - {e}")
        return None

    except Exception as e:
        logger.error(f"[Задания 1-5] Ошибка выполнения решателя: {e}")
        logger.error(traceback.format_exc())
        return None


# ========== ОБЩИЕ ФУНКЦИИ (копии из базового хендлера) ==========

async def call_humanizer(solution_core: Dict[str, Any], state: FSMContext, task_data: Dict[str, Any]) -> str:
    """Вызывает "Оживитель" для гуманизации решения."""
    try:
        student_name = task_data.get("student_name", "друг")
        humanized_solution = await humanize_solution(solution_core, state, student_name)
        humanized_solution = clean_html_tags(humanized_solution)
        logger.debug("[Задания 1-5] Решение успешно гуманизировано")
        return humanized_solution
    except Exception as e:
        logger.error(f"[Задания 1-5] Ошибка гуманизации: {e}")
        return format_basic_solution(solution_core)


def clean_html_tags(text: str) -> str:
    """Очищает текст от недопустимых HTML тегов."""
    import re
    if not text:
        return ""

    try:
        text = re.sub(r'([a-zA-Z]\s*>\s*\d+)', lambda m: m.group(1).replace('>', '&gt;'), text)
        text = re.sub(r'([a-zA-Z]\s*<\s*\d+)', lambda m: m.group(1).replace('<', '&lt;'), text)
        text = re.sub(r'<(?!/?(?:b|i|tg-spoiler)(?:\s|>))[^>]*>', '', text)

        open_b = len(re.findall(r'<b>', text))
        close_b = len(re.findall(r'</b>', text))
        open_i = len(re.findall(r'<i>', text))
        close_i = len(re.findall(r'</i>', text))
        open_spoiler = len(re.findall(r'<tg-spoiler>', text))
        close_spoiler = len(re.findall(r'</tg-spoiler>', text))

        if open_b > close_b:
            text += '</b>' * (open_b - close_b)
        if open_i > close_i:
            text += '</i>' * (open_i - close_i)
        if open_spoiler > close_spoiler:
            text += '</tg-spoiler>' * (open_spoiler - close_spoiler)

        text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        return text.strip()
    except Exception as e:
        logger.error(f"[Задания 1-5] Ошибка очистки HTML: {e}")
        return re.sub(r'<(?!/?(?:b|i|tg-spoiler)(?:\s|>))[^>]*>', '', text).strip()


def format_basic_solution(solution_core: Dict[str, Any]) -> str:
    """Форматирует базовое решение без гуманизации."""
    try:
        steps = solution_core.get('calculation_steps', [])
        answer_data = solution_core.get('final_answer', {})
        answer = answer_data.get('value_display', 'Ответ не найден')
        explanation = solution_core.get('explanation_idea', '')

        text_parts = ["🆘 <b>Полное решение</b>", ""]

        if steps:
            text_parts.extend(["📝 <b>Пошаговое решение:</b>", ""])
            for step in steps:
                desc = step.get('description', '')
                result = step.get('calculation_result', '')
                text_parts.append(f"• {desc} → {result}")
            text_parts.append("")

        if explanation:
            text_parts.extend(["💡 <b>Идея:</b>", explanation, ""])

        text_parts.extend([
            "✨ <i>Попробуй сам! Когда будешь готов, открой ответ:</i>",
            "",
            f"🎯 <b>Ответ:</b> <tg-spoiler>{answer}</tg-spoiler>"
        ])

        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"[Задания 1-5] Ошибка форматирования: {e}")
        return "🆘 <b>Решение сгенерировано, но произошла ошибка форматирования</b>"


async def send_processing_message(callback: CallbackQuery, bot: Bot, state: FSMContext, task_type: int, task_subtype: str):
    """Отправляет сообщение о начале обработки."""
    try:
        processing_text = (
            f"🔄 <b>Генерирую решение...</b>\n\n"
            f"📋 Задание №<b>{task_type}</b> (<b>{task_subtype}</b>)\n\n"
            f"⏳ <i>Подбираю решателя</i>"
        )

        return await send_tracked_message(
            bot=bot,
            chat_id=callback.message.chat.id,
            state=state,
            text=processing_text,
            category="solution_processing",
            message_tag=f"processing_{task_subtype}"
        )
    except Exception as e:
        logger.warning(f"[Задания 1-5] Не удалось отправить сообщение о процессе: {e}")
        return None


async def send_solution_result(callback: CallbackQuery, bot: Bot, state: FSMContext,
                             solution_text: str, task_type: int, task_subtype: str):
    """Отправляет готовое решение."""
    try:
        solution_keyboard = create_solution_keyboard(task_subtype, task_type)

        await send_tracked_message(
            bot=bot,
            chat_id=callback.message.chat.id,
            state=state,
            text=solution_text,
            reply_markup=solution_keyboard,
            category="solution_result",
            message_tag=f"solution_{task_subtype}"
        )
    except Exception as e:
        logger.error(f"[Задания 1-5] Ошибка отправки решения: {e}")


async def send_solver_not_found_message(callback: CallbackQuery, bot: Bot, task_type: int, task_subtype: str):
    """Сообщение о недоступности решателя."""
    not_found_text = (
        f"😔 <b>Решение пока недоступно</b>\n\n"
        f"📋 Задание №<b>{task_type}</b> (<b>{task_subtype}</b>)\n\n"
        f"🔧 Решатель для этого подтипа еще не готов."
    )

    try:
        await callback.message.edit_text(not_found_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"[Задания 1-5] Ошибка отправки сообщения о недоступности: {e}")


async def send_solution_error(callback: CallbackQuery, bot: Bot, error_message: str):
    """Сообщение об ошибке."""
    try:
        await callback.message.edit_text(
            f"❌ <b>Ошибка</b>\n\n{error_message}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"[Задания 1-5] Ошибка отправки сообщения об ошибке: {e}")


def create_solution_keyboard(task_subtype: str, task_type: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для решения."""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(
        text="❓ Задать вопрос",
        callback_data=TaskCallback(
            action="ask_question",
            subtype_key=task_subtype,
            question_num=task_type
        ).pack()
    ))

    builder.row(InlineKeyboardButton(
        text="🔄 Другое решение",
        callback_data=TaskCallback(
            action="request_help",
            subtype_key=task_subtype,
            question_num=task_type
        ).pack()
    ))

    builder.row(InlineKeyboardButton(
        text="❌ Закрыть",
        callback_data=TaskCallback(
            action="hide_help",
            subtype_key=task_subtype,
            question_num=task_type
        ).pack()
    ))

    return builder.as_markup()
