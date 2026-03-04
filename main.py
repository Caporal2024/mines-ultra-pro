import telebot
from telebot import types
import random
import time
import os

# 🔑 Token Railway (ne mets pas ton token en dur)
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# ⏱ Intervalle entre signaux (4 minutes)
INTERVAL = 240
last_signal_time = 0

# 🔗 Mets tes vrais liens ici
AVIATOR_LINK = "https://tonsite.com/aviator"
LUCKYJET_LINK = "https://tonsite.com/luckyjet"
CHANNEL_LINK = "https://t.me/toncanal"

def generate_signal():
    return round(random.uniform(1.70, 2.30), 2)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👑 CAPORAL PCS SIGNAL\n\nTape /signal pour recevoir un signal live 🚀"
    )

@bot.message_handler(commands=['signal'])
def send_signal(message):
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

    # 🚀 Message NEW ROUND
    bot.send_message(message.chat.id, "🚀 NEW ROUND 🚀")

    time.sleep(2)

    # 🎮 Création des boutons
    markup = types.InlineKeyboardMarkup(row_width=1)

    logo_btn = types.InlineKeyboardButton(
        "⬜ H CAPORAL PCS SIGNAL",
        url=CHANNEL_LINK
    )

    aviator_btn = types.InlineKeyboardButton(
        "🎮 Ouvrir Aviator",
        url=AVIATOR_LINK
    )

    luckyjet_btn = types.InlineKeyboardButton(
        "🎮 Ouvrir Lucky Jet",
        url=LUCKYJET_LINK
    )

    markup.add(logo_btn)
    markup.add(aviator_btn)
    markup.add(luckyjet_btn)

    # 🟢 Signal final
    bot.send_message(
        message.chat.id,
        f"""
🟢 SIGNAL LIVE

🎯 Cashout conseillé : {multiplier}x
⚠️ Mise recommandée : 5% bankroll

💼 CAPORAL PCS SIGNAL
""",
        reply_markup=markup
    )

bot.infinity_polling()