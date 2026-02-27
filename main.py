import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

LOSS_LIMIT = -3000
PROFIT_TARGET = 4000
MAX_CONSECUTIVE_LOSSES = 3
BET_AMOUNT = 1000

users = {}
games = {}

def neon(text):
    return f"💜✨ {text} ✨💜"

def check_limits(user_id):
    user = users[user_id]
    profit = user["balance"] - user["start_balance"]

    if profit <= LOSS_LIMIT:
        return "LOSS_LIMIT"
    if profit >= PROFIT_TARGET:
        return "PROFIT_TARGET"
    if user["consecutive_losses"] >= MAX_CONSECUTIVE_LOSSES:
        return "MAX_LOSSES"
    return None

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "start_balance": 10000,
            "wins": 0,
            "losses": 0,
            "consecutive_losses": 0
        }

    await message.answer(
        neon("ULTRA PRO MAX 🎮") + "\n\n"
        f"👤 ID: {user_id}\n"
        f"💰 Solde: {users[user_id]['balance']} FCFA\n\n"
        "/mines\n"
        "/astronaut\n"
        "/apple\n"
        "/stats"
    )

# ---------------- STATS ----------------
@dp.message(Command("stats"))
async def stats(message: types.Message):
    user = users[message.from_user.id]
    profit = user["balance"] - user["start_balance"]

    await message.answer(
        neon("STATISTIQUES 📊") + "\n\n"
        f"💰 Solde: {user['balance']}\n"
        f"📈 Profit session: {profit}\n"
        f"🏆 Victoires: {user['wins']}\n"
        f"💥 Pertes: {user['losses']}"
    )

# ---------------- MINES ----------------
@dp.message(Command("mines"))
async def mines(message: types.Message):
    user_id = message.from_user.id
    limit = check_limits(user_id)
    if limit:
        await message.answer(f"⛔ Jeu bloqué : {limit}")
        return

    if users[user_id]["balance"] < BET_AMOUNT:
        await message.answer("❌ Solde insuffisant.")
        return

    users[user_id]["balance"] -= BET_AMOUNT

    mines_positions = random.sample(range(25), 5)
    games[user_id] = {"mines": mines_positions}

    builder = InlineKeyboardBuilder()
    for i in range(25):
        builder.add(InlineKeyboardButton(text="🟪", callback_data=f"mine_{i}"))
    builder.adjust(5)

    await message.answer(neon("MINES 5x5"), reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("mine_"))
async def mine_click(call: types.CallbackQuery):
    user_id = call.from_user.id
    index = int(call.data.split("_")[1])

    if index in games[user_id]["mines"]:
        users[user_id]["losses"] += 1
        users[user_id]["consecutive_losses"] += 1
        await call.message.edit_text("💣 PERDU")
    else:
        gain = 2000
        users[user_id]["balance"] += gain
        users[user_id]["wins"] += 1
        users[user_id]["consecutive_losses"] = 0
        await call.message.edit_text(f"💎 GAGNÉ {gain} FCFA")

# ---------------- ASTRONAUT ----------------
@dp.message(Command("astronaut"))
async def astronaut(message: types.Message):
    user_id = message.from_user.id
    multiplier = round(random.uniform(1.0, 3.0), 2)
    gain = int(BET_AMOUNT * multiplier)

    users[user_id]["balance"] += gain
    users[user_id]["wins"] += 1
    users[user_id]["consecutive_losses"] = 0

    await message.answer(
        neon("ASTRONAUT 🚀") + "\n\n"
        f"Multiplicateur: x{multiplier}\n"
        f"Gain: {gain} FCFA"
    )

# ---------------- APPLE OF FORTUNE ----------------
@dp.message(Command("apple"))
async def apple(message: types.Message):
    user_id = message.from_user.id
    bomb = random.randint(1, 5)
    choice = random.randint(1, 5)

    if choice == bomb:
        users[user_id]["losses"] += 1
        users[user_id]["consecutive_losses"] += 1
        await message.answer("💣 Mauvaise pomme !")
    else:
        gain = 1500
        users[user_id]["balance"] += gain
        users[user_id]["wins"] += 1
        users[user_id]["consecutive_losses"] = 0
        await message.answer(f"🍎 Bonne pomme ! +{gain} FCFA")

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())