import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN non trouvé")

# ===== CONFIG ULTRA PRUDENT =====
INITIAL_CAPITAL = 30000
BET_PERCENT = 0.03
STOP_LOSS_PERCENT = 0.15
TARGET_PERCENT = 0.20

# ===== STOCKAGE UTILISATEUR =====
users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "capital": INITIAL_CAPITAL,
            "loss_streak": 0,
            "wins": 0,
            "losses": 0
        }
    return users[user_id]

# ===== MENU PRINCIPAL =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Mines (3 mines)", callback_data="mines")],
        [InlineKeyboardButton("🚀 Lucky Jet (Ultra Safe)", callback_data="lucky")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💎 BOT CASINO ULTRA PRUDENT\n"
        "Capitale: 30 000 FCFA\n"
        "Mise: 3%\n\n"
        "Choisis un mode 👇",
        reply_markup=reply_markup
    )

# ===== MINES MODE =====
async def mines_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)

    bet = int(user["capital"] * BET_PERCENT)

    if user["loss_streak"] >= 2:
        await query.edit_message_text("⛔ Pause automatique après 2 pertes.")
        return

    if user["capital"] <= INITIAL_CAPITAL * (1 - STOP_LOSS_PERCENT):
        await query.edit_message_text("🛑 Stop Loss atteint.")
        return

    result = random.choice(["win", "lose"])

    if result == "win":
        gain = int(bet * 1.5)
        user["capital"] += gain
        user["wins"] += 1
        user["loss_streak"] = 0
        message = f"💎 SAFE ! +{gain} FCFA\nCapital: {user['capital']}"
    else:
        user["capital"] -= bet
        user["losses"] += 1
        user["loss_streak"] += 1
        message = f"💣 Mine ! -{bet} FCFA\nCapital: {user['capital']}"

    await query.edit_message_text(message)

# ===== LUCKY JET MODE =====
async def lucky_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)
    bet = int(user["capital"] * BET_PERCENT)

    if user["loss_streak"] >= 2:
        await query.edit_message_text("⛔ Pause automatique après 2 pertes.")
        return

    crash_point = round(random.uniform(1.1, 2.5), 2)
    stop_auto = 1.6

    if crash_point >= stop_auto:
        gain = int(bet * stop_auto)
        user["capital"] += gain
        user["wins"] += 1
        user["loss_streak"] = 0
        message = f"🚀 Cashout à {stop_auto}x\n+{gain} FCFA\nCapital: {user['capital']}"
    else:
        user["capital"] -= bet
        user["losses"] += 1
        user["loss_streak"] += 1
        message = f"💥 Crash à {crash_point}x\n-{bet} FCFA\nCapital: {user['capital']}"

    await query.edit_message_text(message)

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(mines_game, pattern="mines"))
    app.add_handler(CallbackQueryHandler(lucky_game, pattern="lucky"))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()