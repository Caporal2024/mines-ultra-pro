import os
import json
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")  # 🔐 Li soti nan Railway Variables

if not TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

users = {}

def load_data():
    global users
    try:
        with open("data.json", "r") as f:
            users = json.load(f)
    except:
        users = {}

def save_data():
    with open("data.json", "w") as f:
        json.dump(users, f)

def init_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {
            "capital": 123.0,
            "wins": 0,
            "losses": 0,
            "ai_mode": "NORMAL"
        }

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎲 Dice", callback_data="dice")],
        [InlineKeyboardButton("🎰 Slot", callback_data="slot")],
        [InlineKeyboardButton("✈️ Jet", callback_data="jet")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    init_user(user_id)
    await update.message.reply_text("🎰 ULTRA CASINO READY", reply_markup=main_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    init_user(user_id)
    user = users[user_id]

    if query.data == "dice":
        roll = random.randint(1, 6)
        if roll >= 4:
            user["capital"] += 5
            user["wins"] += 1
        else:
            user["capital"] -= 5
            user["losses"] += 1

    elif query.data == "slot":
        symbols = ["🍒", "🍋", "🔔", "💎"]
        final_spin = [random.choice(symbols) for _ in range(3)]
        if final_spin[0] == final_spin[1] == final_spin[2]:
            user["capital"] += 10
            user["wins"] += 1
        else:
            user["capital"] -= 5
            user["losses"] += 1

    elif query.data == "jet":
        multiplier = round(random.uniform(1.1, 3.0), 2)
        if multiplier >= 1.5:
            user["capital"] += 5
        else:
            user["capital"] -= 5

    elif query.data == "stats":
        text = f"💰 {user['capital']}\n🏆 {user['wins']} Wins\n❌ {user['losses']} Losses"
        await query.edit_message_text(text, reply_markup=main_menu())
        save_data()
        return

    save_data()
    await query.edit_message_text("🎰 Game Played", reply_markup=main_menu())

if __name__ == "__main__":
    load_data()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()