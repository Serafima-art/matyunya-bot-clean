"""
Главный обработчик системы помощи - модель "Одно Окно".

Этот модуль реализует упрощенную архитектуру:
- Одна кнопка "🆘 Помощь" -> одно полное решение под спойлером
- Динамический вызов соответствующего "Решателя"
- Передача результата "Оживителю" для гуманизации
- Отправка готового решения пользователю

Автор: Матюня 🤖
Расположение: help_core/dispatchers/help_handler.py
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
from matunya_bot_final.help_core.humanizers.template_humanizers.task_11_humanizer import (
    humanize_solution_11,
)
from matunya_bot_final.help_core.humanizers.template_humanizers.task_20_humanizer import (
    humanize_solution_20,
)

# Импорт универсального CallbackData
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback

# Настраиваем логгер
logger = logging.getLogger(__name__)

# Создаем роутер для обработки помощи
solution_router = Router(name="help_handler")


# ========== ГЛАВНЫЙ ХЕНДЛЕР (МОДЕЛЬ "ОДНО ОКНО") ==========

@solution_router.callback_query(TaskCallback.filter(F.action == "request_help"))
async def handle_help_request(callback: CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext):
    """
    Главный хендлер системы помощи - модель "Одно Окно".

    Реагирует на нажатие кнопки "🆘 Помощь" от любого типа заданий
    и динамически вызывает соответствующего "Решателя".

    Args:
        callback: CallbackQuery от нажатия кнопки "🆘 Помощь"
        callback_data: Структурированные данные TaskCallback
        bot: Экземпляр бота
        state: FSM контекст с данными о задании
    """
    try:
        await callback.answer("🔄 Генерирую полное решение...")

        original_message = callback.message
        if original_message and original_message.reply_markup:
            try:
                keyboard_payload = original_message.reply_markup.model_dump(mode="python")  # type: ignore[attr-defined]
            except Exception as dump_exc:  # pragma: no cover
                logger.warning("Не удалось сериализовать клавиатуру для восстановления: %s", dump_exc)
                keyboard_payload = None

            if keyboard_payload:
                await state.update_data(
                    keyboard_to_restore={
                        "chat_id": original_message.chat.id,
                        "message_id": original_message.message_id,
                        "reply_markup": keyboard_payload,
                    }
                )

            try:
                await original_message.edit_reply_markup(reply_markup=None)
            except Exception as edit_exc:  # pragma: no cover
                logger.warning("Не удалось временно убрать клавиатуру с исходного сообщения: %s", edit_exc)

        # Парсим данные из TaskCallback
        task_subtype = callback_data.subtype_key
        # Используем question_num как основной источник для task_type
        task_type = callback_data.question_num or callback_data.task_id or 11

        logger.info(f"Запрос помощи: task_type={task_type}, subtype={task_subtype}")

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

            logger.debug(f"Отправлена фраза-связка: {help_phrase}")

        except Exception as e:
            logger.warning(f"Не удалось отправить фразу-связку: {e}")

        # Получаем данные о задании из состояния
        state_data = await state.get_data()
        task_type_str = str(task_type)
        task_data_key = f"task_{task_type_str}_data"
        task_payload = state_data.get(task_data_key)

        if not isinstance(task_payload, dict):
            logger.error(
                "В состоянии отсутствуют данные задания для %s/%s (ключ %s)",
                task_type,
                task_subtype,
                task_data_key,
            )
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        # ДИНАМИЧЕСКИЙ ВЫЗОВ "РЕШАТЕЛЯ"
        solution_core = await call_dynamic_solver(task_type_str, task_subtype, task_payload)

        if solution_core is None:
            # Решатель не найден или произошла ошибка
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        # Сохраняем solution_core для будущих диалогов
        solution_core_key = f"task_{task_type_str}_solution_core"
        await state.update_data(solution_core=solution_core, **{solution_core_key: solution_core})

        # ВЫБОР И ВЫЗОВ "ОЖИВИТЕЛЯ"
        try:
            if task_type_str == "11":
                humanized_solution = humanize_solution_11(solution_core)
            elif task_type_str == "20":
                humanized_solution = humanize_solution_20(solution_core)
            else:
                student_name = state_data.get("student_name", "друг")
                humanized_solution = await humanize_solution(solution_core, state, student_name)

            humanized_solution = clean_html_tags(humanized_solution)
        except Exception as humanizer_exc:
            logger.error(
                "Ошибка гуманизации решения для %s/%s: %s",
                task_type,
                task_subtype,
                humanizer_exc,
            )
            humanized_solution = format_basic_solution(solution_core)

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
                logger.warning(f"Не удалось удалить сообщение о процессе: {e}")

        # Отправляем готовое решение
        await send_solution_result(callback, bot, state, humanized_solution, task_type, task_subtype)

        logger.info(f"Успешно сгенерировано решение для {task_type}/{task_subtype}")

    except Exception as e:
        logger.error(f"Критическая ошибка в handle_help_request: {e}")
        logger.error(traceback.format_exc())
        await send_solution_error(callback, bot, f"Произошла ошибка при генерации решения: {str(e)}")


# ========== ДИНАМИЧЕСКИЙ ВЫЗОВ "РЕШАТЕЛЯ" ==========

async def call_dynamic_solver(task_type: str, task_subtype: str, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Динамически находит и вызывает "Решателя" для указанного типа задания.

    Args:
        task_type: Тип задания (например, "11" или "1")
        task_subtype: Подтип задания (например, "match_signs_a_c" или "tires_q1")
        task_data: Данные о задании из FSM состояния

    Returns:
        solution_core от решателя или None при ошибке
    """

    try:
        # --- НАЧАЛО ИЗМЕНЕНИЙ ---
        path_task_type = task_type

        # Проверяем, является ли это заданием из блока 1-5 и подтипом шин
        if task_subtype.startswith("tires"):
            path_task_type = "1_5"
            main_subtype = "tires"
            solver_module_path = f"matunya_bot_final.help_core.solvers.task_{path_task_type}.{main_subtype}.{task_subtype}_solver"
        else:
            solver_module_path = f"matunya_bot_final.help_core.solvers.task_{path_task_type}.{task_subtype}_solver"
        # --- КОНЕЦ ИЗМЕНЕНИЙ ---

        logger.debug(f"Попытка импорта решателя: {solver_module_path}")

        # Динамический импорт модуля
        solver_module = importlib.import_module(solver_module_path)

        # Проверяем наличие стандартной функции solve()
        if not hasattr(solver_module, 'solve'):
            logger.error(f"Модуль {solver_module_path} не содержит функцию solve()")
            return None

        # Вызываем стандартную функцию solve()
        solve_function = getattr(solver_module, 'solve')

        # Определяем, асинхронная ли функция
        import inspect
        if inspect.iscoroutinefunction(solve_function):
            # Асинхронная функция
            solution_core = await solve_function(task_data)
        else:
            # Синхронная функция
            solution_core = solve_function(task_data)

        logger.info(f"Решатель {solver_module_path} успешно выполнен")
        return solution_core

    except ModuleNotFoundError as e:
        logger.warning(f"Решатель не найден: {solver_module_path} - {e}")
        return None

    except AttributeError as e:
        logger.error(f"Функция solve() не найдена в модуле {solver_module_path}: {e}")
        return None

    except Exception as e:
        logger.error(f"Ошибка выполнения решателя {solver_module_path}: {e}")
        logger.error(traceback.format_exc())
        return None


