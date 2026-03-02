import random
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# =============================
# 🔐 TOKEN VIA RAILWAY VARIABLE
# =============================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN non défini dans Railway Variables")

# =============================
# ⚙ CONFIG
# =============================
LOSS_LIMIT = -3000
PROFIT_TARGET = 4000
BASE_BET = 500
IA_MODE = True

user_sessions = {}


# =============================
# 🎛 MENU KEYBOARD GLOBAL
# =============================
def get_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Jouer", callback_data="play")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("📜 Historique", callback_data="history")]
    ])


# =============================
# 👤 INIT USER
# =============================
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


def reset_cycle(user_id):
    user_sessions[user_id]["cycle_profit"] = 0
    user_sessions[user_id]["wins"] = 0
    user_sessions[user_id]["losses"] = 0


async def check_cycle(message, user_id):
    session = user_sessions[user_id]

    if session["cycle_profit"] <= LOSS_LIMIT:
        await message.reply_text(
            "🛑 Limite perte atteinte. Nouveau cycle.",
            reply_markup=get_menu_keyboard()
        )
        reset_cycle(user_id)

    elif session["cycle_profit"] >= PROFIT_TARGET:
        await message.reply_text(
            "🎯 Objectif atteint. Nouveau cycle.",
            reply_markup=get_menu_keyboard()
        )
        reset_cycle(user_id)


# =============================
# 🚀 START / MENU
# =============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 MINES ULTRA PRO\n\n🤖 Mode IA Activé",
        reply_markup=get_menu_keyboard()
    )


# =============================
# 🎮 BUTTON HANDLER
# =============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    init_user(user_id)
    session = user_sessions[user_id]

    # ================= PLAY =================
    if query.data == "play":

        bet = session["current_bet"] if IA_MODE else BASE_BET

        if bet > session["balance"]:
            await query.edit_message_text(
                "❌ Solde insuffisant.",
                reply_markup=get_menu_keyboard()
            )
            return

        multiplier = round(random.uniform(1.0, 7.0), 2)

        message = await query.edit_message_text(
            "🚀 1.00x",
            reply_markup=get_menu_keyboard()
        )

        # 🔥 LIVE STABLE LIMITÉ (ANTI-FLOOD)
        live = 1.0
        steps = min(int((multiplier - 1) / 0.5), 6)

        for _ in range(steps):
            await asyncio.sleep(0.5)
            live += 0.5
            try:
                await message.edit_text(
                    f"🚀 {round(live,2)}x",
                    reply_markup=get_menu_keyboard()
                )
            except:
                break

        await asyncio.sleep(0.5)

        # ================= RESULTAT =================
        if multiplier >= 2:
            gain = bet
            session["balance"] += gain
            session["cycle_profit"] += gain
            session["wins"] += 1
            result = f"🚀 Gain: {gain} FCFA"
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
            f"🤖 Prochaine mise: {session['current_bet']} FCFA",
            reply_markup=get_menu_keyboard()
        )

        await check_cycle(message, user_id)

    # ================= STATS =================
    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 STATISTIQUES\n\n"
            f"💰 Solde: {session['balance']} FCFA\n"
            f"📈 Cycle: {session['cycle_profit']} FCFA\n"
            f"✅ Wins: {session['wins']}\n"
            f"❌ Losses: {session['losses']}",
            reply_markup=get_menu_keyboard()
        )

    # ================= HISTORIQUE =================
    elif query.data == "history":
        hist = " | ".join(session["history"][:5])
        await query.edit_message_text(
            f"📜 Historique:\n\n{hist if hist else 'Aucun historique.'}",
            reply_markup=get_menu_keyboard()
        )


# =============================
# 🚀 MAIN
# =============================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot lancé 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()