# -*- coding: utf-8 -*-
import os
import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError

from matunya_bot_final.utils.db_manager import setup_database, init_db, close_database
from matunya_bot_final.loader import TASKS_DB, load_all_tasks


async def main(bot_token: str):
    """
    Главная точка запуска Матюни.
    Теперь получает bot_token извне — run.py отвечает за выбор env-файла.
    """

    logging.basicConfig(level=logging.INFO)

    # ---------------------------------------
    # 1) Инициализация базы данных
    # ---------------------------------------
    logging.info("Настройка базы данных...")
    engine, session_maker = await setup_database()

    try:
        await init_db(engine)
        logging.info("База данных успешно инициализирована")
    except Exception as e:
        logging.error(f"Критическая ошибка при инициализации БД: {e}")
        return

    # ---------------------------------------
    # 2) Загрузка задач из JSON-баз
    # ---------------------------------------
    logging.info("Загрузка складских JSON-баз...")
    load_all_tasks()
    logging.info("Все базы задач загружены.")

    # ---------------------------------------
    # 3) Импорт роутеров ПОСЛЕ инициализации БД
    # ---------------------------------------
    logging.info("Импорт роутеров...")
    from matunya_bot_final.handlers import routers

    # ---------------------------------------
    # 4) Создание Bot и Dispatcher
    # ---------------------------------------
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(session_maker=session_maker)

    from aiogram.types import BotCommand

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Обратиться в поддержку"),
            BotCommand(command="privacy", description="Политика конфиденциальности"),
            BotCommand(command="public_offer", description="Публичная оферта"),
        ]
    )

    logging.info("Dispatcher создан с session_maker")

    # ---------------------------------------
    # 5) Подключаем все роутеры
    # ---------------------------------------
    for r in routers:
        dp.include_router(r)

    # ---------------------------------------
    # 6) Сбрасываем webhook (на случай миграции между Webhook и Polling)
    # ---------------------------------------
    await bot.delete_webhook(drop_pending_updates=True)

    # ---------------------------------------
    # 7) Старт polling с автоперезапуском
    # ---------------------------------------
    try:
        while True:
            try:
                print("Матюня запускается...")
                await dp.start_polling(bot)

            except TelegramNetworkError as e:
                logging.warning(f"[Polling] Обрыв сети: {e}. Повтор через 2 сек...")
                await asyncio.sleep(2)
                continue

            except (asyncio.CancelledError, KeyboardInterrupt):
                logging.info("[Polling] Остановлено пользователем.")
                break

            except Exception as e:
                logging.exception(f"[Polling] Неожиданная ошибка: {e}. Повтор через 5 сек...")
                await asyncio.sleep(5)
                continue

            finally:
                await bot.session.close()

    finally:
        await close_database(engine)
        logging.info("Приложение завершено.")


# -------------------------------------------------
# Локальный запуск через:
#   python run.py
#   python run.py --dev
# -------------------------------------------------
if __name__ == "__main__":
    raise RuntimeError(
        "Не запускайте main_v2.py напрямую. Используйте run.py!"
    )
