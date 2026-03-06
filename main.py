import telebot
from telebot import types
import os
import random

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

ACCESS_CODE = "CAPORAL123"
users = {}
player_ids = {}

def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔑 Login")
    btn2 = types.KeyboardButton("🎮 Open Game")
    btn3 = types.KeyboardButton("⏳ Next Signal")
    btn4 = types.KeyboardButton("📊 Odds History")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚀 Bienvenue dans le BOT SIGNAL AVIATOR",
        reply_markup=menu()
    )


# LOGIN
@bot.message_handler(func=lambda message: message.text == "🔑 Login")
def login(message):
    bot.send_message(message.chat.id, "Send Player ID")


# SAVE PLAYER ID
@bot.message_handler(func=lambda message: message.text.isdigit())
def save_player_id(message):
    player_ids[message.chat.id] = message.text
    bot.send_message(message.chat.id, "✅ Player ID saved")


# ACCESS CODE
@bot.message_handler(func=lambda message: message.text == ACCESS_CODE)
def access_granted(message):
    users[message.chat.id] = True
    bot.send_message(message.chat.id, "✅ Access granted. Signals unlocked.")


# SIGNAL
@bot.message_handler(func=lambda message: message.text == "⏳ Next Signal")
def signal(message):

    if message.chat.id not in player_ids:
        bot.send_message(message.chat.id, "⚠️ Send Player ID first.")
        return

    entree = round(random.uniform(1.20, 1.60), 2)
    cashout = round(random.uniform(2.00, 3.50), 2)
    attendre = random.randint(5, 12)

    msg = f"""
🚀 SIGNAL AVIATOR

🎯 Entrée : {entree}x
💰 Cashout : {cashout}x

⏱ Attendre : {attendre}s
⚡ Parier maintenant
"""

    bot.send_message(message.chat.id, msg)


# OPEN GAME
@bot.message_handler(func=lambda message: message.text == "🎮 Open Game")
def open_game(message):
    bot.send_message(message.chat.id, "🎮 https://spribe.co/games/aviator")


# HISTORY
@bot.message_handler(func=lambda message: message.text == "📊 Odds History")
def history(message):
    bot.send_message(message.chat.id, "📊 Fonction historique bientôt disponible.")


print("Bot Aviator lancé")

bot.infinity_polling()