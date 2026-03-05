import telebot
from telebot import types
import random
import time
import os
import threading

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

CHANNEL_ID = "@toncanal"

AVIATOR_LINK = "https://tonsite.com/aviator"
LUCKYJET_LINK = "https://tonsite.com/luckyjet"

INTERVAL = 240

history = []
players = {}

next_signal = time.time() + INTERVAL


def generate_multiplier():
    value = round(random.uniform(1.50, 2.50), 2)

    history.append(value)

    if len(history) > 20:
        history.pop(0)

    return value


def menu():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("🔑 Login", "🎮 Open Game")
    markup.row("📊 Odds History", "⏳ Next Signal")
    markup.row("💎 VIP Access")

    return markup


@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "👑 CAPORAL PCS SIGNAL\n\nEnter your Player ID",
        reply_markup=menu()
    )


@bot.message_handler(func=lambda m: m.text == "🔑 Login")
def login(message):

    msg = bot.send_message(message.chat.id, "Send Player ID")
    bot.register_next_step_handler(msg, save_player)


def save_player(message):

    players[message.chat.id] = message.text

    bot.send_message(
        message.chat.id,
        "✅ Player ID saved",
        reply_markup=menu()
    )


@bot.message_handler(func=lambda m: m.text == "🎮 Open Game")
def open_game(message):

    markup = types.InlineKeyboardMarkup()

    aviator = types.InlineKeyboardButton("🚀 Aviator", url=AVIATOR_LINK)
    lucky = types.InlineKeyboardButton("⚡ Lucky Jet", url=LUCKYJET_LINK)

    markup.add(aviator)
    markup.add(lucky)

    bot.send_message(message.chat.id, "Choose Game", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "📊 Odds History")
def odds(message):

    if not history:
        bot.send_message(message.chat.id, "No data yet")
        return

    text = "\n".join([f"{x}x" for x in history])

    bot.send_message(message.chat.id, f"📊 History\n\n{text}")


@bot.message_handler(func=lambda m: m.text == "⏳ Next Signal")
def next_signal_time(message):

    remaining = int(next_signal - time.time())

    if remaining < 0:
        remaining = 0

    minutes = remaining // 60
    seconds = remaining % 60

    bot.send_message(
        message.chat.id,
        f"⏳ Next signal in {minutes}m {seconds}s"
    )


@bot.message_handler(func=lambda m: m.text == "💎 VIP Access")
def vip(message):

    bot.send_message(
        message.chat.id,
        "💎 VIP ACCESS\n\nContact admin to join premium signals"
    )


def auto_signal():

    global next_signal

    while True:

        multiplier = generate_multiplier()

        markup = types.InlineKeyboardMarkup()

        aviator = types.InlineKeyboardButton(
            "🚀 Play Aviator",
            url=AVIATOR_LINK
        )

        lucky = types.InlineKeyboardButton(
            "⚡ Play Lucky Jet",
            url=LUCKYJET_LINK
        )

        markup.add(aviator)
        markup.add(lucky)

        bot.send_message(
            CHANNEL_ID,
            f"""
🚀 NEW ROUND

🟢 SIGNAL

🎯 Cashout : {multiplier}x
⚠️ Bet 5%

👑 CAPORAL PCS SIGNAL
""",
            reply_markup=markup
        )

        next_signal = time.time() + INTERVAL

        time.sleep(INTERVAL)


threading.Thread(target=auto_signal).start()

bot.infinity_polling()