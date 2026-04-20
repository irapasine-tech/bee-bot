import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")

API_URL = "https://bee-api.onrender.com"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🐝 Бот пасеки активен\nНапиши: Улей 3: расплод, мёд")


@dp.message()
async def handler(message: types.Message):
    try:
        r = requests.post(
            f"{API_URL}/add",
            json={
                "hive": 3,
                "text": message.text
            }
        )

        data = r.json()

        await message.answer(
            f"🐝 Улей {data['hive']}\n"
            f"📊 Принято: {data['text']}"
        )

    except Exception as e:
        await message.answer(f"Ошибка API: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
