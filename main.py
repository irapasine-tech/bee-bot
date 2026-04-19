import asyncio
import logging
import os
from collections import defaultdict
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🧠 память: улей -> список записей (с датой)
hives = defaultdict(list)


# 📅 сохранить запись
def save_record(hive, text):
    hives[hive].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "text": text
    })


# 🧠 анализ одной записи
def analyze(text):
    t = text.lower()
    result = []

    brood = "расплод" in t
    strong_brood = "много расплода" in t or "сильный расплод" in t

    honey = "мёд" in t or "мед" in t
    queen = "матк" in t
    aggression = "агресс" in t

    if strong_brood:
        result.append("🔥 Сильная семья (активный расплод)")
    elif brood:
        result.append("📈 Развитие семьи")

    if honey:
        result.append("🍯 Запасы мёда")

    if queen:
        result.append("👑 Контроль матки обязателен")

    if aggression:
        result.append("⚠️ Агрессия / стресс")

    if strong_brood and honey:
        result.append("🟢 Сильная продуктивная семья")
    elif brood and not honey:
        result.append("🟡 Нужен контроль кормов")
    elif aggression:
        result.append("🔴 Нестабильная семья")

    if not result:
        result.append("📌 Записано без отклонений")

    return "\n".join(result)


# 📊 анализ динамики улья
def analyze_history(hive):
    records = hives[hive]

    if len(records) < 2:
        return "📊 Пока мало данных для динамики"

    last = records[-1]["text"].lower()
    prev = records[-2]["text"].lower()

    trend = []

    if "расплод" in last and "расплод" not in prev:
        trend.append("📈 Появился расплод (рост семьи)")

    if "мёд" in prev and "мёд" not in last:
        trend.append("⚠️ Снижение запасов мёда")

    if not trend:
        trend.append("📊 Существенных изменений нет")

    return "\n".join(trend)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🐝 Бот пасеки v3 активен\n\n"
        "Формат:\n"
        "Улей 3: расплод, мёд, спокойные пчёлы\n\n"
        "Команда:\n"
        "/ulya 3 — история"
    )


# 🐝 основной обработчик
@dp.message()
async def handler(message: types.Message):
    text = message.text

    hive = None

    if "Улей" in text:
        try:
            hive = int(text.split("Улей")[1].split(":")[0].strip())
        except:
            hive = None

    if hive:
        save_record(hive, text)

    reply = f"🐝 Улей {hive if hive else '?'}\n\n"
    reply += analyze(text)

    if hive:
        reply += f"\n\n📊 Всего записей: {len(hives[hive])}"
        reply += "\n" + analyze_history(hive)

    await message.answer(reply)


# 📅 история улья
@dp.message(Command("ulya"))
async def history(message: types.Message):
    try:
        hive = int(message.text.split()[1])
    except:
        await message.answer("Укажи номер: /ulya 3")
        return

    if hive not in hives:
        await message.answer("📭 Нет данных по этому улью")
        return

    text = f"🐝 История улья {hive}\n\n"

    for r in hives[hive][-5:]:
        text += f"{r['time']} → {r['text']}\n"

    await message.answer(text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
