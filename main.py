import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# GPT-функция
async def ask_gpt(message_text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — Матюня, добрый и заботливый репетитор по математике для детей 9 класса. "
                        "Ты объясняешь материал просто, тепло и дружелюбно, как друг или старший брат/сестра. "
                        "Всегда поддерживаешь ученика, даже если он не понимает с первого раза. "
                        "Пиши без канцелярита — живым, понятным, человечным языком. "
                        "Объясняй шаг за шагом, вдохновляй и помогай поверить в себя. "
                        "Используй примеры из жизни, сравнения, метафоры. "
                        "Не критикуй. Всегда отвечай на русском языке."
                    )
                },
                {"role": "user", "content": message_text}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при обращении к GPT: {e}"

# Ответ на команду /start
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Я Матюня, твой добрый репетитор по математике 🧮 Спрашивай что угодно!")

# Ответ на обычные сообщения
@dp.message()
async def handle_message(message: Message):
    reply = await ask_gpt(message.text)
    await message.answer(reply)

# Запуск бота
if __name__ == "__main__":
    print("Матюня запущен на aiogram!")
    asyncio.run(dp.start_polling(bot))