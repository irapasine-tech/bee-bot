import asyncio
import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# 🔑 токен бота
TOKEN = os.getenv("BOT_TOKEN")

# 🌐 адрес твоего API (ВАЖНО — вставь свой Render URL)
API_URL = "https://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"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# 💾 сохранение через API
def save(hive, text):
    try:
        response = requests.post(
            f"{API_URL}/add",
            params={
                "hive": hive,
                "text": text
            }
        )
        data = response.json()
        return data.get("score", 50)

    except Exception as e:
        print("Ошибка API:", e)
        return 50


# 📊 получить статистику
def get_stats():
    try:
        response = requests.get(f"{API_URL}/hives")
        return response.json()
    except:
        return []


# 🟢 старт
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🐝 Бот пасеки v9\n\n"
        "Пиши:\n"
        "Улей 3: расплод, мёд\n\n"
        "Команды:\n"
        "/stats"
    )


# 📊 статистика
@dp.message(Command("stats"))
async def stats(message: types.Message):
    data = get_stats()

    if not data:
        await message.answer("📭 нет данных")
        return

    text = "📊 Пасека:\n\n"

    for hive, score in data:
        text += f"Улей {hive} → {score}\n"

    await message.answer(text)


# 🐝 основной обработчик
@dp.message()
async def handler(message: types.Message):
    text = message.text

    hive = None

    # 📌 определяем номер улья
    if "Улей" in text:
        try:
            hive = int(text.split("Улей")[1].split(":")[0].strip())
        except:
            hive = None

    if not hive:
        await message.answer("Напиши: Улей 3: ...")
        return

    # 💾 отправляем в API
    score = save(hive, text)

    reply = f"🐝 Улей {hive}\n\n"
    reply += f"📊 Состояние: {score}/100\n"

    if score >= 80:
        reply += "🟢 Сильная семья"
    elif score >= 60:
        reply += "🟡 Нормальная семья"
    elif score >= 40:
        reply += "🟠 Ослабленная семья"
    else:
        reply += "🔴 Критическое состояние"

    await message.answer(reply)


# 🚀 запуск
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
