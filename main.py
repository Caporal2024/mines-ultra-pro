import telebot
from telebot import types
import random
import time

TOKEN = "METS_TON_TOKEN_ICI"

bot = telebot.TeleBot(TOKEN)

# code secret
ACCESS_CODE = "2580"

# utilisateurs autorisés
users_ok = []

# menu principal
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔑 Login")
    btn2 = types.KeyboardButton("🎮 Open Game")
    btn3 = types.KeyboardButton("⏳ Next Signal")
    btn4 = types.KeyboardButton("📊 Odds History")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)

    return markup


@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("🔑 Login")
    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "🔐 Bienvenue\n\nClique sur Login pour accéder aux signaux Aviator.",
        reply_markup=markup
    )


# LOGIN
@bot.message_handler(func=lambda m: m.text == "🔑 Login")
def login(message):
    msg = bot.send_message(
        message.chat.id,
        "🔑 Envoie ton code d'accès :"
    )

    bot.register_next_step_handler(msg, check_code)


def check_code(message):

    if message.text == ACCESS_CODE:

        users_ok.append(message.chat.id)

        bot.send_message(
            message.chat.id,
            "✅ Accès autorisé !",
            reply_markup=menu()
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Code incorrect."
        )


# SIGNAL AVIATOR
@bot.message_handler(func=lambda m: m.text == "⏳ Next Signal")
def signal(message):

    if message.chat.id not in users_ok:
        bot.send_message(message.chat.id, "🔒 Tu dois d'abord te connecter.")
        return

    entree = round(random.uniform(1.20, 1.60), 2)
    cashout = round(random.uniform(2.00, 3.50), 2)
    attente = random.randint(5, 15)

    text = f"""
🚀 SIGNAL AVIATOR

🎯 Entrée : {entree}x
💰 Cashout : {cashout}x

⏱ Attendre : {attente}s
⚡ Parier maintenant
"""

    bot.send_message(message.chat.id, text)


bot.infinity_polling()