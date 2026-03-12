# utils/telegram_file_cache.py

from aiogram.types import FSInputFile
from pathlib import Path

FILE_CACHE = {}


async def send_cached_photo(bot, chat_id, path: Path):
    key = str(path)

    if key in FILE_CACHE:
        print(f"📦 CACHE HIT: {path}")
        return await bot.send_photo(
            chat_id=chat_id,
            photo=FILE_CACHE[key]
        )

    print(f"⬆️ UPLOAD IMAGE: {path}")

    msg = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(str(path))
    )

    FILE_CACHE[key] = msg.photo[-1].file_id

    return msg
