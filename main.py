import asyncio
import logging
import os
from collections import defaultdict
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# 🔑 токен берётся из Render Variables
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🧠 память ульев
hives = defaultdict(list)


# 🧠 АНАЛИЗ СОСТОЯНИЯ УЛЬЯ
def analyze(text):
    t = text.lower()
    result = []

    brood = "расплод" in t
    strong_brood = "много расплода" in t or "сильный расплод" in t

    honey = "мёд" in t or "мед" in t
    queen = "матк" in t
    aggression = "агресс" in t

    # 📈 развитие
    if strong_brood:
        result.append("🔥 Сильная семья (активный расплод)")
    elif brood:
        result.append("📈 Развитие семьи есть")

    # 🍯 ресурсы
    if honey:
        result.append("🍯 Есть запасы мёда")

    # 👑 матка
    if queen:
        result.append("👑 Проверь матку (контроль обязателен)")

    # ⚠️ поведение
    if aggression:
        result.append("⚠️ Агрессия — возможен стресс или проблема в семье")

    # 🚨 итоговая оценка
    if strong_brood and honey:
        result.append("🟢 Состояние: сильная продуктивная семья")
    elif brood and not honey:
        result.append("🟡 Состояние: развивается, нужен контроль кормов")
    elif aggression:
        result.append("🔴 Состояние: нестабильная семья")

    if not result:
        result.append("📌 Данные записаны, отклонений не выявлено")

    return "\n".join(result)


# 🟢 /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🐝 Бот пасеки активен\n\n"
        "Формат записи:\n"
        "Улей 3: много расплода, мёд, спокойные пчёлы"
    )


# 🐝 обработка сообщений
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

    # 🧠 сохраняем историю
    if hive:
        hives[hive].append(text)

    # 📊 ответ
    reply = f"🐝 Улей {hive if hive else '?'}\n\n"
    reply += analyze(text)

    # 📈 статистика
    if hive:
        reply += f"\n\n📊 Записей по улью: {len(hives[hive])}"

    await message.answer(reply)


# 🚀 запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
