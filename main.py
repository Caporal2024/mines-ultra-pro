import os
import telebot
import random
import time
import threading

TOKEN = os.getenv("TOKEN")  # Ajoute ton token dans Railway

bot = telebot.TeleBot(TOKEN)

# Code secret pour accéder aux signaux
ACCESS_CODE = "PCS2026"

users = {}

# Message start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔐 Bienvenue dans le bot Aviator\n\n"
        "Pour accéder aux signaux envoie ton Player ID.\n"
        "Exemple : 12345678"
    )

# Réception Player ID
@bot.message_handler(func=lambda message: True)
def login(message):

    user_id = message.chat.id

    if user_id not in users:

        users[user_id] = {"player_id": message.text}

        bot.send_message(
            user_id,
            "🔑 Entre maintenant ton code d'accès."
        )

    elif users[user_id].get("access") != True:

        if message.text == ACCESS_CODE:

            users[user_id]["access"] = True

            bot.send_message(
                user_id,
                "✅ Accès autorisé\n\n"
                "📊 Les signaux Aviator arrivent..."
            )

            threading.Thread(target=signals, args=(user_id,)).start()

        else:

            bot.send_message(
                user_id,
                "❌ Code incorrect"
            )

# Génération de signaux
def signals(user_id):

    while True:

        entry = round(random.uniform(1.20, 1.60), 2)
        cashout = round(random.uniform(2.00, 3.50), 2)
        wait = random.randint(5, 15)

        message = f"""
🚀 SIGNAL AVIATOR

🎯 Entrée : {entry}x
💰 Cashout : {cashout}x

⏱ Attendre : {wait}s
⚡ Parier maintenant
"""

        bot.send_message(user_id, message)

        time.sleep(30)

bot.infinity_polling()