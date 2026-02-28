import os
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

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
        "💎 Bienvenue au Casino PRO MAX\n\n"
        "💰 Solde initial: 10 000 FCFA\n\n"
        "Commandes:\n"
        "/solde\n"
        "/stats"
    )

async def solde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 Ton solde: {user[1]} FCFA")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"📊 Statistiques:\n"
        f"💰 Solde: {user[1]} FCFA\n"
        f"🎮 Parties: {user[2]}\n"
        f"🏆 Gains: {user[3]} FCFA\n"
        f"📉 Pertes: {user[4]} FCFA"
    )

# =====================
# Lancement
# =====================
import random

async def lucky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if len(context.args) == 0:
        await update.message.reply_text("Utilisation: /lucky 1000")
        return

    try:
        bet = int(context.args[0])
    except:
        await update.message.reply_text("Mise invalide.")
        return

    if bet <= 0:
        await update.message.reply_text("Mise invalide.")
        return

    balance = user[1]

    if bet > balance:
        await update.message.reply_text("❌ Solde insuffisant.")
        return

    crash_point = round(random.uniform(1.1, 5.0), 2)
    player_multiplier = round(random.uniform(1.1, 5.0), 2)

    cursor.execute("UPDATE users SET games_played = games_played + 1 WHERE user_id=?", (user_id,))

    if player_multiplier < crash_point:
        win_amount = int(bet * player_multiplier)
        profit = win_amount - bet

        cursor.execute("""
            UPDATE users
            SET balance = balance + ?,
                total_won = total_won + ?
            WHERE user_id=?
        """, (profit, profit, user_id))

        result = f"🚀 Lucky Jet\n💥 Crash à x{crash_point}\n🛫 Cashout à x{player_multiplier}\n\n✅ Gain: {profit} FCFA"

    else:
        cursor.execute("""
            UPDATE users
            SET balance = balance - ?,
                total_lost = total_lost + ?
            WHERE user_id=?
        """, (bet, bet, user_id))

        result = f"🚀 Lucky Jet\n💥 Crash à x{crash_point}\n❌ Tu as perdu {bet} FCFA"

    conn.commit()
    await update.message.reply_text(result)