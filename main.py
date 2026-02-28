import os
import sqlite3
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN manquant")

# =====================
# Base de données
# =====================
conn = sqlite3.connect("casino.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 10000,
    games_played INTEGER DEFAULT 0,
    total_won INTEGER DEFAULT 0,
    total_lost INTEGER DEFAULT 0
)
""")
conn.commit()

# =====================
# Anti Spam
# =====================
cooldowns = {}

# =====================
# Fonctions utilitaires
# =====================
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return get_user(user_id)
    return user

# =====================
# Commandes
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_user(user_id)
    await update.message.reply_text(
        "💎 BIENVENUE AU CASINO PRO MAX 💎\n\n"
        "💰 Solde initial: 10 000 FCFA\n\n"
        "🎮 Commandes disponibles :\n"
        "/solde\n"
        "/stats\n"
        "/lucky"
    )

async def solde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 Ton solde actuel : {user[1]} FCFA")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"📊 Statistiques\n\n"
        f"💰 Solde : {user[1]} FCFA\n"
        f"🎮 Parties : {user[2]}\n"
        f"🏆 Gains totaux : {user[3]} FCFA\n"
        f"📉 Pertes totales : {user[4]} FCFA"
    )

# =====================
# Lucky Jet - Menu Boutons
# =====================
async def lucky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("500", callback_data="lucky_500"),
            InlineKeyboardButton("1000", callback_data="lucky_1000"),
        ],
        [
            InlineKeyboardButton("2000", callback_data="lucky_2000"),
            InlineKeyboardButton("5000", callback_data="lucky_5000"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 LUCKY JET 🚀\n\n💎 Choisis ta mise :",
        reply_markup=reply_markup
    )

# =====================
# Lucky Jet - Jeu
# =====================
async def lucky_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Anti-spam 3 secondes
    now = datetime.now()
    if user_id in cooldowns:
        if now - cooldowns[user_id] < timedelta(seconds=3):
            await query.edit_message_text("⏳ Attends 3 secondes avant de rejouer.")
            return

    cooldowns[user_id] = now

    bet = int(query.data.split("_")[1])

    user = get_user(user_id)
    balance = user[1]

    if bet > balance:
        await query.edit_message_text("❌ Solde insuffisant.")
        return

    crash_point = round(random.uniform(1.1, 5.0), 2)
    player_multiplier = round(random.uniform(1.1, 5.0), 2)

    cursor.execute(
        "UPDATE users SET games_played = games_played + 1 WHERE user_id=?",
        (user_id,)
    )

    if player_multiplier < crash_point:
        win_amount = int(bet * player_multiplier)
        profit = win_amount - bet

        cursor.execute("""
            UPDATE users
            SET balance = balance + ?,
                total_won = total_won + ?
            WHERE user_id=?
        """, (profit, profit, user_id))

        result = (
            f"🚀 Lucky Jet\n"
            f"💥 Crash à x{crash_point}\n"
            f"🛫 Cashout à x{player_multiplier}\n\n"
            f"✅ Gain : {profit} FCFA"
        )
    else:
        cursor.execute("""
            UPDATE users
            SET balance = balance - ?,
                total_lost = total_lost + ?
            WHERE user_id=?
        """, (bet, bet, user_id))

        result = (
            f"🚀 Lucky Jet\n"
            f"💥 Crash à x{crash_point}\n"
            f"❌ Tu as perdu {bet} FCFA"
        )

    conn.commit()

    await query.edit_message_text(result)

# =====================
# Lancement
# =====================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("solde", solde))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("lucky", lucky))
app.add_handler(CallbackQueryHandler(lucky_callback, pattern="^lucky_"))

print("🚀 Casino PRO MAX démarré")
app.run_polling()