import asyncio
import logging
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# 🔑 токен Telegram бота (Render ENV: BOT_TOKEN)
TOKEN = os.getenv("BOT_TOKEN")

# 🌐 URL твоего backend API (bee-api)
API_URL = "https://bee-api.onrender.com"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# 📊 команда старт
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🐝 Бот пасеки активен\nНапиши: Улей 3: расплод, мёд")


# 📊 анализ улья
@dp.message()
async def handle(message: types.Message):
    text = message.text

    try:
        response = requests.post(
            f"{API_URL}/add",
            params={
                "hive": 3,
                "text": text
            }
        )

        data = response.json()

        answer = f"""🐝 Улей {data['hive']}

📊 Состояние: {data['score']}/100
"""

        for a in data["advice"]:
            answer += f"{a}\n"

        await message.answer(answer)

    except Exception as e:
        await message.answer(f"Ошибка API: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
