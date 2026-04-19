import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# простая память (пока без базы данных)
hives = {}


def analyze(text):
    t = text.lower()
    result = []

    # 📈 развитие семьи
    if "расплод" in t:
        result.append("📈 Расплод присутствует — семья развивается")

    if "много расплода" in t:
        result.append("🔥 Сильный расплод — активный рост семьи")

    # 👑 матка
    if "матк" in t:
        result.append("👑 Внимание: проверь матку (наличие/качество)")

    # ⚠️ поведение
    if "агресс" in t:
        result.append("⚠️ Агрессия — возможен стресс или проблема с маткой")

    # 🍯 ресурсы
    if "мёд" in t or "мед" in t:
        result.append("🍯 Запасы мёда есть")

    # 🧠 если ничего не найдено
    if not result:
        result.append("📌 Данные записаны, явных рисков не выявлено")

    return "\n".join(result)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🐝 Бот пасеки активен\n\n"
        "Пиши так:\n"
        "Улей 3: много расплода, мёд, пчёлы спокойные"
    )


@dp.message()
async def handler(message: types.Message):
    text = message.text

    hive = None
    if "Улей" in text:
        try:
            hive = int(text.split("Улей")[1].split(":")[0].strip())
        except:
            pass

    if hive:
        hives.setdefault(hive, [])
        hives[hive].append(text)

    reply = f"🐝 Улей {hive if hive else '?'}\n\n"
    reply += analyze(text)

    await message.answer(reply)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
