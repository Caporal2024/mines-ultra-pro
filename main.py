import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ==============================
# CONFIGURATION GLOBALE
# ==============================

START_BALANCE = 10000
BET_AMOUNT = 1000
STOP_LOSS = -3000
PROFIT_TARGET = 4000

games = {}
users = {}

# ==============================
# INITIALISATION UTILISATEUR
# ==============================

def init_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": START_BALANCE,
            "profit": 0,
            "played": 0,
            "wins": 0,
            "losses": 0,
            "current_streak": 0,
            "best_streak": 0
        }

# ==============================
# GENERATION MINES
# ==============================

def generate_mines(mines_count):
    return random.sample(range(25), mines_count)

# ==============================
# CREATION GRILLE
# ==============================

def create_grid(reveal=False, mines_positions=None):
    keyboard = []

    for i in range(0, 25, 5):
        row = []
        for j in range(5):
            index = i + j

            if reveal:
                if index in mines_positions:
                    row.append(InlineKeyboardButton("💣", callback_data="locked"))
                else:
                    row.append(InlineKeyboardButton("💎", callback_data="locked"))
            else:
                row.append(InlineKeyboardButton("🟪", callback_data=str(index)))

        keyboard.append(row)

    if reveal:
        keyboard.append([InlineKeyboardButton("🔄 Rejouer", callback_data="restart")])
        keyboard.append([InlineKeyboardButton("📊 Statistiques", callback_data="stats")])

    return InlineKeyboardMarkup(keyboard)

# ==============================
# MENU PRINCIPAL
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    init_user(user_id)
    user = users[user_id]

    keyboard = [
        [InlineKeyboardButton("💣 3 Mines", callback_data="mines_3")],
        [InlineKeyboardButton("💣 5 Mines", callback_data="mines_5")],
        [InlineKeyboardButton("💣 7 Mines", callback_data="mines_7")],
        [InlineKeyboardButton("📊 Mes Statistiques", callback_data="stats")]
    ]

    await update.message.reply_text(
        f"💎 SOLDE : {user['balance']} FCFA\n"
        f"📈 Profit : {user['profit']} FCFA\n\n"
        f"🎮 Choisis ton mode LIVE 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# GESTION DES ACTIONS
# ==============================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    init_user(user_id)
    user = users[user_id]

    # ==========================
    # CHOIX NOMBRE MINES
    # ==========================
    if query.data.startswith("mines_"):

        if user["profit"] <= STOP_LOSS:
            await query.edit_message_text("🛑 STOP LOSS atteint.")
            return

        if user["profit"] >= PROFIT_TARGET:
            await query.edit_message_text("🎉 OBJECTIF PROFIT atteint.")
            return

        mines_count = int(query.data.split("_")[1])
        games[user_id] = generate_mines(mines_count)
        user["played"] += 1

        await query.edit_message_text(
            "⚡ Jeu LIVE lancé ! Clique une case...",
            reply_markup=create_grid(False)
        )

    # ==========================
    # AFFICHAGE STATS
    # ==========================
    elif query.data == "stats":

        await query.edit_message_text(
            f"📊 STATISTIQUES\n\n"
            f"💰 Solde : {user['balance']} FCFA\n"
            f"📈 Profit : {user['profit']} FCFA\n"
            f"🎮 Parties : {user['played']}\n"
            f"🏆 Victoires : {user['wins']}\n"
            f"❌ Défaites : {user['losses']}\n"
            f"🔥 Meilleure série : {user['best_streak']}"
        )

    # ==========================
    # REJOUER
    # ==========================
    elif query.data == "restart":
        await start(update, context)

    # ==========================
    # CLIC SUR CASE
    # ==========================
    elif query.data != "locked":

        mines = games.get(user_id)
        clicked_index = int(query.data)

        await query.edit_message_text("⚡ Révélation LIVE...")
        await asyncio.sleep(0.5)

        if clicked_index in mines:
            user["losses"] += 1
            user["current_streak"] = 0
            user["balance"] -= BET_AMOUNT
            user["profit"] -= BET_AMOUNT
            result_text = "💥 BOOM ! Mine touchée ! -1000 FCFA"
        else:
            user["wins"] += 1
            user["current_streak"] += 1

            if user["current_streak"] > user["best_streak"]:
                user["best_streak"] = user["current_streak"]

            user["balance"] += BET_AMOUNT
            user["profit"] += BET_AMOUNT
            result_text = "🎉 SAFE ! +1000 FCFA"

        await query.edit_message_text(
            result_text,
            reply_markup=create_grid(True, mines)
        )

# ==============================
# LANCEMENT BOT
# ==============================

def main():
    app = ApplicationBuilder().token("MET_TON_TOKEN_ICI").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot Mines 5x5 LIVE démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()