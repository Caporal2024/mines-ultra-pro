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
    balance INTEGER DEFAULT 2000
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS crash_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game TEXT,
    multiplier REAL
)
""")

conn.commit()

ADMIN_ID = 123456789

# ================= GLOBAL GAME ENGINE =================
game_data = {
    "active": False,
    "game": None,
    "multiplier": 1.0,
    "crash_point": 0,
    "speed": 0.5,
    "players": {},
    "message_id": None,
    "chat_id": None,
    "lock": threading.Lock()
}

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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛩 SKY AVIATOR")
    markup.add("🚀 LUCKY ROCKET")
    markup.add("📊 HISTORIQUE")
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
        f"🎰 CASINO LIVE\n\n💰 Solde: {user[1]} pts",
        reply_markup=main_menu(message.from_user.id)
    )

# ================= JOIN GAME =================
def join_game(message, game_type):

    user_id = message.from_user.id
    user = get_user(user_id)
    bet = 100

    if user[1] < bet:
        bot.send_message(message.chat.id, "❌ Solde insuffisant.")
        return

    with game_data["lock"]:

        if not game_data["active"]:
            start_round(message.chat.id, game_type)

        update_balance(user_id, user[1] - bet)

        game_data["players"][user_id] = {
            "bet": bet,
            "auto": None,
            "cashed": False
        }

    bot.send_message(user_id, "🔥 Entré dans la manche !\nTape: auto 2.0\nTape: cashout")

# ================= START ROUND =================
def start_round(chat_id, game_type):

    game_data["active"] = True
    game_data["game"] = game_type
    game_data["multiplier"] = 1.0
    game_data["players"] = {}
    game_data["chat_id"] = chat_id

    if game_type == "AVIATOR":
        game_data["crash_point"] = round(random.uniform(1.5, 8.0), 2)
        game_data["speed"] = 0.5
        title = "🛩 SKY AVIATOR"
    else:
        game_data["crash_point"] = round(random.uniform(1.1, 5.0), 2)
        game_data["speed"] = 0.3
        title = "🚀 LUCKY ROCKET ⚡"

    msg = bot.send_message(chat_id, f"{title}\n\n🔥 Décollage...\n\nx1.00")
    game_data["message_id"] = msg.message_id

    threading.Thread(target=run_round, daemon=True).start()

# ================= RUN ROUND =================
def run_round():

    while game_data["active"]:
        time.sleep(game_data["speed"])

        with game_data["lock"]:
            game_data["multiplier"] += round(random.uniform(0.10, 0.25), 2)

            # AUTO CASHOUT
            for uid, data in list(game_data["players"].items()):
                if data["auto"] and not data["cashed"]:
                    if game_data["multiplier"] >= data["auto"]:
                        gain = int(data["bet"] * game_data["multiplier"])
                        user = get_user(uid)
                        update_balance(uid, user[1] + gain)
                        data["cashed"] = True
                        bot.send_message(uid, f"🤖 Auto cashout x{data['auto']} | Gain: {gain}")

            # CRASH
            if game_data["multiplier"] >= game_data["crash_point"]:

                crash_value = game_data["crash_point"]

                cursor.execute(
                    "INSERT INTO crash_history (game, multiplier) VALUES (?,?)",
                    (game_data["game"], crash_value)
                )
                conn.commit()

                bot.edit_message_text(
                    f"💥 CRASH à x{crash_value}",
                    game_data["chat_id"],
                    game_data["message_id"]
                )

                for uid, data in game_data["players"].items():
                    if not data["cashed"]:
                        bot.send_message(uid, "❌ Perdu.")

                game_data["active"] = False
                return

            # UPDATE LIVE MESSAGE
            bot.edit_message_text(
                f"{'🛩 SKY AVIATOR' if game_data['game']=='AVIATOR' else '🚀 LUCKY ROCKET ⚡'}\n\n🔥 En vol...\n\nx{round(game_data['multiplier'],2)}",
                game_data["chat_id"],
                game_data["message_id"]
            )

# ================= HANDLERS =================
@bot.message_handler(func=lambda m: m.text == "🛩 SKY AVIATOR")
def aviator(message):
    join_game(message, "AVIATOR")

@bot.message_handler(func=lambda m: m.text == "🚀 LUCKY ROCKET")
def rocket(message):
    join_game(message, "ROCKET")

@bot.message_handler(func=lambda m: m.text.startswith("auto "))
def auto_cash(message):
    user_id = message.from_user.id
    try:
        value = float(message.text.split()[1])
        if user_id in game_data["players"]:
            game_data["players"][user_id]["auto"] = value
            bot.send_message(user_id, f"🤖 Auto réglé à x{value}")
    except:
        bot.send_message(user_id, "Format: auto 2.0")

@bot.message_handler(func=lambda m: m.text == "cashout")
def manual_cash(message):
    user_id = message.from_user.id
    if user_id in game_data["players"]:
        data = game_data["players"][user_id]
        if not data["cashed"]:
            gain = int(data["bet"] * game_data["multiplier"])
            user = get_user(user_id)
            update_balance(user_id, user[1] + gain)
            data["cashed"] = True
            bot.send_message(user_id, f"💸 Cashout à x{round(game_data['multiplier'],2)} | Gain: {gain}")

@bot.message_handler(func=lambda m: m.text == "📊 HISTORIQUE")
def history(message):
    cursor.execute("SELECT game,multiplier FROM crash_history ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()

    text = "📊 10 derniers crashs:\n\n"
    for r in rows:
        text += f"{r[0]} ➜ x{r[1]}\n"

    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "💰 BALANCE")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 Solde: {user[1]} pts")

# ================= RUN =================
def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

app = Flask(__name__)

@app.route("/")
def home():
    return "CASINO LIVE RUNNING"

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)