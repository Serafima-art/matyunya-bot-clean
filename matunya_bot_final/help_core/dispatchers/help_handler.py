"""
Главный диспетчер системы помощи (версия с HelpRegistry).

Реализует модель "Одно Окно" через реестр HELP_ROUTERS.
Каждое задание имеет собственный help_handler_X.py, где X — номер задания.

Автор: Матюня 🤖
"""

import logging
import importlib
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from matunya_bot_final.core.callbacks.tasks_callback import TaskCallback

logger = logging.getLogger(__name__)
solution_router = Router(name="help_dispatcher")

# ==============================================================
# 📘 РЕЕСТР HELP-ХЕНДЛЕРОВ (HelpRegistry)
# Ключ — номер задания, значение — полный путь к функции handle_task_X_help
# ==============================================================

HELP_ROUTERS = {
    # --- Готовые обработчики ---
    1-5: "matunya_bot_final.help_core.dispatchers.task_1_5.handle_group_1_5_help.handle_group_1_5_help",
    11: "matunya_bot_final.help_core.dispatchers.task_11.help_handler_11.handle_task_11_help",
    20: "matunya_bot_final.help_core.dispatchers.task_20.help_handler_20.handle_task_20_help",

    # --- Будущие задания ---
    # 6:  "matunya_bot_final.help_core.dispatchers.task_6.help_handler_6.handle_task_6_help",
    # 7:  "matunya_bot_final.help_core.dispatchers.task_7.help_handler_7.handle_task_7_help",
    # 8:  "matunya_bot_final.help_core.dispatchers.task_8.help_handler_8.handle_task_8_help",
    # 9:  "matunya_bot_final.help_core.dispatchers.task_9.help_handler_9.handle_task_9_help",
    # 10: "matunya_bot_final.help_core.dispatchers.task_10.help_handler_10.handle_task_10_help",
    # 12: "matunya_bot_final.help_core.dispatchers.task_12.help_handler_12.handle_task_12_help",
    # ...
    # Просто раскомментируй нужную строку, когда появится соответствующий файл.
}


# ==============================================================
# 🧩 ГЛАВНЫЙ ОБРАБОТЧИК "🆘 ПОМОЩЬ"
# ==============================================================

@solution_router.callback_query(TaskCallback.filter(F.action == "request_help"))
async def handle_help_request(callback: CallbackQuery, callback_data: TaskCallback, bot: Bot, state: FSMContext):
    """
    Универсальный диспетчер помощи.
    Определяет номер задания и вызывает соответствующий help-handler через HELP_ROUTERS.
    """
    try:
        task_type = callback_data.question_num or callback_data.task_id
        if task_type is None:
            await callback.answer("Неизвестный тип задания 😔")
            return

        # Поиск соответствующего обработчика
        handler_path = HELP_ROUTERS.get(task_type)
        if not handler_path:
            await callback.answer(f"Помощь для задания №{task_type} пока не реализована 😔")
            return

        # Динамический импорт нужного обработчика
        module_name, func_name = handler_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        handler_func = getattr(module, func_name)

        # Вызов обработчика
        await handler_func(callback, callback_data, bot, state)
        logger.info(f"[HelpDispatcher] Вызван хендлер помощи для задания №{task_type}")

    except ModuleNotFoundError as e:
        logger.error(f"[HelpDispatcher] Не найден модуль обработчика: {e}")
        await callback.answer(f"❌ Помощь для задания №{task_type} пока не готова.")

    except AttributeError as e:
        logger.error(f"[HelpDispatcher] Не найдена функция обработчика: {e}")
        await callback.answer(f"⚠️ Некорректный обработчик для задания №{task_type}.")

    except Exception as e:
        logger.error(f"[HelpDispatcher] Ошибка при вызове помощи: {e}")
        await callback.answer("Произошла ошибка при вызове помощи.")
