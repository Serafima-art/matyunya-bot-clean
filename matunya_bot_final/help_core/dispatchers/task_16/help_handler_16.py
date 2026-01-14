# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from pathlib import Path
import pprint

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile

from matunya_bot_final.help_core.dispatchers.common import (
    call_dynamic_solver,
    send_solution_result,
    send_solver_not_found_message,
    send_solution_error,
)
from matunya_bot_final.help_core.humanizers.template_humanizers.task_16_humanizer import (
    humanize,
)
from matunya_bot_final.utils.message_manager import send_tracked_photo

logger = logging.getLogger(__name__)


async def handle_task_16_help(
    callback: CallbackQuery,
    callback_data,
    bot: Bot,
    state: FSMContext,
) -> None:
    """
    Обрабатывает запрос помощи по Заданию №16 (Окружность).

    Архитектура:
    - НЕ анализируем текст задачи
    - НЕ определяем тему по тексту
    - Handler выбирает solver по theme_key
    - Solver работает по pattern + task_context
    - Картинки помощи выводятся ТОЛЬКО здесь
    """
    try:
        await callback.answer("Готовлю пошаговое решение...")

        task_type = 16
        state_data = await state.get_data()

        # ------------------------------------------------------------------
        # 1️⃣ Payload задания
        # ------------------------------------------------------------------
        task_payload = state_data.get("task_16_data")

        if not isinstance(task_payload, dict):
            logger.error("[Help16] task_16_data отсутствует или не dict")
            await send_solver_not_found_message(callback, bot, task_type)
            return

        pattern = task_payload.get("pattern")
        theme_key = task_payload.get("theme_key")

        if not pattern:
            logger.error("[Help16] В task_payload отсутствует ключ 'pattern'")
            await send_solver_not_found_message(callback, bot, task_type)
            return

        if not theme_key:
            logger.error("[Help16] В task_payload отсутствует ключ 'theme_key'")
            await send_solver_not_found_message(callback, bot, task_type)
            return

        # ------------------------------------------------------------------
        # 2️⃣ Вызов solver'а (по ТЕМЕ)
        # ------------------------------------------------------------------
        solution_core = await call_dynamic_solver(
            str(task_type),
            theme_key,
            task_payload,
        )

        logger.warning("[DEBUG][Help16] solution_core:\n%s", pprint.pformat(solution_core))

        if not isinstance(solution_core, dict):
            logger.error("[Help16] solver вернул некорректный результат")
            await send_solver_not_found_message(callback, bot, task_type)
            return

        # ------------------------------------------------------------------
        # 3️⃣ Гуманизация
        # ------------------------------------------------------------------
        try:
            humanized_solution = humanize(solution_core)
        except Exception as exc:
            logger.error("[Help16] Ошибка гуманизации: %s", exc, exc_info=True)
            await send_solution_error(callback, bot, "Ошибка при оформлении решения.")
            return

        # 4️⃣ КАРТИНКА ПОМОЩИ (если есть)
        help_image_file = task_payload.get("help_image_file")

        if help_image_file:
            package_root = Path(__file__).resolve().parents[3]  # ← ВАЖНО
            image_path = (
                package_root
                / "non_generators"
                / "task_16"
                / "assets"
                / help_image_file
            )

            chat_id = callback.message.chat.id

            if image_path.exists():
                await send_tracked_photo(
                    bot=bot,
                    chat_id=chat_id,
                    state=state,
                    photo=BufferedInputFile.from_file(image_path),
                    category="solution_result",
                    message_tag="task_16_help_image",
                )
            else:
                logger.warning(
                    "[Help16] Файл картинки помощи не найден: %s",
                    image_path,
                )

        # ------------------------------------------------------------------
        # 5️⃣ Сохраняем в state
        # ------------------------------------------------------------------
        await state.update_data(
            task_16_help_text=humanized_solution,
            task_16_solution_core=solution_core,
            help_opened=True,
        )

        # ------------------------------------------------------------------
        # 6️⃣ Отправляем текст решения + клавиатуру
        # ------------------------------------------------------------------
        await send_solution_result(
            callback,
            bot,
            state,
            humanized_solution,
            task_type,
            pattern,
        )

        logger.info(
            "[Help16] Решение успешно сформировано (pattern=%s, theme=%s)",
            pattern,
            theme_key,
        )

    except Exception as exc:
        logger.error("[Help16] Критическая ошибка: %s", exc, exc_info=True)
        await send_solution_error(
            callback,
            bot,
            f"Не удалось собрать подсказку: {exc}",
        )
