# set_bot_commands.py
import asyncio
import os
from aiogram import Bot
from aiogram.types import BotCommand
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    bot = Bot(token=BOT_TOKEN)

    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Обратиться в поддержку"),
        BotCommand(command="privacy", description="Политика конфиденциальности"),
        BotCommand(command="public_offer", description="Публичная оферта"),
    ]

    await bot.set_my_commands(commands)
    print("✅ Команды установлены!")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())