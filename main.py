import telebot
from telebot import types
import random
import time

TOKEN = "PUT_YOUR_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

ACCESS_CODE = "12345"
users = {}

def aviator_signal():
    entree = round(random.uniform(1.20,1.70),2)
    cashout = round(random.uniform(2.00,3.50),2)
    wait = random.randint(6,12)

    return f"""
🚀 SIGNAL AVIATOR

🎯 Entrée : {entree}x
💰 Cashout : {cashout}x

⏱ Attendre : {wait}s
⚡ Parier maintenant
"""


@bot.message_handler(commands=['start'])
def start(message):

    users[message.chat.id] = False

    bot.send_message(
        message.chat.id,
        "🔐 Entrez le code d'accès pour utiliser le bot."
    )


@bot.message_handler(func=lambda message: True)
def login(message):

    chat = message.chat.id

    if users.get(chat):

        if message.text == "Next Signal":

            bot.send_message(chat,"⏳ Analyse...")
            time.sleep(2)

            bot.send_message(chat, aviator_signal())

        return


    if message.text == ACCESS_CODE:

        users[chat] = True

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Next Signal")

        bot.send_message(
            chat,
            "✅ Accès autorisé",
            reply_markup=keyboard
        )

    else:

        bot.send_message(chat,"❌ Code incorrect")


print("Bot started...")

bot.infinity_polling()