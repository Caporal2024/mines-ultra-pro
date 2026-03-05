import telebot
import random
import time
import threading

# AJOUTE TON TOKEN ICI
TOKEN = "COLLE_TON_TOKEN_ICI"

bot = telebot.TeleBot(TOKEN)

users = {}

# message start
@bot.message_handler(commands=['start'])
def start(message):
    msg = """
✈️ BOT SIGNAL AVIATOR

Bienvenue.

🔑 Pour utiliser le bot envoie ton Player ID.

Exemple :
12345678
"""
    bot.send_message(message.chat.id, msg)

# recevoir player id
@bot.message_handler(func=lambda message: True)
def get_player_id(message):

    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = message.text

        bot.send_message(
            message.chat.id,
            "✅ Player ID enregistré.\n\nLes prédictions Aviator vont commencer..."
        )

        threading.Thread(target=send_signals, args=(message.chat.id,)).start()


# générateur de signal
def generate_signal():

    entry = round(random.uniform(1.10,1.30),2)
    cashout = round(random.uniform(2.00,3.50),2)

    signal = f"""
✈️ SIGNAL AVIATOR

🎯 Entrée : {entry}x
💰 Cashout : {cashout}x

⏳ Attendre 2 tours
🔥 Parier maintenant
"""

    return signal


# envoyer signal automatiquement
def send_signals(chat_id):

    while True:

        signal = generate_signal()

        bot.send_message(chat_id, signal)

        time.sleep(60)


print("Bot Aviator lancé...")

bot.infinity_polling()