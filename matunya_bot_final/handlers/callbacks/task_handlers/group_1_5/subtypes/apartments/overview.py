from aiogram.types import FSInputFile
from pathlib import Path


async def send_overview_block_apartments(bot, state, chat_id, task_1_5_data):

    variant = task_1_5_data
    image_path = Path(variant["image"])

    photo = FSInputFile(image_path)

    await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption="🧩 План квартиры"
    )
    
