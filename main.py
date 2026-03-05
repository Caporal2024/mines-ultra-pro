import telebot
from telebot import types
import random
import time
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

INTERVAL = 240
last_signal_time = 0

AVIATOR_LINK = "https://tonsite.com/aviator"
LUCKYJET_LINK = "https://tonsite.com/luckyjet"
VIP_LINK = "https://t.me/toncanal"

def generate_signal():
    return round(random.uniform(1.70, 2.30), 2)


# MENU PRINCIPAL
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


@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "👑 CAPORAL PCS SIGNAL\n\nEnter your Player ID",
        reply_markup=main_menu()
    )


# LOGIN
@bot.message_handler(func=lambda message: message.text == "🔑 Login")
def login(message):

    bot.send_message(
        message.chat.id,
        "🔑 Envoie ton Player ID pour te connecter."
    )


# OPEN GAME
@bot.message_handler(func=lambda message: message.text == "🎮 Open Game")
def open_game(message):

    markup = types.InlineKeyboardMarkup()

    aviator = types.InlineKeyboardButton(
        "🚀 Aviator",
        url=AVIATOR_LINK
    )

    luckyjet = types.InlineKeyboardButton(
        "✈️ Lucky Jet",
        url=LUCKYJET_LINK
    )

    markup.add(aviator)
    markup.add(luckyjet)

    bot.send_message(
        message.chat.id,
        "🎮 Choisis ton jeu :",
        reply_markup=markup
    )


# ODDS HISTORY
@bot.message_handler(func=lambda message: message.text == "📊 Odds History")
def history(message):

    results = []

    for i in range(5):
        results.append(str(generate_signal()) + "x")

    bot.send_message(
        message.chat.id,
        "📊 Derniers multiplicateurs :\n\n" + "\n".join(results)
    )


# NEXT SIGNAL
@bot.message_handler(func=lambda message: message.text == "⏳ Next Signal")
def next_signal(message):

    global last_signal_time

    now = time.time()

    if now - last_signal_time < INTERVAL:

        remaining = int(INTERVAL - (now - last_signal_time))

        bot.send_message(
            message.chat.id,
            f"⏳ Next signal in {remaining} seconds"
        )

        return

    last_signal_time = now

    multiplier = generate_signal()

    bot.send_message(
        message.chat.id,
        "🚀 NEW ROUND 🚀"
    )

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


# VIP
@bot.message_handler(func=lambda message: message.text == "💎 VIP Access")
def vip(message):

    markup = types.InlineKeyboardMarkup()

    vip = types.InlineKeyboardButton(
        "💎 Rejoindre VIP",
        url=VIP_LINK
    )

    markup.add(vip)

    bot.send_message(
        message.chat.id,
        "💎 Accès VIP pour recevoir plus de signaux.",
        reply_markup=markup
    )


bot.infinity_polling()