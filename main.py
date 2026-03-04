import telebot
import random
import time
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

VIP_USERS = ["123456789"]  # Mets ici les chat_id VIP

def generate_signal():
    return round(random.uniform(1.50, 2.20), 2)

def send_signal(chat_id, vip=False):
    multiplier = generate_signal()

    message = f"""
🟢 SIGNAL LIVE {'VIP' if vip else 'FREE'}
🎯 Cashout conseillé : {multiplier}x
⚠️ Mise : 5% bankroll
"""

    bot.send_message(chat_id, message)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
    "Bienvenue 👑\nTape /signal pour recevoir un signal.")

@bot.message_handler(commands=['signal'])
def signal(message):
    if str(message.chat.id) in VIP_USERS:
        send_signal(message.chat.id, vip=True)
    else:
        send_signal(message.chat.id, vip=False)

bot.infinity_polling()