import os
import telebot
from telebot import types
import random

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# CODE SECRET POUR UTILISER LE BOT
ACCESS_CODE = "PCS2026"

authorized_users = {}
player_ids = {}

# START
@bot.message_handler(commands=['start'])
def start(message):

    msg = bot.send_message(
        message.chat.id,
        "🔐 Entrez le code d'accès pour utiliser ce bot :"
    )

    bot.register_next_step_handler(msg, check_code)

# VERIFIER CODE
def check_code(message):

    if message.text == ACCESS_CODE:

        authorized_users[message.chat.id] = True

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("🔑 Login", "🎮 Open Game")
        markup.row("⏳ Next Signal", "📊 Odds History")
        markup.row("💎 VIP Access")

        bot.send_message(
            message.chat.id,
            "👑 CAPORAL PCS SIGNAL\n\nBienvenue 🚀",
            reply_markup=markup
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Code incorrect. Accès refusé."
        )

# LOGIN PLAYER ID
@bot.message_handler(func=lambda m: m.text == "🔑 Login")
def login(message):

    if message.chat.id not in authorized_users:
        bot.send_message(message.chat.id,"⛔ Accès refusé")
        return

    msg = bot.send_message(
        message.chat.id,
        "🔑 Envoie ton Player ID pour te connecter."
    )

    bot.register_next_step_handler(msg, save_id)

def save_id(message):

    player_ids[message.chat.id] = message.text

    bot.send_message(
        message.chat.id,
        f"✅ Connexion réussie\n\nPlayer ID : {message.text}"
    )

# SIGNAL
@bot.message_handler(func=lambda m: m.text == "⏳ Next Signal")
def signal(message):

    if message.chat.id not in player_ids:

        bot.send_message(
            message.chat.id,
            "⚠️ Tu dois d'abord envoyer ton Player ID avec 🔑 Login."
        )
        return

    crash = round(random.uniform(1.20,5.00),2)

    bot.send_message(
        message.chat.id,
        f"🚀 SIGNAL\n\nMultiplier prévu : {crash}x\n\nCashout avant {crash}x"
    )

# HISTORIQUE
@bot.message_handler(func=lambda m: m.text == "📊 Odds History")
def history(message):

    odds = []

    for i in range(5):
        odds.append(str(round(random.uniform(1.10,5.00),2))+"x")

    bot.send_message(
        message.chat.id,
        "📊 Historique :\n\n"+"\n".join(odds)
    )

print("Bot lancé...")
bot.infinity_polling()