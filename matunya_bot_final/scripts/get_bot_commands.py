# get_bot_commands.py
import os, asyncio
from aiogram import Bot
from aiogram.types import BotCommandScopeDefault, BotCommandScopeAllPrivateChats

BOT_TOKEN = os.getenv("BOT_TOKEN") or "<вставь_сюда_токен>"

async def main():
    bot = Bot(BOT_TOKEN)

    print("— Получаю команды (Default scope)…")
    cmds_default = await bot.get_my_commands(scope=BotCommandScopeDefault())
    print([f"/{c.command} — {c.description}" for c in cmds_default])

    print("— Получаю команды (AllPrivateChats)…")
    cmds_private = await bot.get_my_commands(scope=BotCommandScopeAllPrivateChats())
    print([f"/{c.command} — {c.description}" for c in cmds_private])

    print("— Проверяю тип меню-кнопки…")
    menu = await bot.get_chat_menu_button()
    print(menu)

    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())