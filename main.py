import telebot
from telebot import types
import random
import time
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

last_signal = 0
cooldown = 120

history = []

# -------- MENU PRINCIPAL --------

def menu():
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


# -------- START --------

@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "👑 *CAPORAL PCS SIGNAL*\n\nBot de signaux Aviator 🚀",
        parse_mode="Markdown",
        reply_markup=menu()
    )


# -------- LOGIN --------

@bot.message_handler(func=lambda m: m.text == "🔑 Login")
def login(message):

    bot.send_message(
        message.chat.id,
        "🔐 Connecte-toi ici :\nhttps://tonsite.com/login"
    )


# -------- OPEN GAME --------

@bot.message_handler(func=lambda m: m.text == "🎮 Open Game")
def open_game(message):

    bot.send_message(
        message.chat.id,
        "🎮 Ouvre Aviator ici :\nhttps://tonsite.com/aviator"
    )


# -------- HISTORY --------

@bot.message_handler(func=lambda m: m.text == "📊 Odds History")
def history_odds(message):

    if not history:
        bot.send_message(message.chat.id, "Aucun historique.")
        return

    text = "📊 Historique Aviator :\n\n"

    for h in history[-10:]:
        text += f"{h}x\n"

    bot.send_message(message.chat.id, text)


# -------- SIGNAL --------

@bot.message_handler(func=lambda m: m.text == "⏳ Next Signal")
def signal(message):

    global last_signal

    now = time.time()

    if now - last_signal < cooldown:

        wait = int(cooldown - (now - last_signal))

        bot.send_message(
            message.chat.id,
            f"⏳ Prochain signal dans {wait} secondes"
        )
        return

    last_signal = now

    multiplier = round(random.uniform(1.5, 2.5), 2)

    history.append(multiplier)

    bot.send_message(
        message.chat.id,
        f"""
🚀 *SIGNAL AVIATOR*

🎯 Cashout : *{multiplier}x*

⚠️ Mise : 5% bankroll
""",
        parse_mode="Markdown"
    )


# -------- VIP --------

@bot.message_handler(func=lambda m: m.text == "💎 VIP Access")
def vip(message):

    bot.send_message(
        message.chat.id,
        "💎 VIP disponible ici :\nhttps://t.me/toncanalvip"
    )


# -------- RUN BOT --------

bot.infinity_polling()