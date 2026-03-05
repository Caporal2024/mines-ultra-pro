import telebot
from telebot import types
import random
import time
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

AVIATOR_LINK = "https://1win.com/casino/play/aviator"
LUCKYJET_LINK = "https://1win.com/casino/play/luckyjet"

last_signal_time = 0
INTERVAL = 180


# MENU
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🔑 Login")
    btn2 = types.KeyboardButton("🎮 Open Game")
    btn3 = types.KeyboardButton("⏳ Next Signal")
    btn4 = types.KeyboardButton("📊 Odds History")
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
        "👑 CAPORAL PCS SIGNAL\n\nBienvenue 🚀",
        reply_markup=menu()
    )


# LOGIN
@bot.message_handler(func=lambda message: message.text == "🔑 Login")
def login(message):

    msg = bot.send_message(
        message.chat.id,
        "🔑 Envoie ton Player ID pour te connecter."
    )

    bot.register_next_step_handler(msg, connected)


def connected(message):

    player_id = message.text

    bot.send_message(
        message.chat.id,
        f"✅ Connexion réussie\n\nPlayer ID : {player_id}",
        reply_markup=menu()
    )


# OPEN GAME
@bot.message_handler(func=lambda message: message.text == "🎮 Open Game")
def game(message):

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

    now = time.time()

    if now - last_signal_time < INTERVAL:

        bot.send_message(
            message.chat.id,
            "⏳ Attends le prochain signal..."
        )

        return

    last_signal_time = now

    multiplier = round(random.uniform(1.70, 2.30), 2)

    bot.send_message(
        message.chat.id,
        f"""
🚀 SIGNAL AVIATOR

🎯 Cashout conseillé : {multiplier}x
💰 Mise recommandée : 5%

👑 CAPORAL PCS SIGNAL
"""
    )


# HISTORY
@bot.message_handler(func=lambda message: message.text == "📊 Odds History")
def history(message):

    numbers = []

    for i in range(10):

        numbers.append(str(round(random.uniform(1.0, 5.0), 2)))

    bot.send_message(
        message.chat.id,
        "📊 Historique :\n\n" + " | ".join(numbers)
    )


# VIP
@bot.message_handler(func=lambda message: message.text == "💎 VIP Access")
def vip(message):

    bot.send_message(
        message.chat.id,
        """
💎 VIP ACCESS

🚀 Signaux premium
📊 Statistiques avancées
🎯 Meilleurs multiplicateurs
"""
    )


bot.infinity_polling()