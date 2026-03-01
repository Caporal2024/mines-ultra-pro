import random
import sqlite3
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ======================
# CONFIG (TOKEN VIDE)
# ======================
TOKEN = ""

# ======================
# DATABASE
# ======================
conn = sqlite3.connect("casino.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER,
    life INTEGER,
    wins INTEGER,
    losses INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jackpot (
    id INTEGER PRIMARY KEY,
    amount INTEGER,
    last_win TEXT
)
""")

conn.commit()

cursor.execute("SELECT * FROM jackpot WHERE id=1")
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO jackpot VALUES (1, 0, '')")
    conn.commit()

# ======================
# UTILS
# ======================

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
            (user_id, 10000, 3, 0, 0),
        )
        conn.commit()
        return (user_id, 10000, 3, 0, 0)
    return user

def time_until_midnight():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
    return str((midnight - now)).split(".")[0]

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("💣 Mines", callback_data="mines"),
            InlineKeyboardButton("❤️ Mines Life", callback_data="mineslife"),
        ],
        [
            InlineKeyboardButton("🚀 Crash", callback_data="crash"),
            InlineKeyboardButton("✈️ Lucky Jet", callback_data="lucky"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

# ======================
# START
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    cursor.execute("SELECT amount FROM jackpot WHERE id=1")
    jackpot = cursor.fetchone()[0]

    text = f"""
🟣 CASINO ULTRA 🟣

👤 ID: {update.effective_user.id}
💰 Solde: {user[1]} FCFA
❤️ Vies: {user[2]}

📊 Wins: {user[3]} | Losses: {user[4]}

🎁 Jackpot: {jackpot} FCFA
⏳ Reset: {time_until_midnight()}

🎛️ Choisis un jeu :
"""

    await update.message.reply_text(text, reply_markup=main_menu())

# ======================
# GAME HANDLER
# ======================

async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)
    bet = 1000

    if user[1] < bet:
        await query.edit_message_text("❌ Solde insuffisant", reply_markup=main_menu())
        return

    multiplier = round(random.uniform(1.0, 5.0), 2)
    win = multiplier > 2

    if query.data == "mineslife":
        if user[2] <= 0:
            await query.edit_message_text("💀 Plus de vies", reply_markup=main_menu())
            return

        if win:
            cursor.execute("UPDATE users SET balance=balance+500, wins=wins+1 WHERE user_id=?", (user[0],))
        else:
            cursor.execute("UPDATE users SET life=life-1, losses=losses+1 WHERE user_id=?", (user[0],))

    else:
        if win:
            gain = int(bet * multiplier)
            cursor.execute("UPDATE users SET balance=balance+?, wins=wins+1 WHERE user_id=?", (gain, user[0]))
            cursor.execute("UPDATE jackpot SET amount=amount+100 WHERE id=1")
        else:
            cursor.execute("UPDATE users SET balance=balance-?, losses=losses+1 WHERE user_id=?", (bet, user[0]))
            cursor.execute("UPDATE jackpot SET amount=amount+200 WHERE id=1")

    conn.commit()

    result = f"🎰 x{multiplier}\n"
    result += "💎 GAGNÉ !" if win else "💥 PERDU !"

    await query.edit_message_text(result, reply_markup=main_menu())

# ======================
# MAIN
# ======================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(game_handler))

    print("BOT LANCÉ ✅")
    app.run_polling()

if __name__ == "__main__":
    main()