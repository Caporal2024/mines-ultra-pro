import os
import telebot
from telebot import types
from flask import Flask
import threading
import random
import time
import sqlite3
from datetime import datetime, timedelta

# ================= TOKEN =================
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise Exception("TOKEN manquant dans Railway")

bot = telebot.TeleBot(TOKEN)

# ================= DATABASE =================
conn = sqlite3.connect("game.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 1000,
    games INTEGER DEFAULT 0,
    total_won INTEGER DEFAULT 0,
    last_bonus TEXT
)
""")
conn.commit()

active_rounds = {}

# ================= LIVE SYSTEM =================
live_history = []
current_round = {"active": False, "multiplier": 1.0, "crash": 0}

def live_loop():
    global current_round

    while True:
        time.sleep(5)

        crash = round(random.uniform(1.5, 6.0), 2)
        current_round = {"active": True, "multiplier": 1.0, "crash": crash}

        while current_round["multiplier"] < crash:
            time.sleep(1)
            current_round["multiplier"] += round(random.uniform(0.1, 0.4), 2)

        current_round["active"] = False

        live_history.insert(0, crash)
        if len(live_history) > 10:
            live_history.pop()

threading.Thread(target=live_loop, daemon=True).start()

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

def update_stats(user_id, gain):
    cursor.execute("""
    UPDATE users
    SET games = games + 1,
        total_won = total_won + ?
    WHERE user_id=?
    """, (gain, user_id))
    conn.commit()

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 PLAY")
    markup.add("💰 BALANCE", "📊 STATS")
    markup.add("🏆 LEADERBOARD", "🎁 BONUS")
    markup.add("📡 LIVE")

    bot.send_message(
        message.chat.id,
        f"🎮 MINES 5x5 PRO MAX 💎\n\n💎 Points: {user[1]}",
        reply_markup=markup
    )

# ================= BONUS =================
@bot.message_handler(func=lambda m: m.text == "🎁 BONUS")
def bonus(message):
    user = get_user(message.from_user.id)
    last_bonus = user[4]
    now = datetime.now()

    if last_bonus:
        last_time = datetime.fromisoformat(last_bonus)
        if now - last_time < timedelta(hours=24):
            bot.send_message(message.chat.id, "⏳ Bonus déjà pris aujourd'hui.")
            return

    bonus_amount = 500
    new_balance = user[1] + bonus_amount

    cursor.execute("""
    UPDATE users SET balance=?, last_bonus=?
    WHERE user_id=?
    """, (new_balance, now.isoformat(), message.from_user.id))
    conn.commit()

    bot.send_message(message.chat.id, f"🎁 +{bonus_amount} pts ajoutés !")

# ================= BALANCE =================
@bot.message_handler(func=lambda m: m.text == "💰 BALANCE")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 Solde: {user[1]} pts")

# ================= STATS =================
@bot.message_handler(func=lambda m: m.text == "📊 STATS")
def stats(message):
    user = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"📊 Stats\n\n🎮 Parties: {user[2]}\n💰 Total gagné: {user[3]} pts"
    )

# ================= LEADERBOARD =================
@bot.message_handler(func=lambda m: m.text == "🏆 LEADERBOARD")
def leaderboard(message):
    cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 5")
    top = cursor.fetchall()

    text = "🏆 TOP 5\n\n"
    for i, user in enumerate(top):
        text += f"{i+1}. ID {user[0]} — {user[1]} pts\n"

    bot.send_message(message.chat.id, text)

# ================= LIVE =================
@bot.message_handler(func=lambda m: m.text == "📡 LIVE")
def live(message):
    text = "📡 LIVE MODE\n\n"

    if current_round["active"]:
        text += f"🚀 En cours : {current_round['multiplier']:.2f}x\n\n"

    text += "🔥 Historique :\n"
    for x in live_history:
        text += f"💥 {x}x\n"

    bot.send_message(message.chat.id, text)

# ================= PLAY =================
@bot.message_handler(func=lambda m: m.text == "🚀 PLAY")
def play(message):
    user_id = message.from_user.id

    if user_id in active_rounds:
        bot.send_message(message.chat.id, "⚠️ Partie déjà en cours.")
        return

    bot.send_message(message.chat.id, "💎 Entre ta mise :")
    bot.register_next_step_handler(message, process_bet)

def process_bet(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if not message.text.isdigit():
        bot.send_message(message.chat.id, "💎 Entre un nombre valide.")
        bot.register_next_step_handler(message, process_bet)
        return

    bet = int(message.text)

    if bet <= 0 or bet > user[1]:
        bot.send_message(message.chat.id, "❌ Mise invalide.")
        return

    crash = round(random.uniform(1.5, 6.0), 2)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💸 CASHOUT", callback_data="cashout"))

    msg = bot.send_message(message.chat.id, "🚀 1.00x", reply_markup=markup)

    active_rounds[user_id] = {
        "bet": bet,
        "crash": crash,
        "multiplier": 1.0,
        "message_id": msg.message_id,
        "chat_id": message.chat.id,
        "active": True
    }

    threading.Thread(target=run_game, args=(user_id,), daemon=True).start()

def run_game(user_id):
    round_data = active_rounds[user_id]

    while round_data["multiplier"] < round_data["crash"]:
        if not round_data["active"]:
            return

        time.sleep(0.8)
        round_data["multiplier"] += round(random.uniform(0.1, 0.4), 2)

        bot.edit_message_text(
            f"🚀 {round_data['multiplier']:.2f}x",
            round_data["chat_id"],
            round_data["message_id"],
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("💸 CASHOUT", callback_data="cashout")
            )
        )

    round_data["active"] = False

    user = get_user(user_id)
    new_balance = user[1] - round_data["bet"]
    update_balance(user_id, new_balance)
    update_stats(user_id, 0)

    bot.edit_message_text(
        f"💥 Crash à {round_data['crash']}x\n\n❌ -{round_data['bet']} pts\n\n💰 {new_balance} pts",
        round_data["chat_id"],
        round_data["message_id"]
    )

    del active_rounds[user_id]

# ================= CASHOUT =================
@bot.callback_query_handler(func=lambda call: call.data == "cashout")
def cashout(call):
    user_id = call.from_user.id

    if user_id not in active_rounds:
        return

    round_data = active_rounds[user_id]
    if not round_data["active"]:
        return

    round_data["active"] = False

    gain = int(round_data["bet"] * round_data["multiplier"])
    user = get_user(user_id)
    new_balance = user[1] + gain

    update_balance(user_id, new_balance)
    update_stats(user_id, gain)

    bot.edit_message_text(
        f"💸 CASHOUT à {round_data['multiplier']:.2f}x\n\n✅ +{gain} pts\n\n💰 {new_balance} pts",
        round_data["chat_id"],
        round_data["message_id"]
    )

    del active_rounds[user_id]

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