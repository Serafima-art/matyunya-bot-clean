import importlib
import inspect
import logging
import traceback
from typing import Any, Dict, Optional

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from matunya_bot_final.keyboards.navigation.emergency import emergency_nav_kb

from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback
from matunya_bot_final.help_core.humanizers.solution_humanizer import humanize_solution
from matunya_bot_final.utils.message_manager import (
    cleanup_messages_by_category,
    send_tracked_message,
)
from matunya_bot_final.keyboards.inline_keyboards.help_core_keyboard import create_solution_keyboard
from matunya_bot_final.utils.text_formatters import sanitize_gpt_response

logger = logging.getLogger(__name__)


async def handle_generic_help(callback: CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext) -> None:
    """
    Обработка запросов помощи для остальных типов заданий.
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

        task_subtype = callback_data.subtype_key
        task_type = callback_data.question_num or callback_data.task_id or 11

        logger.info(f"Запрос помощи (generic): task_type={task_type}, subtype={task_subtype}")

        processing_message = await send_processing_message(callback, bot, state, task_type, task_subtype)

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

        solution_core = await call_dynamic_solver(task_type_str, task_subtype, task_payload)

        if solution_core is None:
            await send_solver_not_found_message(callback, bot, task_type, task_subtype)
            return

        solution_core_key = f"task_{task_type_str}_solution_core"
        await state.update_data(solution_core=solution_core, **{solution_core_key: solution_core})

        try:
            student_name = state_data.get("student_name", "ученик")
            humanized_solution = await humanize_solution(solution_core, state, student_name)
            humanized_solution = clean_html_tags(humanized_solution)
            humanized_solution = sanitize_gpt_response(humanized_solution)
        except Exception as humanizer_exc:
            logger.error(
                "Ошибка генерации человекочитаемого решения для %s/%s: %s",
                task_type,
                task_subtype,
                humanizer_exc,
            )
            humanized_solution = format_basic_solution(solution_core)

        if processing_message:
            try:
                await cleanup_messages_by_category(
                    bot=bot,
                    state=state,
                    chat_id=callback.message.chat.id,
                    category="solution_processing"
                )
            except Exception as e:
                logger.warning(f"Не удалось очистить сообщения о процессе: {e}")

        await send_solution_result(callback, bot, state, humanized_solution, task_type, task_subtype)

        logger.info(f"Успешно сгенерировано решение (generic) для {task_type}/{task_subtype}")

    except Exception as e:
        logger.error(f"Исключение во время generic help: {e}")
        logger.error(traceback.format_exc())
        await send_solution_error(callback, bot, f"Произошла ошибка при обработке решения: {str(e)}")


async def call_dynamic_solver(
    task_type: str,
    task_subtype: str,
    task_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Динамически подтягивает модуль решателя и возвращает его результат.
    """

    try:
        # ==========================================================
        # 🔧 СПЕЦ-ЛОГИКА ДЛЯ ГРУППЫ 1–5 (tires)
        # ==========================================================
        if task_subtype.startswith("tires"):
            if task_subtype == "tires":
                question_index = task_data.get("index")
            else:
                try:
                    question_index = int(task_subtype.rsplit("_q", 1)[1]) - 1
                except (ValueError, IndexError):
                    question_index = None

            if question_index is None:
                logger.critical(
                    "🚨 FSM CONTRACT BROKEN: tires-help вызван без index.\n"
                    f"task_subtype={task_subtype!r}, task_data_keys={list(task_data.keys())}\n"
                    "Ожидается: state['index'] установлен при показе фокусного задания."
                )
                return None


            solver_module_path = (
                f"matunya_bot_final.help_core.solvers."
                f"task_1_5.tires.tires_q{question_index + 1}_solver"
            )

        # ==========================================================
        # 🔧 ОБЩАЯ ЛОГИКА ДЛЯ ВСЕХ ОСТАЛЬНЫХ ЗАДАНИЙ
        # ==========================================================
        else:
            solver_module_path = (
                f"matunya_bot_final.help_core.solvers."
                f"task_{task_type}.{task_subtype}_solver"
            )

        logger.info(f"🔍 Загружаем решатель: {solver_module_path}")

        solver_module = importlib.import_module(solver_module_path)

        if not hasattr(solver_module, "solve"):
            logger.error(f"❌ Модуль {solver_module_path} не содержит функцию solve()")
            return None

        solve_function = solver_module.solve

        if inspect.iscoroutinefunction(solve_function):
            return await solve_function(task_data)
        else:
            return solve_function(task_data)

    except ModuleNotFoundError as e:
        logger.warning(f"❌ Решатель не найден: {solver_module_path} — {e}")
        return None

    except Exception as e:
        logger.error(f"❌ Ошибка выполнения решателя {solver_module_path}: {e}")
        logger.error(traceback.format_exc())
        return None


