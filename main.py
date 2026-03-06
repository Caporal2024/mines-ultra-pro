import telebot
from telebot import types
import random
import time
import os

TOKEN = "PUT_YOUR_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

ACCESS_CODE = "CaporalPCS"

users = {}

def signal():
    entree = round(random.uniform(1.20,1.70),2)
    cashout = round(random.uniform(2.00,3.50),2)
    wait = random.randint(6,12)

    msg = f"""
🚀 SIGNAL AVIATOR

🎯 Entrée : {entree}x
💰 Cashout : {cashout}x

⏱ Attendre : {wait}s
⚡ Parier maintenant
"""

    return msg


@bot.message_handler(commands=['start'])
def start(message):

    users[message.chat.id] = False

    bot.send_message(
        message.chat.id,
        "🔐 Accès privé\n\nEntre ton code pour utiliser le bot."
    )


@bot.message_handler(func=lambda message: True)
def login(message):

    chat = message.chat.id

    if users.get(chat) == True:

        if message.text == "Next Signal":

            bot.send_message(chat,"⏳ Analyse en cours...")
            time.sleep(2)

            bot.send_message(chat, signal())

        return


    if message.text == ACCESS_CODE:

        users[chat] = True

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Next Signal")

        bot.send_message(
            chat,
            "✅ Accès autorisé\n\nClique sur Next Signal pour recevoir une prédiction.",
            reply_markup=markup
        )

    else:

        bot.send_message(chat,"❌ Code incorrect.")


print("BOT STARTED")

bot.infinity_polling()