def clean_html_tags(text: str) -> str:
    """
    Очищает текст от недопустимых HTML тегов и исправляет незакрытые теги.

    Args:
        text: Исходный текст

    Returns:
        Очищенный текст с правильными HTML тегами
    """
    import re

    if not text:
        return ""

    try:
        # Шаг 2: Удаляем все HTML теги кроме <b>, </b>, <i>, </i>, <tg-spoiler>, </tg-spoiler>
        text = re.sub(r'<(?!/?(?:b|i|tg-spoiler)(?:\s|>))[^>]*>', '', text)

        # Шаг 3: Исправляем незакрытые теги
        open_b = len(re.findall(r'<b>', text))
        close_b = len(re.findall(r'</b>', text))
        open_i = len(re.findall(r'<i>', text))
        close_i = len(re.findall(r'</i>', text))
        open_spoiler = len(re.findall(r'<tg-spoiler>', text))
        close_spoiler = len(re.findall(r'</tg-spoiler>', text))

        # Добавляем недостающие закрывающие теги
        if open_b > close_b:
            text += '</b>' * (open_b - close_b)
        elif close_b > open_b:
            for _ in range(close_b - open_b):
                text = text.replace('</b>', '', 1)

        if open_i > close_i:
            text += '</i>' * (open_i - close_i)
        elif close_i > open_i:
            for _ in range(close_i - open_i):
                text = text.replace('</i>', '', 1)

        if open_spoiler > close_spoiler:
            text += '</tg-spoiler>' * (open_spoiler - close_spoiler)
        elif close_spoiler > open_spoiler:
            for _ in range(close_spoiler - open_spoiler):
                text = text.replace('</tg-spoiler>', '', 1)

        # Шаг 4: Заменяем <br> на переносы строк
        text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')

        # Шаг 5: Убираем двойные пробелы и лишние переносы
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = text.strip()

        return text

    except Exception as e:
        logger.error(f"Ошибка очистки HTML: {e}")
        # Fallback: убираем все HTML теги кроме разрешенных
        fallback_text = re.sub(r'<(?!/?(?:b|i|tg-spoiler)(?:\s|>))[^>]*>', '', text)
        return fallback_text.strip()


