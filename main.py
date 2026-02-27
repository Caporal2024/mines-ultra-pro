import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
import asyncio

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = {}

# -------- START --------
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"balance": 10000}
    await message.answer(
        f"🔥 PRO MAX GAME 🔥\n\n"
        f"👤 ID: {user_id}\n"
        f"💰 Solde: {users[user_id]['balance']} FCFA\n\n"
        f"/mines - Jouer Mines\n"
        f"/wheel - Roue de la fortune"
    )

# -------- MINES --------
games = {}

@dp.message(Command("mines"))
async def mines(message: types.Message):
    user_id = message.from_user.id

    mines_positions = random.sample(range(25), 5)
    games[user_id] = {
        "mines": mines_positions,
        "opened": [],
        "multiplier": 1
    }

    builder = InlineKeyboardBuilder()
    for i in range(25):
        builder.add(InlineKeyboardButton(text="⬜", callback_data=f"cell_{i}"))

    builder.adjust(5)
    builder.row(
        InlineKeyboardButton(text="💰 CASHOUT", callback_data="cashout")
    )

    await message.answer("🎮 Mines 5x5\nChoisis une case :", reply_markup=builder.as_markup())

@dp.callback_query()
async def game_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id not in games:
        return

    data = call.data

    if data.startswith("cell_"):
        index = int(data.split("_")[1])

        if index in games[user_id]["mines"]:
            await call.message.edit_text("💣 PENALTY ! Tu as perdu.")
            del games[user_id]
            return
        else:
            games[user_id]["multiplier"] += 0.5
            games[user_id]["opened"].append(index)
            await call.answer("💎 Safe !")

    if data == "cashout":
        gain = int(1000 * games[user_id]["multiplier"])
        users[user_id]["balance"] += gain
        await call.message.edit_text(f"💰 Gain sécurisé: {gain} FCFA")
        del games[user_id]

# -------- WHEEL --------
@dp.message(Command("wheel"))
async def wheel(message: types.Message):
    user_id = message.from_user.id
    prize = random.choice([0, 500, 1000, 2000, 5000])

    users[user_id]["balance"] += prize

    await message.answer(
        f"🎡 Résultat de la roue:\n\n"
        f"💰 Gain: {prize} FCFA\n"
        f"💼 Nouveau solde: {users[user_id]['balance']} FCFA"
    )

# -------- RUN --------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())