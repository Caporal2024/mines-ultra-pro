import telebot
from telebot import types
import random
import time
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

last_signal_time = 0
INTERVAL = 240  # 4 minutes

# 🔥 Mets ici tes vrais liens
AVIATOR_LINK = "https://tonsite.com/aviator"
LUCKYJET_LINK = "https://tonsite.com/luckyjet"

def generate_signal():
    return round(random.uniform(1.70, 2.20), 2)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👑 CAPORAL PCS SIGNAL\n\nTape /signal pour recevoir un signal live 🚀"
    )

@bot.message_handler(commands=['signal'])
def signal(message):
    global last_signal_time

    now = time.time()

    if now - last_signal_time < INTERVAL:
        remaining = int((INTERVAL - (now - last_signal_time)) / 60) + 1
        bot.send_message(
            message.chat.id,
            f"⏳ Prochain signal dans {remaining} minute(s)"
        )
        return

    last_signal_time = now
    multiplier = generate_signal()

    # 🚀 NEW ROUND
    bot.send_message(message.chat.id, "🚀 NEW ROUND 🚀")

    time.sleep(2)

    # 🎮 Création des boutons
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎮 Ouvrir Aviator", url=AVIATOR_LINK)
    btn2 = types.InlineKeyboardButton("🎮 Ouvrir Lucky Jet", url=LUCKYJET_LINK)

    markup.add(btn1)
    markup.add(btn2)

    # 🟢 SIGNAL + boutons
    bot.send_message(
        message.chat.id,
        f"""
🟢 SIGNAL LIVE

🎯 Cashout conseillé : {multiplier}x
⚠️ Mise : 5% bankroll

💼 CAPORAL PCS SIGNAL
""",
        reply_markup=markup
    )

bot.infinity_polling()