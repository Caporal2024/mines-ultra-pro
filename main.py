import telebot
from telebot import types
import random
import time

from config import *
import database

bot = telebot.TeleBot(TOKEN)

INTERVAL = 240
last_signal_time = 0


def generate_signal():
    return round(random.uniform(1.7, 2.5), 2)


def main_menu():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🔑 Login")
    btn2 = types.KeyboardButton("🎮 Open Game")
    btn3 = types.KeyboardButton("📊 Odds History")
    btn4 = types.KeyboardButton("⏳ Next Signal")
    btn5 = types.KeyboardButton("💎 VIP Access")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)

    return markup


@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(
        message.chat.id,
        "👑 CAPORAL PCS SIGNAL\n\nEnter your Player ID",
        reply_markup=main_menu()
    )


# LOGIN
@bot.message_handler(func=lambda m: m.text == "🔑 Login")
def login(message):

    msg = bot.send_message(message.chat.id, "Envoie ton Player ID")

    bot.register_next_step_handler(msg, save_player)


def save_player(message):

    database.add_user(message.chat.id, message.text)

    bot.send_message(
        message.chat.id,
        "✅ Player ID enregistré"
    )


# OPEN GAME
@bot.message_handler(func=lambda m: m.text == "🎮 Open Game")
def open_game(message):

    markup = types.InlineKeyboardMarkup()

    aviator = types.InlineKeyboardButton(
        "🚀 Aviator",
        url=AVIATOR_LINK
    )

    lucky = types.InlineKeyboardButton(
        "✈️ Lucky Jet",
        url=LUCKYJET_LINK
    )

    markup.add(aviator)
    markup.add(lucky)

    bot.send_message(
        message.chat.id,
        "Choisis ton jeu",
        reply_markup=markup
    )


# SIGNAL
@bot.message_handler(func=lambda m: m.text == "⏳ Next Signal")
def signal(message):

    global last_signal_time

    now = time.time()

    if now - last_signal_time < INTERVAL:

        remaining = int((INTERVAL - (now - last_signal_time)) / 60) + 1

        bot.send_message(
            message.chat.id,
            f"⏳ prochain signal dans {remaining} minute(s)"
        )

        return

    last_signal_time = now

    multiplier = generate_signal()

    bot.send_message(
        message.chat.id,
        f"""
🚀 NEW ROUND

🎯 Cashout conseillé : {multiplier}x
⚠️ Mise recommandée : 5%

👑 CAPORAL PCS SIGNAL
"""
    )


# VIP
@bot.message_handler(func=lambda m: m.text == "💎 VIP Access")
def vip(message):

    bot.send_message(
        message.chat.id,
        "💎 Contacte l'admin pour accès VIP."
    )


# ADMIN VIP
@bot.message_handler(commands=["addvip"])
def addvip(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        user_id = int(message.text.split()[1])

        database.make_vip(user_id)

        bot.reply_to(message, "✅ VIP activé")

    except:

        bot.reply_to(message, "usage: /addvip user_id")


# STATS
@bot.message_handler(commands=["stats"])
def stats(message):

    if message.from_user.id != ADMIN_ID:
        return

    users = database.total_users()
    vip = database.total_vip()

    bot.send_message(
        message.chat.id,
        f"""
📊 STATISTIQUES

👥 utilisateurs : {users}
💎 VIP : {vip}
"""
    )


print("BOT STARTED")

bot.infinity_polling()