def clean_html_tags(text: str) -> str:
    """
    Очищает текст от лишних HTML тегов и балансирует открывающие теги.
    """
    import re

    if not text:
        return ""

    try:
        text = re.sub(r'<(?!/?(?:b|i|tg-spoiler)(?:\s|>))[^>]*>', '', text)

        open_b = len(re.findall(r'<b>', text))
        close_b = len(re.findall(r'</b>', text))
        open_i = len(re.findall(r'<i>', text))
        close_i = len(re.findall(r'</i>', text))
        open_spoiler = len(re.findall(r'<tg-spoiler>', text))
        close_spoiler = len(re.findall(r'</tg-spoiler>', text))

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

        text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = text.strip()

        return text

    except Exception as e:
        logger.error(f"Ошибка очистки HTML: {e}")
        fallback_text = re.sub(r'<(?!/?(?:b|i|tg-spoiler)(?:\s|>))[^>]*>', '', text)
        return fallback_text.strip()


def format_basic_solution(solution_core: Dict[str, Any]) -> str:
    """
    Форматирует решение в базовом виде для отображения.
    """
    try:
        steps = solution_core.get('solution_steps', [])
        answer = solution_core.get('answer', 'Ответ не найден')
        explanation = solution_core.get('explanation', '')

        text_parts = [
            "🆘 <b>Полное решение</b>",
            ""
        ]

        if steps:
            text_parts.extend([
                "📝 <b>Пошаговое решение:</b>",
                ""
            ])

            for i, step in enumerate(steps, 1):
                text_parts.append(f"<b>{i}.</b> {step}")

            text_parts.append("")

        if explanation:
            text_parts.extend([
                "💡 <b>Объяснение:</b>",
                explanation,
                ""
            ])

        text_parts.extend([
            "✨ <i>А теперь попробуй сам! Когда будешь готов, открой ответ:</i>",
            "",
            f"🎯 <b>Ответ:</b> <tg-spoiler>{answer}</tg-spoiler>"
        ])

        return "\n".join(text_parts)

    except Exception as e:
        logger.error(f"Ошибка форматирования базового решения: {e}")
        return "🆘 <b>Решение сгенерировано, но произошла ошибка форматирования</b>"


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
                               solution_text: str, task_type: int, task_subtype: str) -> None:
    """
    Отправляет готовое решение пользователю.
    """
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
        logger.error(f"Ошибка отправки решения: {e}")


async def send_solver_not_found_message(callback: CallbackQuery, bot: Bot, task_type: int, task_subtype: str) -> None:
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

    # ⚠️ Fallback-клавиатура:
    # Используется только если решатель для задания не найден.
    # В отличие от основной create_solution_keyboard, эта клавиатура автономна,
    # чтобы сообщение "Решение пока недоступно" могло работать даже без импорта UI-модулей.
    # Кнопки:
    # • 📚 Теория — переход к теоретическому разделу
    # • ❓ Задать вопрос — запуск диалога с GPT
    # • ❌ Закрыть — закрытие окна помощи
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
        logger.error(f"Ошибка отправки fallback сообщения о решателе: {e}")


async def send_solution_error(callback: CallbackQuery, bot: Bot, error_message: str) -> None:
    """
    Отправляет сообщение об ошибке при генерации решения + аварийные кнопки.
    """
    error_text = (
        f"😔 <b>Ошибка генерации решения</b>\n\n"
        f"{error_message}\n\n"
        f"💡 Выбери другое задание или вернись в меню."
    )

    try:
        await callback.message.edit_text(
            error_text,
            parse_mode="HTML",
            reply_markup=emergency_nav_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения об ошибке: {e}")


__all__ = [
    "handle_generic_help",
    "call_dynamic_solver",
    "clean_html_tags",
    "format_basic_solution",
    "send_processing_message",
    "send_solution_result",
    "send_solver_not_found_message",
    "send_solution_error",
]
