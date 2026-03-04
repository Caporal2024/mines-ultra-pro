import telebot
import random
import time
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

last_signal_time = 0
INTERVAL = 240  # 4 minutes

def generate_signal():
    return round(random.uniform(1.70, 2.20), 2)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
    "Bienvenue 👑\nTape /signal pour recevoir un signal.")

@bot.message_handler(commands=['signal'])
def signal(message):
    global last_signal_time

    now = time.time()

    if now - last_signal_time < INTERVAL:
        remaining = int((INTERVAL - (now - last_signal_time)) / 60) + 1
        bot.send_message(message.chat.id,
        f"⏳ Prochain signal dans {remaining} minute(s)")
        return

    last_signal_time = now
    multiplier = generate_signal()

    bot.send_message(message.chat.id, f"""
🟢 SIGNAL LIVE
🎯 Cashout conseillé : {multiplier}x
⚠️ Mise : 5% bankroll
""")

bot.infinity_polling()