def format_basic_solution(solution_core: Dict[str, Any]) -> str:
    """
    Форматирует базовое решение без гуманизации.

    Args:
        solution_core: Результат работы решателя

    Returns:
        Отформатированное решение
    """
    try:
        # Извлекаем основные компоненты решения
        steps = solution_core.get('solution_steps', [])
        answer = solution_core.get('answer', 'Ответ не найден')
        explanation = solution_core.get('explanation', '')

        text_parts = [
            "🆘 <b>Полное решение</b>",
            ""
        ]

        # Добавляем шаги решения
        if steps:
            text_parts.extend([
                "📝 <b>Пошаговое решение:</b>",
                ""
            ])

            for i, step in enumerate(steps, 1):
                text_parts.append(f"<b>{i}.</b> {step}")

            text_parts.append("")

        # Добавляем объяснение
        if explanation:
            text_parts.extend([
                "💡 <b>Объяснение:</b>",
                explanation,
                ""
            ])

        # Добавляем ответ под спойлером
        text_parts.extend([
            "✨ <i>А теперь попробуй сам! Когда будешь готов, открой ответ:</i>",
            "",
            f"🎯 <b>Ответ:</b> <tg-spoiler>{answer}</tg-spoiler>"
        ])

        return "\n".join(text_parts)

    except Exception as e:
        logger.error(f"Ошибка форматирования базового решения: {e}")
        return "🆘 <b>Решение сгенерировано, но произошла ошибка форматирования</b>"


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

async def send_processing_message(callback: CallbackQuery, bot: Bot, state: FSMContext, task_type: int, task_subtype: str) -> Optional[Any]:
    """
    Отправляет сообщение о начале обработки решения.
    """
    try:
        processing_text = (
            f"🔄 <b>Генерирую решение...</b>\n\n"
            f"📋 Задание №<b>{task_type}</b> (<b>{task_subtype}</b>)\n\n"
            f"⏳ <i>Подбираю решателя и анализирую задачу</i>"
        )

        message = await send_tracked_message(
            bot=bot,
            chat_id=callback.message.chat.id,
            state=state,
            text=processing_text,
            category="solution_processing",
            message_tag=f"processing_{task_subtype}"
        )

        return message

    except Exception as e:
        logger.warning(f"Не удалось отправить сообщение о процессе: {e}")
        return None


async def send_solution_result(callback: CallbackQuery, bot: Bot, state: FSMContext,
                             solution_text: str, task_type: int, task_subtype: str):
    """
    Отправляет готовое решение пользователю.
    """
    try:
        # Создаем клавиатуру для решения
        solution_keyboard = create_solution_keyboard(task_subtype, task_type)

        # Отправляем решение
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
        logger.error(f"Ошибка отправки решения: {e}")


async def send_solver_not_found_message(callback: CallbackQuery, bot: Bot, task_type: int, task_subtype: str):
    """
    Отправляет сообщение о том, что решатель не найден.
    """
    not_found_text = (
        f"😔 <b>Решение пока недоступно</b>\n\n"
        f"📋 Задание №<b>{task_type}</b> (<b>{task_subtype}</b>)\n\n"
        f"🔧 Полное решение для этого типа заданий еще не готово.\n\n"
        f"💡 <b>Что можно сделать:</b>\n"
        f"• Изучи теорию к заданию\n"
        f"• Задай вопрос — постараюсь помочь!\n"
        f"• Попробуй решить самостоятельно"
    )

    fallback_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📚 Теория",
            callback_data=TaskCallback(
                action="request_theory",
                subtype_key=task_subtype,
                question_num=task_type
            ).pack()
        )],
        [InlineKeyboardButton(
            text="❓ Задать вопрос",
            callback_data=TaskCallback(
                action="ask_question",
                subtype_key=task_subtype,
                question_num=task_type
            ).pack()
        )],
        [InlineKeyboardButton(
            text="❌ Закрыть",
            callback_data=TaskCallback(
                action="hide_help",
                subtype_key=task_subtype,
                question_num=task_type
            ).pack()
        )]
    ])

    try:
        await callback.message.edit_text(
            not_found_text,
            parse_mode="HTML",
            reply_markup=fallback_keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения о недоступности решателя: {e}")


async def send_solution_error(callback: CallbackQuery, bot: Bot, error_message: str):
    """
    Отправляет сообщение об ошибке генерации решения.
    """
    error_text = (
        f"❌ <b>Ошибка генерации решения</b>\n\n"
        f"{error_message}\n\n"
        f"🔧 Попробуйте еще раз или обратитесь к теории."
    )

    try:
        await callback.message.edit_text(
            error_text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения об ошибке: {e}")


def create_solution_keyboard(task_subtype: str, task_type: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для сообщения с решением.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        # Кнопка слева
        InlineKeyboardButton(
            text="❌ Закрыть помощь", # <-- Текст можно сделать понятнее
            callback_data=TaskCallback(
                action="hide_help",
                subtype_key=task_subtype,
                question_num=task_type
            ).pack()
        ),
        # Кнопка справа
        InlineKeyboardButton(
            text="❓ Задать вопрос",
            callback_data=TaskCallback(
                action="ask_question",
                subtype_key=task_subtype,
                question_num=task_type
            ).pack()
        )
    )
    # Кнопка "Другое решение" удалена

    return builder.as_markup()

# ========== ЭКСПОРТ ==========

__all__ = [
    "solution_router",
    "handle_help_request",
    "call_dynamic_solver"
]
