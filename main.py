import telebot
from telebot import types
import random
import time
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# 🔑 TON ID TELEGRAM ADMIN
ADMIN_ID = 123456789

players = {}
active_users = set()

INTERVAL = 240
last_signal_time = 0

AVIATOR_LINK = "https://tonsite.com/aviator"
LUCKYJET_LINK = "https://tonsite.com/luckyjet"
CHANNEL_LINK = "https://t.me/toncanal"


def generate_signal():
    return round(random.uniform(1.70, 2.30), 2)


# MENU
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    login = types.KeyboardButton("🔑 Login")
    open_game = types.KeyboardButton("🎮 Open Game")
    odds = types.KeyboardButton("📊 Odds History")
    next_signal = types.KeyboardButton("⏳ Next Signal")
    vip = types.KeyboardButton("💎 VIP Access")

    markup.add(login, open_game)
    markup.add(odds, next_signal)
    markup.add(vip)

    return markup


@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "👑 CAPORAL PCS SIGNAL\n\nEnter your Player ID",
        reply_markup=main_menu()
    )


# LOGIN
@bot.message_handler(func=lambda message: message.text == "🔑 Login")
def login(message):

    msg = bot.send_message(message.chat.id, "🔑 Envoie ton Player ID pour te connecter.")
    bot.register_next_step_handler(msg, save_player)


def save_player(message):

    player_id = message.text

    players[message.chat.id] = player_id

    bot.send_message(
        message.chat.id,
        "⏳ Ton compte est en attente d'activation par l'admin."
    )

    bot.send_message(
        ADMIN_ID,
        f"👤 Nouvel utilisateur\nID Telegram: {message.chat.id}\nPlayer ID: {player_id}"
    )


# ACTIVER UTILISATEUR
@bot.message_handler(commands=['activate'])
def activate_user(message):

    if message.chat.id != ADMIN_ID:
        return

    user_id = int(message.text.split()[1])

    active_users.add(user_id)

    bot.send_message(user_id, "✅ Ton accès aux signaux est activé.")


# BAN UTILISATEUR
@bot.message_handler(commands=['ban'])
def ban_user(message):

    if message.chat.id != ADMIN_ID:
        return

    user_id = int(message.text.split()[1])

    if user_id in active_users:
        active_users.remove(user_id)

    bot.send_message(user_id, "❌ Ton accès aux signaux est désactivé.")


# OPEN GAME
@bot.message_handler(func=lambda message: message.text == "🎮 Open Game")
def open_game(message):

    if message.chat.id not in active_users:
        bot.send_message(message.chat.id, "❌ Ton accès n'est pas activé.")
        return

    markup = types.InlineKeyboardMarkup()

    aviator = types.InlineKeyboardButton(
        "🚀 Ouvrir Aviator",
        url=AVIATOR_LINK
    )

    luckyjet = types.InlineKeyboardButton(
        "✈️ Ouvrir Lucky Jet",
        url=LUCKYJET_LINK
    )

    markup.add(aviator)
    markup.add(luckyjet)

    bot.send_message(
        message.chat.id,
        "🎮 Choisis un jeu",
        reply_markup=markup
    )


# NEXT SIGNAL
@bot.message_handler(func=lambda message: message.text == "⏳ Next Signal")
def next_signal(message):

    if message.chat.id not in active_users:
        bot.send_message(message.chat.id, "❌ Ton accès n'est pas activé.")
        return

    global last_signal_time

    now = time.time()

    if now - last_signal_time < INTERVAL:

        remaining = int((INTERVAL - (now - last_signal_time)) / 60) + 1

        bot.send_message(
            message.chat.id,
            f"⏳ Next signal in {remaining} minute(s)"
        )

        return

    last_signal_time = now

    multiplier = generate_signal()

    markup = types.InlineKeyboardMarkup()

    aviator = types.InlineKeyboardButton(
        "🚀 Aviator",
        url=AVIATOR_LINK
    )

    luckyjet = types.InlineKeyboardButton(
        "✈️ Lucky Jet",
        url=LUCKYJET_LINK
    )

    markup.add(aviator)
    markup.add(luckyjet)

    bot.send_message(
        message.chat.id,
        f"""
🚀 NEW SIGNAL

🎯 Cashout conseillé : {multiplier}x
⚠️ Mise recommandée : 5%

👑 CAPORAL PCS SIGNAL
""",
        reply_markup=markup
    )


# ODDS HISTORY
@bot.message_handler(func=lambda message: message.text == "📊 Odds History")
def odds(message):

    bot.send_message(
        message.chat.id,
        "📊 Historique bientôt disponible."
    )


# VIP
@bot.message_handler(func=lambda message: message.text == "💎 VIP Access")
def vip(message):

    bot.send_message(
        message.chat.id,
        "💎 Contacte l'admin pour accéder au VIP."
    )


bot.infinity_polling()