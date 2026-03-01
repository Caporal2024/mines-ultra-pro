import json
import os
import random
import statistics
import matplotlib.pyplot as plt

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= CONFIG =================

TOKEN = "PUT_YOUR_TOKEN_HERE"
START_BALANCE = 100000
STOP_LOSS = 10000
TARGET_PROFIT = 15000
BET_PERCENT = 0.02
DATA_FILE = "user_data.json"

# ==========================================

# -------- DATABASE --------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_user(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "balance": START_BALANCE,
            "start_balance": START_BALANCE,
            "history": [],
            "mode": "SIM"
        }
        save_data(data)
    return data[str(user_id)]

def update_user(user_id, user_data):
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)

# -------- MENU --------

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🎮 Simulation", callback_data="mode_sim"),
            InlineKeyboardButton("🔴 LIVE", callback_data="mode_live"),
        ],
        [
            InlineKeyboardButton("🚀 Jouer", callback_data="play"),
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
        ],
        [
            InlineKeyboardButton("💰 Balance", callback_data="balance"),
            InlineKeyboardButton("📈 Graph", callback_data="graph"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

# -------- IA --------

def analyze(history):
    if len(history) < 5:
        return "Pas assez de données..."

    recent = history[-30:]
    avg = statistics.mean(recent)
    low = sum(1 for x in recent if x < 1.5)
    high = sum(1 for x in recent if x > 5)

    if low > high:
        strat = "SAFE 1.40x"
    else:
        strat = "NORMAL 2x"

    return f"""
💜 GOD MODE ANALYSE 💜

Tours analysés: {len(recent)}
Moyenne: {round(avg,2)}x
Crash <1.5x: {low}
Crash >5x: {high}

🎯 Stratégie: {strat}
"""

# -------- COMMANDES --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    await update.message.reply_text(
        "💜 LUCKYJET SCHOOL PRO 💜",
        reply_markup=main_menu()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)

    if query.data == "mode_sim":
        user["mode"] = "SIM"
        update_user(query.from_user.id, user)
        await query.edit_message_text("🎮 Mode Simulation", reply_markup=main_menu())

    elif query.data == "mode_live":
        user["mode"] = "LIVE"
        update_user(query.from_user.id, user)
        await query.edit_message_text("🔴 Mode LIVE\nEnvoie juste un nombre (ex: 2.34)", reply_markup=main_menu())

    elif query.data == "play":
        if user["mode"] != "SIM":
            await query.answer("Active Simulation", show_alert=True)
            return

        bet = user["balance"] * BET_PERCENT
        crash = round(random.uniform(1.0, 10.0), 2)
        user["history"].append(crash)

        if crash >= 2:
            user["balance"] += bet * crash - bet
        else:
            user["balance"] -= bet

        update_user(query.from_user.id, user)

        await query.edit_message_text(
            f"🎰 {crash}x\n💰 {round(user['balance'],2)} FCFA",
            reply_markup=main_menu()
        )

    elif query.data == "stats":
        await query.edit_message_text(
            analyze(user["history"]),
            reply_markup=main_menu()
        )

    elif query.data == "balance":
        await query.edit_message_text(
            f"💰 Balance: {round(user['balance'],2)} FCFA",
            reply_markup=main_menu()
        )

    elif query.data == "graph":
        if len(user["history"]) < 2:
            await query.answer("Pas assez de données", show_alert=True)
            return

        balances = []
        balance = user["start_balance"]

        for m in user["history"]:
            bet = balance * BET_PERCENT
            if m >= 2:
                balance += bet * m - bet
            else:
                balance -= bet
            balances.append(balance)

        plt.figure()
        plt.plot(balances)
        plt.title("Evolution Bankroll")
        plt.xlabel("Tours")
        plt.ylabel("Balance")
        plt.savefig("graph.png")
        plt.close()

        await context.bot.send_photo(
            chat_id=query.from_user.id,
            photo=open("graph.png", "rb")
        )

# -------- LIVE RAPIDE --------

async def live_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if user["mode"] != "LIVE":
        return

    try:
        value = float(update.message.text)
        user["history"].append(value)
        update_user(update.effective_user.id, user)
        await update.message.reply_text("🔴 Multiplicateur ajouté", reply_markup=main_menu())
    except:
        pass

# -------- MAIN --------

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, live_input))

    app.run_polling()

if __name__ == "__main__":
    main()