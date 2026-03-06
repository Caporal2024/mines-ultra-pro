import telebot
from telebot import types
import random

# AJOUTE TON TOKEN ICI
TOKEN = "PASTE_YOUR_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

# code secret pour accéder aux signaux
ACCESS_CODE = "2580"

# utilisateurs autorisés
authorized_users = []


# MENU
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔑 Login")
    btn2 = types.KeyboardButton("⏳ Next Signal")
    btn3 = types.KeyboardButton("🎮 Open Game")

    markup.add(btn1)
    markup.add(btn2, btn3)

    return markup


# START
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    login_btn = types.KeyboardButton("🔑 Login")
    markup.add(login_btn)

    bot.send_message(
        message.chat.id,
        "🚀 Bienvenue\n\nClique sur 🔑 Login pour accéder aux signaux Aviator.",
        reply_markup=markup
    )


# LOGIN
@bot.message_handler(func=lambda message: message.text == "🔑 Login")
def login(message):

    msg = bot.send_message(
        message.chat.id,
        "🔐 Entre le code d'accès :"
    )

    bot.register_next_step_handler(msg, check_code)


def check_code(message):

    if message.text == ACCESS_CODE:

        authorized_users.append(message.chat.id)

        bot.send_message(
            message.chat.id,
            "✅ Accès autorisé !",
            reply_markup=main_menu()
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Code incorrect."
        )


# SIGNAL AVIATOR
@bot.message_handler(func=lambda message: message.text == "⏳ Next Signal")
def aviator_signal(message):

    if message.chat.id not in authorized_users:

        bot.send_message(
            message.chat.id,
            "🔒 Tu dois d'abord te connecter."
        )
        return

    entry = round(random.uniform(1.20, 1.50), 2)
    cashout = round(random.uniform(2.00, 3.50), 2)

    signal = f"""
🚀 SIGNAL AVIATOR

🎯 Entrée : {entry}x
💰 Cashout : {cashout}x

⚡ Parier maintenant
"""

    bot.send_message(message.chat.id, signal)


# RUN BOT
print("Bot démarré...")
bot.infinity_polling()