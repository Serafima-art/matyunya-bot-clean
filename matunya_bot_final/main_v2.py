import os
import asyncio
import logging
from pathlib import Path

# --- Загрузка .env из корня проекта ---
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent  # поднимаемся из matunya_bot_final/
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)
# --------------------------------------
from flask import Flask

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError

# Импортируем компоненты БД в начале
from matunya_bot_final.utils.db_manager import setup_database, init_db, close_database
from matunya_bot_final.loader import TASKS_DB, load_all_tasks


# --- опционально: заглушка Flask для хостинга (локально не нужна) ---
def run_flask():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Матюня работает 🧮"

    app.run(host="0.0.0.0", port=10000)


async def main():
    logging.basicConfig(level=logging.INFO)

    # 1) .env
    load_dotenv(Path(__file__).resolve().parent / ".env")
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN не найден в .env")

    # 2) ПЕРВЫМ ДЕЛОМ: Настройка и инициализация базы данных
    logging.info("Настройка базы данных...")
    engine, session_maker = await setup_database()

    try:
        await init_db(engine)
        logging.info("База данных успешно инициализирована")
    except Exception as e:
        logging.error(f"Критическая ошибка при инициализации БД: {e}")
        return  # Прерываем запуск бота, если БД не инициализировалась

    # 2.5) Загрузка всех задач из JSON-баз
    logging.info("Загрузка складских JSON-баз...")
    load_all_tasks()
    logging.info("Все базы задач загружены.")

    # 3) ТОЛЬКО ПОСЛЕ настройки БД импортируем роутеры
    logging.info("Импорт роутеров...")
    from matunya_bot_final.handlers import routers              # внутри уже есть start_router и остальные

    # 4) Bot & Dispatcher с передачей session_maker как keyword-аргумента
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(session_maker=session_maker)
    logging.info("Диспетчер создан с session_maker")

    # 5) Подключаем роутеры (порядок важен)
    # сначала все из handlers (там start_router уже первым стоит в списке)
    for r in routers:
        dp.include_router(r)

    # help_router — строго последним включен в handlers\__init__.py
    # dp.include_router(help_handlers.router)  # включай, если нужен legacy-режим

    # 6) Сбрасываем webhook и висячие апдейты
    await bot.delete_webhook(drop_pending_updates=True)

    # 7) Надёжный polling с автоперезапуском
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
                # закрываем сессию при каждом цикле
                await bot.session.close()
    finally:
        # Закрываем базу данных при завершении работы
        await close_database(engine)
        logging.info("Приложение завершено")


if __name__ == "__main__":
    asyncio.run(main())
