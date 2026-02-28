import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ⚠️ TOKEN récupéré automatiquement depuis Railway
TOKEN = os.environ.get("BOT_TOKEN")

# ==============================
# BASE UTILISATEURS
# ==============================
users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "wins": 0,
            "losses": 0,
            "profit": 0,
            "loss_limit": -3000,
            "profit_target": 4000,
            "auto_stop": False,
            "consecutive_losses": 0
        }
    return users[user_id]

# ==============================
# MENU PRINCIPAL
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💣 Mine 5x5", callback_data="mine")],
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="jet")],
        [InlineKeyboardButton("🥅 Gardien", callback_data="penalty")],
        [InlineKeyboardButton("📊 Statistiques", callback_data="stats")]
    ]

    await update.message.reply_text(
        "🎰 CASINO PRO MAX\n\n💎 Interface Premium Active",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# SYSTEME AUTO STOP
# ==============================
def check_auto_stop(user):
    if user["profit"] <= user["loss_limit"]:
        user["auto_stop"] = True
    if user["profit"] >= user["profit_target"]:
        user["auto_stop"] = True
    if user["consecutive_losses"] >= 3:
        user["auto_stop"] = True

# ==============================
# MINE
# ==============================
async def mine_game(query, user):
    if user["auto_stop"]:
        await query.edit_message_text("🛑 Mode Stop actif.")
        return

    result = random.choice(["win", "lose"])

    if result == "win":
        gain = 1000
        user["balance"] += gain
        user["wins"] += 1
        user["profit"] += gain
        user["consecutive_losses"] = 0
        text = f"💎 Case sûre trouvée ! +{gain} FCFA"
    else:
        loss = 1000
        user["balance"] -= loss
        user["losses"] += 1
        user["profit"] -= loss
        user["consecutive_losses"] += 1
        text = f"💣 Bombe ! -{loss} FCFA"

    check_auto_stop(user)

    await query.edit_message_text(
        f"{text}\n\n💰 Balance: {user['balance']} FCFA"
    )

# ==============================
# LUCKY JET
# ==============================
async def jet_game(query, user):
    if user["auto_stop"]:
        await query.edit_message_text("🛑 Mode Stop actif.")
        return

    multiplier = round(random.uniform(1.1, 5.0), 2)
    bet = 1000

    if multiplier > 2:
        gain = int(bet * multiplier)
        user["balance"] += gain
        user["wins"] += 1
        user["profit"] += gain
        user["consecutive_losses"] = 0
        text = f"🚀 Crash à x{multiplier}\n💎 Gain: {gain}"
    else:
        user["balance"] -= bet
        user["losses"] += 1
        user["profit"] -= bet
        user["consecutive_losses"] += 1
        text = f"💥 Crash à x{multiplier}\n❌ Perdu: {bet}"

    check_auto_stop(user)

    await query.edit_message_text(
        f"{text}\n\n💰 Balance: {user['balance']} FCFA"
    )

# ==============================
# GARDIEN
# ==============================
async def penalty_game(query, user):
    if user["auto_stop"]:
        await query.edit_message_text("🛑 Mode Stop actif.")
        return

    directions = ["gauche", "centre", "droite"]
    player = random.choice(directions)
    keeper = random.choice(directions)

    bet = 1000

    if player != keeper:
        gain = 1500
        user["balance"] += gain
        user["wins"] += 1
        user["profit"] += gain
        user["consecutive_losses"] = 0
        text = f"🥅 Gardien plonge {keeper}\n⚽ But ! +{gain}"
    else:
        user["balance"] -= bet
        user["losses"] += 1
        user["profit"] -= bet
        user["consecutive_losses"] += 1
        text = f"🧤 Gardien plonge {keeper}\n❌ Arrêt ! -{bet}"

    check_auto_stop(user)

    await query.edit_message_text(
        f"{text}\n\n💰 Balance: {user['balance']} FCFA"
    )

# ==============================
# STATISTIQUES
# ==============================
async def show_stats(query, user):
    await query.edit_message_text(
        f"📊 STATISTIQUES\n\n"
        f"💰 Balance: {user['balance']} FCFA\n"
        f"🏆 Victoires: {user['wins']}\n"
        f"❌ Défaites: {user['losses']}\n"
        f"📈 Profit: {user['profit']} FCFA\n"
        f"🛑 Loss Limit: {user['loss_limit']} FCFA\n"
        f"🎯 Profit Target: {user['profit_target']} FCFA"
    )

# ==============================
# HANDLER BOUTONS
# ==============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)

    if query.data == "mine":
        await mine_game(query, user)
    elif query.data == "jet":
        await jet_game(query, user)
    elif query.data == "penalty":
        await penalty_game(query, user)
    elif query.data == "stats":
        await show_stats(query, user)

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("CASINO PRO MAX ACTIF 🚀")
    app.run_polling()