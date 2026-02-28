import os
import random
import asyncio
import threading
import sqlite3
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ================== CONFIG ==================
TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 8080))
ADMIN_ID = 8094967191  # ⚠️ Mets ton Telegram ID ici

if not TOKEN:
    raise ValueError("TOKEN not found")

# ================== WEB SERVER ==================
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Casino Bot Running 💎"

def run_web():
    app_web.run(host="0.0.0.0", port=PORT)

# ================== DATABASE ==================
conn = sqlite3.connect("casino.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 1000
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 1000))
        conn.commit()
        return {"balance": 1000}

    return {"balance": user[0]}

def update_balance(user_id, new_balance):
    cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"👑 CASINO PRO\n\n"
        f"💰 Solde: {user['balance']} FCFA\n\n"
        "Commandes:\n"
        "/luckyjet montant\n"
        "/mines montant\n"
        "/stats"
    )

# ================== STATS ==================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"📊 STATS\n\n💰 Solde: {user['balance']} FCFA"
    )

# ================== LUCKY JET ==================
async def luckyjet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not context.args:
        await update.message.reply_text("Utilise: /luckyjet montant")
        return

    bet = int(context.args[0])

    if bet > user["balance"]:
        await update.message.reply_text("❌ Solde insuffisant")
        return

    update_balance(user_id, user["balance"] - bet)

    multiplier = 1.0
    crashed = False

    keyboard = [[InlineKeyboardButton("🛑 CASHOUT", callback_data="cashout")]]

    message = await update.message.reply_text(
        "🚀 x1.00",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data["bet"] = bet
    context.user_data["multiplier"] = multiplier
    context.user_data["crashed"] = False

    while not crashed:
        await asyncio.sleep(0.8)
        multiplier += random.uniform(0.1, 0.3)
        context.user_data["multiplier"] = multiplier

        if random.random() < 0.1:
            crashed = True
            context.user_data["crashed"] = True
            await message.edit_text(f"💥 CRASH à x{multiplier:.2f}")
            break

        await message.edit_text(
            f"🚀 x{multiplier:.2f}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("crashed"):
        await query.edit_message_text("💥 Trop tard ! Crash.")
        return

    multiplier = context.user_data["multiplier"]
    bet = context.user_data["bet"]
    user_id = query.from_user.id

    user = get_user(user_id)
    gain = int(bet * multiplier)
    update_balance(user_id, user["balance"] + gain)

    await query.edit_message_text(
        f"💰 CASHOUT à x{multiplier:.2f}\n"
        f"🎉 Gain: {gain} FCFA"
    )

    context.user_data.clear()

# ================== MINES 5x5 ==================
GRID = 5
MINES_COUNT = 5

def generate_board():
    board = ["💎"] * 25
    for pos in random.sample(range(25), MINES_COUNT):
        board[pos] = "💣"
    return board

async def mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not context.args:
        await update.message.reply_text("Utilise: /mines montant")
        return

    bet = int(context.args[0])

    if bet > user["balance"]:
        await update.message.reply_text("❌ Solde insuffisant")
        return

    update_balance(user_id, user["balance"] - bet)

    board = generate_board()
    context.user_data["board"] = board
    context.user_data["bet"] = bet
    context.user_data["safe"] = 0

    keyboard = []
    for i in range(5):
        row = []
        for j in range(5):
            row.append(InlineKeyboardButton("❓", callback_data=f"mine_{i*5+j}"))
        keyboard.append(row)

    await update.message.reply_text(
        "💣 Mines 5x5 - Clique une case",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    board = context.user_data["board"]
    bet = context.user_data["bet"]
    user_id = query.from_user.id
    user = get_user(user_id)

    index = int(query.data.split("_")[1])

    if board[index] == "💣":
        await query.edit_message_text("💥 BOOM ! Tu as perdu.")
        context.user_data.clear()
        return

    context.user_data["safe"] += 1
    gain = int(bet * (1 + context.user_data["safe"] * 0.3))
    update_balance(user_id, user["balance"] + gain)

    await query.edit_message_text(
        f"💎 Safe !\n🎉 Gain: {gain} FCFA"
    )

# ================== ADMIN ==================
async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    amount = int(context.args[1])

    user = get_user(user_id)
    update_balance(user_id, user["balance"] + amount)

    await update.message.reply_text("✅ Dépôt effectué")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    amount = int(context.args[1])

    user = get_user(user_id)
    update_balance(user_id, user["balance"] - amount)

    await update.message.reply_text("💸 Retrait effectué")

# ================== MAIN ==================
def main():
    threading.Thread(target=run_web).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("luckyjet", luckyjet))
    app.add_handler(CommandHandler("mines", mines))
    app.add_handler(CallbackQueryHandler(handle_mine, pattern="^mine_"))
    app.add_handler(CallbackQueryHandler(handle_cashout, pattern="^cashout$"))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(CommandHandler("withdraw", withdraw))

    app.run_polling()

if __name__ == "__main__":
    main()