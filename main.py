import telebot
from telebot import types
import os
import random

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# 🔐 Code d'accès
ACCESS_CODES = ["CAPORAL123"]
authorized_users = []

users = {}

# 📋 Menu principal
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Signal Aviator")
    btn2 = types.KeyboardButton("📊 Prochain Signal")
    markup.add(btn1, btn2)
    return markup

# ▶️ Démarrage du bot
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if user_id in authorized_users:
        bot.send_message(user_id, "✅ Bienvenue sur CAPORAL PCS SIGNAL", reply_markup=menu())
    else:
        msg = bot.send_message(user_id, "🔐 Entrez votre code d'accès pour utiliser le bot :")
        bot.register_next_step_handler(msg, check_code)

# 🔍 Vérification du code
def check_code(message):
    user_id = message.from_user.id
    code = message.text

    if code in ACCESS_CODES:
        authorized_users.append(user_id)
        bot.send_message(user_id, "✅ Code correct. Accès autorisé.", reply_markup=menu())
    else:
        bot.send_message(user_id, "❌ Code incorrect. Contactez l'administrateur.")

# 🚀 Génération signal Aviator
@bot.message_handler(func=lambda message: message.text == "🚀 Signal Aviator")
def signal(message):
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "🔐 Vous devez entrer un code pour utiliser le bot.")
        return

    crash = round(random.uniform(1.50, 5.00), 2)

    bot.send_message(
        message.chat.id,
        f"""
🚀 **SIGNAL AVIATOR**

💰 Cashout conseillé : {crash}x
⚡ Jouez maintenant !

CAPORAL PCS SIGNAL
"""
    )

# 📊 Prochain signal
@bot.message_handler(func=lambda message: message.text == "📊 Prochain Signal")
def next_signal(message):
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "🔐 Accès refusé.")
        return

    bot.send_message(message.chat.id, "⏳ Analyse du prochain signal...")

bot.infinity_polling()