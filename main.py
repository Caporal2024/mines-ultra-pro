import telebot
from telebot import types
import random
import time

TOKEN = "PUT_YOUR_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

users = {}

def aviator_signal():
    entree = round(random.uniform(1.20,1.70),2)
    cashout = round(random.uniform(2.00,3.50),2)

    return f"""
🚀 SIGNAL AVIATOR

🎯 Entrée : {entree}x
💰 Cashout : {cashout}x
"""

@bot.message_handler(commands=['start'])
def start(message):

    users[message.chat.id] = False

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🔑 Login")
    keyboard.add("🚀 Next Signal")

    bot.send_message(
        message.chat.id,
        "Bienvenue dans le bot Aviator",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: True)
def messages(message):

    chat = message.chat.id

    if message.text == "🔑 Login":

        bot.send_message(
            chat,
            "🆔 Envoie ton Player ID pour activer le bot."
        )

        users[chat] = "waiting_id"
        return

    if users.get(chat) == "waiting_id":

        users[chat] = True

        bot.send_message(
            chat,
            "✅ Player ID enregistré."
        )

        return

    if message.text == "🚀 Next Signal":

        if users.get(chat) != True:

            bot.send_message(
                chat,
                "⚠️ Tu dois d'abord envoyer ton Player ID avec 🔑 Login."
            )
            return

        bot.send_message(chat,"⏳ Analyse...")
        time.sleep(2)

        bot.send_message(chat, aviator_signal())

print("Bot lancé")
bot.infinity_polling()