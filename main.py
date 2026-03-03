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
    multiplier REAL
)
""")

conn.commit()

ADMIN_ID = 123456789

# ================= GLOBAL CRASH =================
crash_data = {
    "active": False,
    "multiplier": 1.0,
    "crash_point": 0,
    "players": {},
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
    markup.add("🎮 MINES 5x5")
    markup.add("✈️ JET CRASH")
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
        f"🎰 CASINO PRO MAX\n\n💰 Solde: {user[1]} pts",
        reply_markup=main_menu(message.from_user.id)
    )

# ================= BALANCE =================
@bot.message_handler(func=lambda m: m.text == "💰 BALANCE")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 Solde: {user[1]} pts")

# ================= JOIN GLOBAL CRASH =================
@bot.message_handler(func=lambda m: m.text == "✈️ JET CRASH")
def join_crash(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    bet = 100

    if user[1] < bet:
        bot.send_message(message.chat.id, "❌ Solde insuffisant.")
        return

    with crash_data["lock"]:
        if not crash_data["active"]:
            start_crash_round()

        update_balance(user_id, user[1] - bet)

        crash_data["players"][user_id] = {
            "bet": bet,
            "auto": None,
            "cashed": False
        }

    bot.send_message(
        message.chat.id,
        "🔥 Partie rejointe !\nEnvoie: auto 2.0 pour auto cashout\nEnvoie: cashout pour retirer manuellement"
    )

# ================= START ROUND =================
def start_crash_round():
    crash_data["active"] = True
    crash_data["multiplier"] = 1.0
    crash_data["crash_point"] = round(random.uniform(1.5, 8.0), 2)
    crash_data["players"] = {}

    threading.Thread(target=run_crash, daemon=True).start()

# ================= RUN CRASH =================
def run_crash():
    while crash_data["active"]:
        time.sleep(0.8)

        with crash_data["lock"]:
            crash_data["multiplier"] += round(random.uniform(0.10, 0.30), 2)

            # AUTO CASHOUT
            for user_id, data in list(crash_data["players"].items()):
                if data["auto"] and not data["cashed"]:
                    if crash_data["multiplier"] >= data["auto"]:
                        gain = int(data["bet"] * crash_data["multiplier"])
                        user = get_user(user_id)
                        update_balance(user_id, user[1] + gain)
                        data["cashed"] = True
                        bot.send_message(user_id, f"🤖 Auto cashout à x{data['auto']} | Gain: {gain}")

            # CRASH
            if crash_data["multiplier"] >= crash_data["crash_point"]:
                crash_value = crash_data["crash_point"]

                cursor.execute("INSERT INTO crash_history (multiplier) VALUES (?)", (crash_value,))
                conn.commit()

                for user_id, data in crash_data["players"].items():
                    if not data["cashed"]:
                        bot.send_message(user_id, f"💥 Crash à x{crash_value} ❌ Perdu")

                crash_data["active"] = False
                return

# ================= MANUAL CASHOUT =================
@bot.message_handler(func=lambda m: m.text == "cashout")
def manual_cashout(message):
    user_id = message.from_user.id

    with crash_data["lock"]:
        if user_id not in crash_data["players"]:
            return

        data = crash_data["players"][user_id]

        if data["cashed"]:
            return

        gain = int(data["bet"] * crash_data["multiplier"])
        user = get_user(user_id)
        update_balance(user_id, user[1] + gain)

        data["cashed"] = True

    bot.send_message(
        message.chat.id,
        f"💸 Cashout manuel à x{round(crash_data['multiplier'],2)} | Gain: {gain}"
    )

# ================= AUTO CASHOUT =================
@bot.message_handler(func=lambda m: m.text.startswith("auto "))
def set_auto(message):
    user_id = message.from_user.id

    try:
        value = float(message.text.split()[1])
    except:
        bot.send_message(message.chat.id, "Format: auto 2.0")
        return

    with crash_data["lock"]:
        if user_id in crash_data["players"]:
            crash_data["players"][user_id]["auto"] = value
            bot.send_message(message.chat.id, f"🤖 Auto réglé à x{value}")

# ================= HISTORY =================
@bot.message_handler(func=lambda m: m.text == "📊 HISTORIQUE")
def history(message):
    cursor.execute("SELECT multiplier FROM crash_history ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()

    if not rows:
        bot.send_message(message.chat.id, "Aucun historique.")
        return

    text = "📊 10 derniers crashs:\n\n"
    for row in rows:
        text += f"x{row[0]}\n"

    bot.send_message(message.chat.id, text)

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
        f"🛡 QG\n\n👥 Users: {total_users}\n💰 Total balance: {total_balance}"
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