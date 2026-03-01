import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== CONFIG =====

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8094967191  # TON ID TELEGRAM

logging.basicConfig(level=logging.INFO)

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "bankroll": 10000,
            "profit": 0,
            "games": 0
        }
    return users[user_id]

# ===== MENUS =====

def main_menu():
    keyboard = [
        [InlineKeyboardButton("💣 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("🚀 Signal Live", callback_data="signal")],
        [InlineKeyboardButton("📊 Statistiques", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu")]])

# ===== START =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    text = f"""
💎 <b>PRO MAX V4</b>
━━━━━━━━━━━━━━━━━━
💰 Bankroll : <b>{user['bankroll']} FCFA</b>
━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())

# ===== SIGNAL SIMULÉ (propre) =====

def generate_signal():
    entry = round(random.uniform(1.20, 1.60), 2)
    confidence = random.randint(60, 85)
    risk = random.choice(["Faible", "Moyen"])
    return entry, confidence, risk

# ===== HANDLER =====

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    if query.data == "menu":
        await query.edit_message_text(
            "💎 MENU PRINCIPAL",
            reply_markup=main_menu()
        )

    # ===== MINES SIMPLE =====
    elif query.data == "mines":
        result = random.choice(["safe", "bomb"])

        if result == "safe":
            gain = random.randint(500, 1500)
            user["bankroll"] += gain
            user["profit"] += gain
            text = f"""
✅ <b>SAFE</b>
💰 Gain : +{gain} FCFA
🏦 Bankroll : {user['bankroll']}
"""
        else:
            loss = random.randint(500, 1500)
            user["bankroll"] -= loss
            user["profit"] -= loss
            text = f"""
💣 <b>BOOM</b>
💸 Perte : -{loss} FCFA
🏦 Bankroll : {user['bankroll']}
"""

        await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_menu())

    # ===== SIGNAL LIVE INTERNE =====
    elif query.data == "signal":
        entry, confidence, risk = generate_signal()

        text = f"""
🚀 <b>SIGNAL LIVE</b>
━━━━━━━━━━━━━━━━━━
🎯 Entrée conseillée : <b>x{entry}</b>
📊 Confiance : <b>{confidence}%</b>
⚠️ Risque : <b>{risk}</b>
━━━━━━━━━━━━━━━━━━
⚡ Analyse basée sur algorithme interne
"""

        await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_menu())

    # ===== STATS =====
    elif query.data == "stats":
        text = f"""
📊 <b>STATISTIQUES</b>
━━━━━━━━━━━━━━━━━━
💰 Bankroll : {user['bankroll']}
📈 Profit : {user['profit']}
━━━━━━━━━━━━━━━━━━
"""
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_menu())

# ===== ADMIN COMMAND =====

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("🔐 Accès Admin confirmé")
    else:
        await update.message.reply_text("⛔ Accès refusé")

# ===== MAIN =====

def main():
    if not TOKEN:
        print("BOT_TOKEN manquant")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("PRO MAX V4 actif")
    app.run_polling()

if __name__ == "__main__":
    main()