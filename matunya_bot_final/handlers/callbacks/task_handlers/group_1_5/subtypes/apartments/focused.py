from pathlib import Path


async def send_focused_task_block_apartments(
    bot,
    state,
    chat_id,
    task_1_5_data,
    question_num
):

    variant = task_1_5_data

    image_path = Path(variant["image"])

    await bot.send_photo(
        chat_id=chat_id,
        photo=image_path.open("rb"),
        caption="🧩 План квартиры"
    )
