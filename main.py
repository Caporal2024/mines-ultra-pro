import os
import telebot
from telebot import types
from flask import Flask
import threading
import random
import sqlite3

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise Exception("TOKEN manquant")

bot = telebot.TeleBot(TOKEN)

# ================= DATABASE =================
conn = sqlite3.connect("game.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 1000
)
""")
conn.commit()

games = {}
ADMIN_ID = 123456789  # ← Mets ton ID Telegram ici

# ================= UTIL =================
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return get_user(user_id)

    return user

def update_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (amount, user_id))
    conn.commit()

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎮 MINES 5x5")
    markup.add("💰 BALANCE")

    if message.from_user.id == ADMIN_ID:
        markup.add("🛡 QG")

    bot.send_message(
        message.chat.id,
        f"🎰 MINES 5x5 PRO MAX 💎\n\n💰 Solde: {user[1]} pts",
        reply_markup=markup
    )

# ================= BALANCE =================
@bot.message_handler(func=lambda m: m.text == "💰 BALANCE")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 Solde: {user[1]} pts")

# ================= START GAME =================
@bot.message_handler(func=lambda m: m.text == "🎮 MINES 5x5")
def start_game(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user[1] < 100:
        bot.send_message(message.chat.id, "❌ Minimum 100 pts pour jouer.")
        return

    mines = random.sample(range(25), 5)

    games[user_id] = {
        "mines": mines,
        "revealed": [],
        "bet": 100,
        "multiplier": 1.0
    }

    update_balance(user_id, user[1] - 100)

    send_grid(message.chat.id, user_id)

# ================= GRID =================
def send_grid(chat_id, user_id):
    game = games[user_id]

    markup = types.InlineKeyboardMarkup(row_width=5)

    buttons = []
    for i in range(25):
        if i in game["revealed"]:
            buttons.append(types.InlineKeyboardButton("💎", callback_data="x"))
        else:
            buttons.append(types.InlineKeyboardButton("⬛", callback_data=f"cell_{i}"))

    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("💸 CASHOUT", callback_data="cashout"))

    bot.send_message(chat_id, "🎮 Choisis une case :", reply_markup=markup)

# ================= CLICK =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cell_"))
def click_cell(call):
    user_id = call.from_user.id
    index = int(call.data.split("_")[1])

    if user_id not in games:
        return

    game = games[user_id]

    if index in game["mines"]:
        bot.edit_message_text(
            "💣 BOOM ! Tu as perdu.",
            call.message.chat.id,
            call.message.message_id
        )
        games.pop(user_id)
        return

    game["revealed"].append(index)
    game["multiplier"] += 0.5

    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []

    for i in range(25):
        if i in game["revealed"]:
            buttons.append(types.InlineKeyboardButton("💎", callback_data="x"))
        else:
            buttons.append(types.InlineKeyboardButton("⬛", callback_data=f"cell_{i}"))

    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton(
        f"💸 CASHOUT x{game['multiplier']}",
        callback_data="cashout"
    ))

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# ================= CASHOUT =================
@bot.callback_query_handler(func=lambda call: call.data == "cashout")
def cashout(call):
    user_id = call.from_user.id

    if user_id not in games:
        return

    game = games[user_id]
    user = get_user(user_id)

    gain = int(game["bet"] * game["multiplier"])
    update_balance(user_id, user[1] + gain)

    bot.edit_message_text(
        f"💸 CASHOUT réussi !\n\nGain: {gain} pts",
        call.message.chat.id,
        call.message.message_id
    )

    games.pop(user_id)

# ================= ADMIN QG =================
@bot.message_handler(func=lambda m: m.text == "🛡 QG")
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"🛡 QG ADMIN\n\n👥 Utilisateurs: {total_users}"
    )

# ================= RUN =================
def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

app = Flask(__name__)

@app.route("/")
def home():
    return "MINES 5x5 PRO MAX Running"

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)