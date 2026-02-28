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
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("solde", solde))
app.add_handler(CommandHandler("stats", stats))

print("🚀 Casino PRO démarré")
app.run_polling()