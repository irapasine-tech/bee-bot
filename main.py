import asyncio
import logging
import os
from collections import defaultdict
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

hives = defaultdict(list)


def save_record(hive, text):
    hives[hive].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "text": text
    })


# 🤖 НАСТОЯЩИЙ AI АНАЛИЗ
def ai_analyze(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты опытный пчеловод-эксперт. "
                        "Анализируй состояние улья по описанию. "
                        "Дай: 1) состояние семьи 2) риски 3) рекомендации."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.4
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ AI недоступен: {str(e)}"


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🐝 Бот пасеки v7 (AI режим)\n\n"
        "Пиши:\n"
        "Улей 3: много расплода, мёд, спокойные пчёлы"
    )


@dp.message(Command("ulya"))
async def history(message: types.Message):
    try:
        hive = int(message.text.split()[1])
    except:
        await message.answer("Укажи: /ulya 3")
        return

    if hive not in hives:
        await message.answer("📭 нет данных")
        return

    text = f"🐝 Улей {hive}\n\n"

    for r in hives[hive][-5:]:
        text += f"{r['time']} → {r['text']}\n"

    await message.answer(text)


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

    ai_result = ai_analyze(text)

    reply = f"🐝 Улей {hive if hive else '?'}\n\n"
    reply += "🤖 AI-АНАЛИЗ:\n"
    reply += ai_result

    if hive:
        reply += f"\n\n📊 записей: {len(hives[hive])}"

    await message.answer(reply)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
