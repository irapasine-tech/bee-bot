import asyncio
import logging
import os
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI
import matplotlib.pyplot as plt

# 🔑 ключи
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🗄 БД
conn = sqlite3.connect("hives.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS records (
    hive INTEGER,
    text TEXT,
    score INTEGER,
    time TEXT
)
""")
conn.commit()


# 📊 скоринг
def score(text):
    t = text.lower()
    s = 50

    if "расплод" in t: s += 15
    if "много расплода" in t: s += 25
    if "мёд" in t: s += 10
    if "матк" in t: s -= 20
    if "агресс" in t: s -= 25

    return max(0, min(100, s))


# 💾 сохранить
def save(hive, text):
    s = score(text)
    cur.execute("INSERT INTO records VALUES (?, ?, ?, ?)",
                (hive, text, s, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    return s


# 🤖 AI анализ
def ai(text):
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Ты профессиональный пчеловод. Дай: состояние, риски, действия."},
                {"role": "user", "content": text}
            ]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI ошибка: {e}"


# 🔮 прогноз
def forecast(hive):
    cur.execute("SELECT score FROM records WHERE hive=? ORDER BY time DESC LIMIT 3", (hive,))
    rows = cur.fetchall()

    if len(rows) < 2:
        return "📊 мало данных"

    scores = [r[0] for r in rows]

    if scores[0] > 80 and scores[1] > 80:
        return "🔮 возможное роение"
    if scores[0] < 40:
        return "🔮 риск ослабления"
    return "🔮 стабильное развитие"


# 📊 график
def make_chart(hive):
    cur.execute("SELECT time, score FROM records WHERE hive=?", (hive,))
    rows = cur.fetchall()

    if len(rows) < 2:
        return None

    times = [r[0] for r in rows]
    scores = [r[1] for r in rows]

    plt.figure()
    plt.plot(scores)
    plt.title(f"Hive {hive}")
    plt.savefig(f"hive_{hive}.png")
    plt.close()

    return f"hive_{hive}.png"


# 📊 статистика
def stats():
    cur.execute("SELECT hive, score FROM records")
    data = cur.fetchall()

    if not data:
        return "📭 нет данных"

    hive_scores = {}

    for h, s in data:
        hive_scores.setdefault(h, []).append(s)

    avg = {h: sum(v)/len(v) for h, v in hive_scores.items()}

    best = max(avg, key=avg.get)
    worst = min(avg, key=avg.get)

    return f"🏆 лучший улей: {best}\n⚠️ слабый улей: {worst}"


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🐝 Пасека v8 активна")


@dp.message(Command("stats"))
async def stat_cmd(message: types.Message):
    await message.answer(stats())


@dp.message(Command("chart"))
async def chart(message: types.Message):
    try:
        hive = int(message.text.split()[1])
    except:
        await message.answer("пример: /chart 3")
        return

    file = make_chart(hive)

    if not file:
        await message.answer("📊 мало данных")
        return

    await message.answer_photo(types.FSInputFile(file))


@dp.message()
async def handler(message: types.Message):
    text = message.text

    hive = None
    if "Улей" in text:
        try:
            hive = int(text.split("Улей")[1].split(":")[0].strip())
        except:
            pass

    if not hive:
        await message.answer("Напиши: Улей 3: ...")
        return

    s = save(hive, text)

    reply = f"🐝 Улей {hive}\n\n"
    reply += f"📊 {s}/100\n\n"
    reply += ai(text)
    reply += "\n\n" + forecast(hive)

    await message.answer(reply)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
