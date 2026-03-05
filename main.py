import telebot
from telebot import types
import random
import time
import sqlite3
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 123456789  # mets ton ID Telegram ici

AVIATOR_LINK = "https://1win.com/casino/play/aviator"
LUCKYJET_LINK = "https://1win.com/casino/play/luckyjet"

INTERVAL = 240
last_signal_time = 0


# DATABASE
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER,
        player_id TEXT,
        active INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()


# MENU
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🔑 Login")
    btn2 = types.KeyboardButton("🎮 Open Game")
    btn3 = types.KeyboardButton("📊 Odds History")
    btn4 = types.KeyboardButton("⏳ Next Signal")
    btn5 = types.KeyboardButton("💎 VIP Access")

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5)

    return markup


# START
@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "👑 CAPORAL PCS SIGNAL\n\nBienvenue dans le bot officiel 🚀",
        reply_markup=main_menu()
    )


# LOGIN
@bot.message_handler(func=lambda message: message.text == "🔑 Login")
def login(message):

    msg = bot.send_message(
        message.chat.id,
        "🔑 Envoie ton Player ID pour te connecter."
    )

    bot.register_next_step_handler(msg, save_player_id)


def save_player_id(message):

    player_id = message.text
    user_id = message.from_user.id

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users VALUES(?,?,?)",
        (user_id, player_id, 0)
    )

    conn.commit()
    conn.close()

    bot.send_message(
        message.chat.id,
        "⏳ Ton compte est en attente d'activation par l'admin."
    )


# CHECK USER
def check_user(user_id):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT active FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result


# OPEN GAME
@bot.message_handler(func=lambda message: message.text == "🎮 Open Game")
def open_game(message):

    user_id = message.from_user.id
    result = check_user(user_id)

    if result is None:
        bot.send_message(message.chat.id, "❌ Tu dois te connecter avec 🔑 Login")
        return

    if result[0] == 0:
        bot.send_message(message.chat.id, "❌ Ton accès n'est pas activé.")
        return

    markup = types.InlineKeyboardMarkup()

    aviator = types.InlineKeyboardButton(
        "✈️ Aviator",
        url=AVIATOR_LINK
    )

    lucky = types.InlineKeyboardButton(
        "🚀 Lucky Jet",
        url=LUCKYJET_LINK
    )

    markup.add(aviator)
    markup.add(lucky)

    bot.send_message(
        message.chat.id,
        "🎮 Choisis ton jeu :",
        reply_markup=markup
    )


# SIGNAL
@bot.message_handler(func=lambda message: message.text == "⏳ Next Signal")
def signal(message):

    global last_signal_time

    user_id = message.from_user.id
    result = check_user(user_id)

    if result is None or result[0] == 0:
        bot.send_message(message.chat.id, "❌ Ton accès n'est pas activé.")
        return

    now = time.time()

    if now - last_signal_time < INTERVAL:

        remaining = int((INTERVAL - (now - last_signal_time)) / 60) + 1

        bot.send_message(
            message.chat.id,
            f"⏳ Prochain signal dans {remaining} minute(s)"
        )

        return

    last_signal_time = now

    multiplier = round(random.uniform(1.70, 2.30), 2)

    bot.send_message(message.chat.id, "🚀 NEW ROUND 🚀")

    time.sleep(2)

    bot.send_message(
        message.chat.id,
        f"""
🟢 SIGNAL LIVE

🎯 Cashout conseillé : {multiplier}x
⚠️ Mise recommandée : 5%

👑 CAPORAL PCS SIGNAL
"""
    )


# ODDS HISTORY
@bot.message_handler(func=lambda message: message.text == "📊 Odds History")
def history(message):

    history = []

    for i in range(10):
        history.append(str(round(random.uniform(1.0, 5.0), 2)))

    text = "📊 Historique des multiplicateurs\n\n"

    text += " | ".join(history)

    bot.send_message(message.chat.id, text)


# VIP
@bot.message_handler(func=lambda message: message.text == "💎 VIP Access")
def vip(message):

    bot.send_message(
        message.chat.id,
        """
💎 VIP ACCESS

Accès VIP donne :

🚀 signaux premium
📊 statistiques avancées
🎯 meilleurs multiplicateurs

Contact admin pour activer.
"""
    )


# ADMIN ACTIVATE
@bot.message_handler(commands=['activate'])
def activate(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        user_id = int(message.text.split()[1])

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET active=1 WHERE user_id=?",
            (user_id,)
        )

        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, "✅ Utilisateur activé")

    except:
        bot.send_message(message.chat.id, "❌ Erreur")


# ADMIN LIST
@bot.message_handler(commands=['users'])
def users(message):

    if message.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")

    rows = cursor.fetchall()

    text = "👥 UTILISATEURS\n\n"

    for r in rows:

        text += f"ID: {r[0]} | PlayerID: {r[1]} | Active: {r[2]}\n"

    bot.send_message(message.chat.id, text)


bot.infinity_polling()