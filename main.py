import os
import random
import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")

INITIAL_CAPITAL = 30000
BET_PERCENT = 0.03
STOP_LOSS_PERCENT = 0.15
PAUSE_DURATION = 600  # 10 minutes

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "capital": INITIAL_CAPITAL,
            "loss_streak": 0,
            "pause_until": 0
        }
    return users[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    keyboard = [
        [InlineKeyboardButton("🎮 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("🚀 Lucky Jet LIVE", callback_data="lucky")]
    ]

    await update.message.reply_text(
        f"💎 CASINO ULTRA PRUDENT\n"
        f"Capital: {user['capital']} FCFA\n"
        f"Mise: 3%\n\nChoisis 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    user["loss_streak"] = 0
    user["pause_until"] = 0
    await update.message.reply_text("✅ Pause réinitialisée.")

def check_pause(user):
    if time.time() < user["pause_until"]:
        return True
    return False

async def mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)

    if check_pause(user):
        await query.edit_message_text("⛔ Pause en cours. Attends 10 minutes.")
        return

    bet = int(user["capital"] * BET_PERCENT)
    result = random.choice(["win", "lose"])

    if result == "win":
        gain = int(bet * 1.5)
        user["capital"] += gain
        user["loss_streak"] = 0
        message = f"💎 Safe +{gain} FCFA\nCapital: {user['capital']}"
    else:
        user["capital"] -= bet
        user["loss_streak"] += 1
        message = f"💣 Mine -{bet} FCFA\nCapital: {user['capital']}"

        if user["loss_streak"] >= 2:
            user["pause_until"] = time.time() + PAUSE_DURATION
            message += "\n\n⛔ Pause 10 minutes activée."

    await query.edit_message_text(message)

async def lucky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)

    if check_pause(user):
        await query.edit_message_text("⛔ Pause en cours. Attends 10 minutes.")
        return

    bet = int(user["capital"] * BET_PERCENT)
    crash = round(random.uniform(1.1, 2.5), 2)
    stop_auto = 1.6

    if crash >= stop_auto:
        gain = int(bet * stop_auto)
        user["capital"] += gain
        user["loss_streak"] = 0
        message = f"🚀 Cashout 1.6x\n+{gain} FCFA\nCapital: {user['capital']}"
    else:
        user["capital"] -= bet
        user["loss_streak"] += 1
        message = f"💥 Crash {crash}x\n-{bet} FCFA\nCapital: {user['capital']}"

        if user["loss_streak"] >= 2:
            user["pause_until"] = time.time() + PAUSE_DURATION
            message += "\n\n⛔ Pause 10 minutes activée."

    await query.edit_message_text(message)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(mines, pattern="mines"))
    app.add_handler(CallbackQueryHandler(lucky, pattern="lucky"))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()