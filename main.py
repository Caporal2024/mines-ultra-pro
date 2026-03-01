import telebot
from telebot import types
import sqlite3
import random
from datetime import datetime, timedelta

# ======================
# CONFIG
# ======================
TOKEN = "PASTE_YOUR_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN)

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
    total_wins INTEGER,
    total_losses INTEGER,
    stop_loss INTEGER,
    profit_target INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jackpot (
    id INTEGER PRIMARY KEY,
    amount INTEGER,
    last_win_date TEXT
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

def today():
    return datetime.now().strftime("%Y-%m-%d")

def time_until_midnight():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
    remaining = midnight - now
    return str(remaining).split('.')[0]

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (user_id, 10000, 3, 0, 0, -3000, 4000))
        conn.commit()
        return (user_id, 10000, 3, 0, 0, -3000, 4000)
    return user

def update_stats(user_id, win):
    if win:
        cursor.execute("UPDATE users SET total_wins=total_wins+1 WHERE user_id=?", (user_id,))
    else:
        cursor.execute("UPDATE users SET total_losses=total_losses+1 WHERE user_id=?", (user_id,))
    conn.commit()

# ======================
# MENU
# ======================

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💣 Mines", callback_data="mines"),
        types.InlineKeyboardButton("❤️ Mines Life", callback_data="mineslife"),
        types.InlineKeyboardButton("🚀 Crash", callback_data="crash"),
        types.InlineKeyboardButton("✈️ Lucky Jet", callback_data="lucky")
    )
    return markup

# ======================
# START
# ======================

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)

    cursor.execute("SELECT amount FROM jackpot WHERE id=1")
    jackpot = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"""
🟣 CASINO ULTRA PRO MAX 🟣

👤 ID: {message.from_user.id}
💰 Solde: {user[1]} FCFA
❤️ Vies: {user[2]}

📊 Wins: {user[3]} | Losses: {user[4]}

🎁 Jackpot: {jackpot} FCFA
⏳ Reset: {time_until_midnight()}

🎛️ Choisis un jeu :
""",
        reply_markup=main_menu()
    )

# ======================
# GAME LOGIC
# ======================

@bot.callback_query_handler(func=lambda call: True)
def game_handler(call):
    user = get_user(call.from_user.id)
    bet = 1000

    if user[1] < bet:
        bot.answer_callback_query(call.id, "❌ Solde insuffisant")
        return

    multiplier = round(random.uniform(1.0, 5.0), 2)

    win = multiplier > 2.0

    if call.data == "mineslife":
        if user[2] <= 0:
            bot.answer_callback_query(call.id, "💀 Plus de vies")
            return
        if not win:
            cursor.execute("UPDATE users SET life=life-1 WHERE user_id=?", (user[0],))
        else:
            cursor.execute("UPDATE users SET balance=balance+500 WHERE user_id=?", (user[0],))

    else:
        if win:
            gain = int(bet * multiplier)
            cursor.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (gain, user[0]))
            cursor.execute("UPDATE jackpot SET amount=amount+100 WHERE id=1")
        else:
            cursor.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (bet, user[0]))
            cursor.execute("UPDATE jackpot SET amount=amount+200 WHERE id=1")

    update_stats(user[0], win)
    conn.commit()

    result_text = f"🎰 x{multiplier}\n"
    result_text += "💎 GAGNÉ !" if win else "💥 PERDU !"

    bot.edit_message_text(
        result_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=main_menu()
    )

# ======================
# RUN
# ======================
bot.polling()