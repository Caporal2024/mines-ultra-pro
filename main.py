import os
import random
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("TOKEN")

# ==============================
# 📊 STOCKAGE UTILISATEURS
# ==============================

users = {}

START_BALANCE = 10000

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": START_BALANCE,
            "wins": 0,
            "losses": 0,
            "game": None,
            "bet": 0
        }
    return users[user_id]

# ==============================
# 🎨 MENU PRINCIPAL
# ==============================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("⚽ Penalty", callback_data="penalty")],
        [InlineKeyboardButton("💰 Solde", callback_data="balance")],
        [InlineKeyboardButton("📊 Statistiques", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==============================
# 🚀 START
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    text = f"""
💎 *MINES 5x5 PRO MAX*

💰 Solde: {user['balance']} FCFA

Choisis un jeu 👇
"""
    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ==============================
# 💰 SOLDE
# ==============================

async def show_balance(query):
    user = get_user(query.from_user.id)

    text = f"""
💰 *TON SOLDE*

Solde actuel : {user['balance']} FCFA
"""
    await query.edit_message_text(
        text,
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ==============================
# 📊 STATISTIQUES
# ==============================

async def show_stats(query):
    user = get_user(query.from_user.id)
    total = user["wins"] + user["losses"]
    winrate = (user["wins"] / total * 100) if total > 0 else 0

    text = f"""
📊 *STATISTIQUES*

Victoires : {user['wins']}
Défaites : {user['losses']}
Parties : {total}
Winrate : {round(winrate,2)}%

💰 Solde : {user['balance']} FCFA
"""
    await query.edit_message_text(
        text,
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ==============================
# 🎮 NAVIGATION
# ==============================

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "balance":
        await show_balance(query)

    elif data == "stats":
        await show_stats(query)

    elif data == "mines":
        await query.edit_message_text(
            "🎮 Mines 5x5 arrive dans la Partie 2...",
            reply_markup=main_menu()
        )

    elif data == "lucky":
        await query.edit_message_text(
            "🚀 Lucky Jet arrive dans la Partie 2...",
            reply_markup=main_menu()
        )

    elif data == "penalty":
        await query.edit_message_text(
            "⚽ Penalty arrive dans la Partie 2...",
            reply_markup=main_menu()
        )

# ==============================
# 🚀 LANCEMENT BOT
# ==============================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()