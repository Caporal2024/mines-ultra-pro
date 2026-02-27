import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(TOKEN).build()

# Stockage simple en mémoire
users = {}

# ===== MENU PRINCIPAL =====
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("⚽ Penalty", callback_data="penalty")],
        [InlineKeyboardButton("🚀 Jet", callback_data="jet")],
        [InlineKeyboardButton("⚡ Speed Cash", callback_data="speed")],
        [InlineKeyboardButton("🎡 Roue", callback_data="wheel")],
        [InlineKeyboardButton("💰 Mon Solde", callback_data="balance")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "wins": 0,
            "losses": 0
        }

    text = f"""
🎰 ULTRA PRO MAX BOT 🎰

💰 Solde : {users[user_id]['balance']} FCFA
📊 Victoires : {users[user_id]['wins']}
📉 Défaites : {users[user_id]['losses']}

Choisissez un jeu 👇
"""

    await update.message.reply_text(text, reply_markup=main_menu())

# ===== GESTION MENU =====
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Votre solde actuel : {users[user_id]['balance']} FCFA",
            reply_markup=main_menu()
        )

    elif query.data in ["mines", "penalty", "jet", "speed", "wheel"]:
        await query.edit_message_text(
            f"🚧 Jeu en construction...\n\nSolde actuel : {users[user_id]['balance']} FCFA",
            reply_markup=main_menu()
        )

# ===== HANDLERS =====
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(menu_handler))

app.run_polling()