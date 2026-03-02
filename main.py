import logging
import random
import asyncio
import os
import time
from io import BytesIO
import matplotlib.pyplot as plt

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Ajoute TOKEN dans Railway Variables")

logging.basicConfig(level=logging.INFO)

users = {}
active_games = {}

# =========================
# DONNÉES JOUEUR
# =========================
def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "bet": 100,
            "loss_streak": 0,
            "games": 0,
            "wins": 0,
            "blocked_until": 0,
            "history": []
        }
    return users[user_id]

# =========================
# CRASH
# =========================
def generate_crash():
    return round(random.uniform(1.2, 7.0), 2)

# =========================
# MENU
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    keyboard = [
        [InlineKeyboardButton("🚀 LANCER", callback_data="play")],
        [InlineKeyboardButton("💰 Mise", callback_data="bet")],
        [InlineKeyboardButton("📊 Graphique", callback_data="graph")]
    ]

    await update.message.reply_text(
        f"💎 LUCKY JET PRO\n\n"
        f"Solde: {user['balance']} FCFA\n\n"
        f"🎨 Mode Violet Néon activé",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# SIGNAL AUTO
# =========================
async def auto_signal(context: ContextTypes.DEFAULT_TYPE):
    crash = generate_crash()
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f"📡 SIGNAL AUTO\nProchain crash estimé > {crash}x"
    )

# =========================
# BOUTONS
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    if query.data == "play":

        if time.time() < user["blocked_until"]:
            await query.edit_message_text("🛑 Pause active 60s")
            return

        if user["balance"] < user["bet"]:
            await query.edit_message_text("❌ Solde insuffisant")
            return

        crash_point = generate_crash()
        multiplier = 1.0
        start_time = time.time()

        user["balance"] -= user["bet"]
        user["games"] += 1

        keyboard = [
            [InlineKeyboardButton("⏹ CASHOUT", callback_data="cashout")]
        ]

        msg = await query.edit_message_text(
            f"🚀 {multiplier}x\n⏱️ 0.0s",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        active_games[query.from_user.id] = {
            "crash": crash_point,
            "multiplier": multiplier,
            "message": msg,
            "running": True
        }

        while multiplier < crash_point and active_games[query.from_user.id]["running"]:
            await asyncio.sleep(0.5)
            multiplier += 0.2
            elapsed = round(time.time() - start_time, 1)

            active_games[query.from_user.id]["multiplier"] = multiplier

            await msg.edit_text(
                f"🚀 {round(multiplier,2)}x\n⏱️ {elapsed}s",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        if active_games[query.from_user.id]["running"]:
            await msg.edit_text(f"💥 CRASH à {crash_point}x")
            user["loss_streak"] += 1
            if user["loss_streak"] >= 3:
                user["blocked_until"] = time.time() + 60
                user["loss_streak"] = 0

        del active_games[query.from_user.id]

    elif query.data == "cashout":
        if query.from_user.id in active_games:
            game = active_games[query.from_user.id]
            game["running"] = False
            multiplier = game["multiplier"]

            gain = round(user["bet"] * multiplier)
            user["balance"] += gain
            user["wins"] += 1
            user["loss_streak"] = 0
            user["history"].append(user["balance"])

            await game["message"].edit_text(
                f"💰 CASHOUT à {round(multiplier,2)}x\nGain: {gain}\nSolde: {user['balance']}"
            )

    elif query.data == "bet":
        await query.edit_message_text("💰 Envoie le montant de la mise")

    elif query.data == "graph":
        if not user["history"]:
            await query.edit_message_text("📊 Pas encore de données")
            return

        plt.figure()
        plt.plot(user["history"])
        plt.title("Performance")
        plt.xlabel("Parties")
        plt.ylabel("Balance")

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        plt.close()

        await query.message.reply_photo(photo=buffer)

# =========================
# MISE
# =========================
async def set_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user.id)
    try:
        amount = int(update.message.text)
        if amount <= 0:
            raise ValueError
        user["bet"] = amount
        await update.message.reply_text(f"✅ Mise définie à {amount}")
    except:
        await update.message.reply_text("❌ Montant invalide")

# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_bet))

    # Signal automatique toutes les 3 minutes
    app.job_queue.run_repeating(
        auto_signal,
        interval=180,
        first=10,
        chat_id=None
    )

    print("Lucky Jet PRO lancé")
    app.run_polling()

if __name__ == "__main__":
    main()