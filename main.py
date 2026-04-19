import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


def analyze(text):
    t = text.lower()
    res = []

    if "матк" in t:
        res.append("👑 Проверь матку через 5–7 дней")

    if "расплод" in t:
        res.append("📈 Расплод есть — развитие идёт")

    if "агресс" in t:
        res.append("⚠️ Возможна проблема в семье")

    if "мёд" in t or "мед" in t:
        res.append("🍯 Мёд есть — ресурс норм")

    if not res:
        res.append("📌 Записано")

    return "\n".join(res)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🐝 Бот пасеки активен. Пиши: Улей 3: расплод, мёд")


@dp.message()
async def handler(message: types.Message):
    text = message.text

    hive = None
    if "Улей" in text:
        try:
            hive = int(text.split("Улей")[1].split(":")[0].strip())
        except:
            pass

    reply = f"🐝 Улей {hive if hive else '?'}\n\n"
    reply += analyze(text)

    await message.answer(reply)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
