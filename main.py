import os
import telebot
from telebot import types
from flask import Flask
import threading
import random
import sqlite3
import time

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
crash_games = {}

ADMIN_ID = 123456789  # Mets ton ID ici

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

# ================= MENU =================
def main_menu(user_id):
    user = get_user(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎮 MINES 5x5")
    markup.add("✈️ JET CRASH", "🚀 ROCKET RISE")
    markup.add("💰 BALANCE")

    if user_id == ADMIN_ID:
        markup.add("🛡 QG")

    return markup

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"🎰 CASINO PRO MAX 💎\n\n💰 Solde: {user[1]} pts",
        reply_markup=main_menu(message.from_user.id)
    )

# ================= BALANCE =================
@bot.message_handler(func=lambda m: m.text == "💰 BALANCE")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 Solde: {user[1]} pts")

# ================= JET CRASH LIVE =================
@bot.message_handler(func=lambda m: m.text == "✈️ JET CRASH")
def jet_crash(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    bet = 100

    if user[1] < bet:
        bot.send_message(message.chat.id, "❌ Minimum 100 pts.")
        return

    update_balance(user_id, user[1] - bet)

    crash_point = round(random.uniform(1.5, 6.0), 2)

    crash_games[user_id] = {
        "bet": bet,
        "multiplier": 1.00,
        "crash_point": crash_point,
        "active": True
    }

    msg = bot.send_message(message.chat.id, "✈️ Décollage...\n\nx1.00")

    threading.Thread(
        target=run_crash,
        args=(message.chat.id, msg.message_id, user_id),
        daemon=True
    ).start()

def run_crash(chat_id, message_id, user_id):
    while user_id in crash_games and crash_games[user_id]["active"]:
        game = crash_games[user_id]

        game["multiplier"] += round(random.uniform(0.05, 0.25), 2)

        if game["multiplier"] >= game["crash_point"]:
            bot.edit_message_text(
                f"💥 CRASH à x{game['crash_point']}\n\n❌ Perdu.",
                chat_id,
                message_id
            )
            crash_games.pop(user_id)
            return

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            f"💸 CASHOUT x{round(game['multiplier'],2)}",
            callback_data="crash_out"
        ))

        bot.edit_message_text(
            f"✈️ En vol...\n\nMultiplicateur: x{round(game['multiplier'],2)}",
            chat_id,
            message_id,
            reply_markup=markup
        )

        time.sleep(1)

@bot.callback_query_handler(func=lambda call: call.data == "crash_out")
def crash_out(call):
    user_id = call.from_user.id

    if user_id not in crash_games:
        return

    game = crash_games[user_id]
    gain = int(game["bet"] * game["multiplier"])

    user = get_user(user_id)
    update_balance(user_id, user[1] + gain)

    game["active"] = False
    crash_games.pop(user_id)

    bot.edit_message_text(
        f"💸 CASHOUT réussi !\n\nMultiplicateur: x{round(game['multiplier'],2)}\nGain: {gain} pts",
        call.message.chat.id,
        call.message.message_id
    )

# ================= ROCKET RISE (rapide) =================
@bot.message_handler(func=lambda m: m.text == "🚀 ROCKET RISE")
def rocket_rise(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user[1] < 100:
        bot.send_message(message.chat.id, "❌ Minimum 100 pts.")
        return

    crash = round(random.uniform(1.0, 7.0), 2)

    update_balance(user_id, user[1] - 100)

    gain = int(100 * crash)
    update_balance(user_id, get_user(user_id)[1] + gain)

    bot.send_message(
        message.chat.id,
        f"🚀 Rocket Rise\n\n💥 Crash à x{crash}\n\n💰 Gain: {gain} pts",
        reply_markup=main_menu(user_id)
    )

# ================= MINES =================
@bot.message_handler(func=lambda m: m.text == "🎮 MINES 5x5")
def start_game(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user[1] < 100:
        bot.send_message(message.chat.id, "❌ Minimum 100 pts.")
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
    markup.add(types.InlineKeyboardButton(
        f"💸 CASHOUT x{game['multiplier']}",
        callback_data="cashout"
    ))

    bot.send_message(chat_id, "🎮 Choisis une case :", reply_markup=markup)

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

@bot.callback_query_handler(func=lambda call: call.data == "cashout")
def cashout(call):
    user_id = call.from_user.id

    if user_id not in games:
        return

    game = games[user_id]
    gain = int(game["bet"] * game["multiplier"])

    user = get_user(user_id)
    update_balance(user_id, user[1] + gain)

    bot.edit_message_text(
        f"💸 CASHOUT réussi !\n\nGain: {gain} pts",
        call.message.chat.id,
        call.message.message_id
    )

    games.pop(user_id)

# ================= ADMIN =================
@bot.message_handler(func=lambda m: m.text == "🛡 QG")
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(balance) FROM users")
    total_balance = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"🛡 QG ADMIN\n\n👥 Utilisateurs: {total_users}\n💰 Total balance: {total_balance}"
    )

# ================= RUN =================
def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

app = Flask(__name__)

@app.route("/")
def home():
    return "CASINO PRO MAX Running"

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)