import telebot
from telebot import types
import random
import sqlite3
import time
import threading

TOKEN = "COLLE_TON_TOKEN_ICI"

bot = telebot.TeleBot(TOKEN)

# Base de données
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER,
    player_id TEXT,
    active INTEGER
)
""")
conn.commit()

# Code secret pour utiliser le bot
ACCESS_CODE = "PCS2026"


# MENU
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Aviator Signal")
    btn2 = types.KeyboardButton("✈️ Lucky Jet Signal")
    markup.add(btn1, btn2)
    return markup


# START
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔑 Bienvenue dans le BOT SIGNAL\n\nEnvoie le code d'accès pour continuer."
    )


# CODE ACCES
@bot.message_handler(func=lambda message: True)
def check_access(message):

    user_id = message.chat.id

    if message.text == ACCESS_CODE:

        cursor.execute(
            "INSERT INTO users (id, player_id, active) VALUES (?, ?, ?)",
            (user_id, "", 0)
        )
        conn.commit()

        bot.send_message(
            user_id,
            "🔑 Envoie ton Player ID pour te connecter."
        )
        return

    # PLAYER ID
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if user:

        if user[1] == "":
            cursor.execute(
                "UPDATE users SET player_id=?, active=1 WHERE id=?",
                (message.text, user_id)
            )
            conn.commit()

            bot.send_message(
                user_id,
                "✅ Connexion réussie !",
                reply_markup=menu()
            )
            return

        if message.text == "🚀 Aviator Signal":
            send_aviator_signal(user_id)

        if message.text == "✈️ Lucky Jet Signal":
            send_lucky_signal(user_id)


# SIGNAL AVIATOR
def send_aviator_signal(chat_id):

    entree = round(random.uniform(1.10, 1.30), 2)
    cashout = round(random.uniform(2.00, 3.00), 2)

    signal = f"""
🚀 SIGNAL AVIATOR

🎯 Entrée : {entree}x
💰 Cashout : {cashout}x

⏱ Attendre 2 tours
🔥 Mise : 1000F
"""

    bot.send_message(chat_id, signal)


# SIGNAL LUCKY JET
def send_lucky_signal(chat_id):

    entree = round(random.uniform(1.10, 1.30), 2)
    cashout = round(random.uniform(2.00, 3.00), 2)

    signal = f"""
✈️ SIGNAL LUCKY JET

🎯 Entrée : {entree}x
💰 Cashout : {cashout}x

⏱ Attendre 2 tours
🔥 Mise : 1000F
"""

    bot.send_message(chat_id, signal)


print("Bot en marche...")
bot.infinity_polling()