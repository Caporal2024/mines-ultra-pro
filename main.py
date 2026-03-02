import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ==============================
# 🔐 COLLE TON TOKEN ICI
# ==============================
TOKEN = "COLLE_TON_TOKEN_ICI"

# ==============================
# 💰 CONFIG BANKROLL
# ==============================
LOSS_LIMIT = -3000
PROFIT_TARGET = 4000

# ==============================
# 🤖 MODE IA
# ==============================
BASE_BET = 500
IA_MODE = True

# ==============================
# 📦 STOCKAGE SESSION
# ==============================
user_sessions = {}


# ==============================
# 🔄 INITIALISATION JOUEUR
# ==============================
def init_user(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "balance": 10000,
            "cycle_profit": 0,
            "wins": 0,
            "losses": 0,
            "history": [],
            "current_bet": BASE_BET
        }


# ==============================
# 🔄 RESET CYCLE
# ==============================
def reset_cycle(user_id):
    user_sessions[user_id]["cycle_profit"] = 0
    user_sessions[user_id]["wins"] = 0
    user_sessions[user_id]["losses"] = 0


# ==============================
# 🔎 CHECK AUTO-CYCLE
# ==============================
async def check_cycle(update: Update, user_id):
    session = user_sessions[user_id]

    if session["cycle_profit"] <= LOSS_LIMIT:
        await update.effective_message.reply_text(
            f"🛑 Cycle terminé !\n\n"
            f"📉 Perte: {session['cycle_profit']} FCFA\n"
            f"✅ Wins: {session['wins']}\n"
            f"❌ Losses: {session['losses']}\n\n"
            "🔄 Nouveau cycle démarré 🚀"
        )
        reset_cycle(user_id)

    elif session["cycle_profit"] >= PROFIT_TARGET:
        await update.effective_message.reply_text(
            f"🎯 Objectif atteint !\n\n"
            f"📈 Profit: +{session['cycle_profit']} FCFA\n"
            f"✅ Wins: {session['wins']}\n"
            f"❌ Losses: {session['losses']}\n\n"
            "🔄 Nouveau cycle démarré 🚀"
        )
        reset_cycle(user_id)


# ==============================
# 🎮 MENU PRINCIPAL
# ==============================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Jouer", callback_data="play")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("📜 Historique", callback_data="history")]
    ]

    await update.message.reply_text(
        "💎 MINES 5x5 PRO MAX\n\n"
        "🎰 Mode IA Activé\n"
        "Choisis une action 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==============================
# 🎛 GESTION BOUTONS
# ==============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    init_user(user_id)
    session = user_sessions[user_id]

    # =========================
    # 🎮 JOUER
    # =========================
    if query.data == "play":

        if IA_MODE:
            bet = session["current_bet"]
        else:
            bet = BASE_BET

        if bet > session["balance"]:
            await query.edit_message_text("❌ Solde insuffisant.")
            return

        multiplier = round(random.uniform(1.0, 7.0), 2)

        # 🎬 Animation Live
        live = 1.00
        message = await query.edit_message_text("🚀 1.00x")

        while live < multiplier:
            await asyncio_sleep(0.3)
            live += 0.25
            await message.edit_text(f"🚀 {round(live,2)}x")

        await message.edit_text(f"💥 CRASH à {multiplier}x")

        # 🎯 Résultat
        if multiplier >= 2:
            gain = bet
            session["balance"] += gain
            session["cycle_profit"] += gain
            session["wins"] += 1
            result = f"🚀 CASHOUT\n💰 Gain: {gain} FCFA"
        else:
            session["balance"] -= bet
            session["cycle_profit"] -= bet
            session["losses"] += 1
            result = f"💥 Perte: {bet} FCFA"

        session["history"].insert(0, f"{multiplier}x")

        # 🤖 IA LOGIC
        if IA_MODE:
            if multiplier >= 2:
                session["current_bet"] = BASE_BET
            else:
                session["current_bet"] = int(session["current_bet"] * 1.4)

                if session["current_bet"] > session["balance"] * 0.3:
                    session["current_bet"] = BASE_BET

        await message.edit_text(
            f"{result}\n\n"
            f"💰 Solde: {session['balance']} FCFA\n"
            f"🤖 Prochaine mise IA: {session['current_bet']} FCFA"
        )

        await check_cycle(update, user_id)

    # =========================
    # 📊 STATS
    # =========================
    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 STATISTIQUES\n\n"
            f"💰 Solde: {session['balance']} FCFA\n"
            f"📈 Cycle: {session['cycle_profit']} FCFA\n"
            f"✅ Wins: {session['wins']}\n"
            f"❌ Losses: {session['losses']}"
        )

    # =========================
    # 📜 HISTORIQUE
    # =========================
    elif query.data == "history":
        hist = " | ".join(session["history"][:5])
        await query.edit_message_text(
            f"📜 Historique:\n\n{hist if hist else 'Aucun historique.'}"
        )


# ==============================
# ⏳ ASYNC SLEEP
# ==============================
import asyncio
asyncio_sleep = asyncio.sleep


# ==============================
# 🚀 LANCEMENT BOT
# ==============================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot lancé 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()