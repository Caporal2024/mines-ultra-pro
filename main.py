import telebot
from telebot import types
import os
import random

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("TOKEN manquant")
    exit()

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
        "🚀 Bienvenue dans le BOT SIGNAL AVIATOR\n\n⚠️ Tu dois d'abord envoyer ton Player ID avec 🔑 Login.",
        reply_markup=menu()
    )


@bot.message_handler(func=lambda message: message.text == "🔑 Login")
def login(message):
    bot.send_message(message.chat.id, "🔑 Envoie ton Player ID pour te connecter.")


@bot.message_handler(func=lambda message: message.text and message.text.startswith("ID"))
def save_player_id(message):
    player_ids[message.chat.id] = message.text
    bot.send_message(message.chat.id, "✅ Player ID enregistré.\n\n🔐 Maintenant envoie le code d'accès.")


@bot.message_handler(func=lambda message: message.text == ACCESS_CODE)
def access_granted(message):

    if message.chat.id not in player_ids:
        bot.send_message(message.chat.id, "⚠️ Tu dois d'abord envoyer ton Player ID avec 🔑 Login.")
        return

    users[message.chat.id] = True
    bot.send_message(message.chat.id, "✅ Accès autorisé. Les signaux sont débloqués.")


@bot.message_handler(func=lambda message: message.text == "⏳ Next Signal")
def signal(message):

    if users.get(message.chat.id) != True:
        bot.send_message(message.chat.id, "❌ Accès refusé.\n⚠️ Tu dois d'abord envoyer ton Player ID avec 🔑 Login.")
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


@bot.message_handler(func=lambda message: message.text == "🎮 Open Game")
def open_game(message):
    bot.send_message(message.chat.id, "🎮 https://spribe.co/games/aviator")


@bot.message_handler(func=lambda message: message.text == "📊 Odds History")
def history(message):
    bot.send_message(message.chat.id, "📊 Fonction historique bientôt disponible.")


print("Bot Aviator lancé")

bot.infinity_polling()