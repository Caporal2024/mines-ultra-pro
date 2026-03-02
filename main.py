import logging
import random
import asyncio
import os
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

# 🔐 TOKEN récupéré depuis Railway
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN manquant. Ajoute la variable TOKEN dans Railway.")

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
            "blocked": False
        }
    return users[user_id]

# =========================
# GÉNÉRATION CRASH
# =========================
def generate_crash():
    return round(random.uniform(1.2, 6.0), 2)

# =========================
# MENU
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    keyboard = [
        [InlineKeyboardButton("🚀 LANCER", callback_data="play")],
        [InlineKeyboardButton("💰 Mise", callback_data="bet")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ]

    await update.message.reply_text(
        f"🎮 LUCKY JET SIMULATOR\nSolde: {user['balance']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# BOUTONS
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    if query.data == "play":

        if user["blocked"]:
            await query.edit_message_text("🛑 Trop de pertes. Pause activée.")
            return

        if user["balance"] < user["bet"]:
            await query.edit_message_text("❌ Solde insuffisant")
            return

        crash_point = generate_crash()
        multiplier = 1.0

        user["balance"] -= user["bet"]
        user["games"] += 1

        keyboard = [
            [InlineKeyboardButton("⏹ CASHOUT", callback_data="cashout")]
        ]

        msg = await query.edit_message_text(
            f"🚀 {multiplier}x",
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
            multiplier += 0.15
            active_games[query.from_user.id]["multiplier"] = multiplier

            await msg.edit_text(
                f"🚀 {round(multiplier,2)}x",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        if active_games[query.from_user.id]["running"]:
            await msg.edit_text(f"💥 CRASH à {crash_point}x")
            user["loss_streak"] += 1
            if user["loss_streak"] >= 3:
                user["blocked"] = True

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

            await game["message"].edit_text(
                f"💰 CASHOUT à {round(multiplier,2)}x\nGain: {gain}"
            )

    elif query.data == "bet":
        await query.edit_message_text("💰 Envoie le montant de la mise")

    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 STATS\n"
            f"Solde: {user['balance']}\n"
            f"Parties: {user['games']}\n"
            f"Victoires: {user['wins']}\n"
            f"Série pertes: {user['loss_streak']}"
        )

# =========================
# MISE PERSONNALISÉE
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

    print("Bot lancé...")
    app.run_polling()

if __name__ == "__main__":
    main()