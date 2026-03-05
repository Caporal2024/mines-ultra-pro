import os
import telebot
from telebot import types
import random

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

ACCESS_CODE = "PCS2026"
CHANNEL = "@caporal_signal_vip"

authorized_users = {}
player_ids = {}

# vérifier si utilisateur est dans le canal
def check_subscription(user_id):

    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# START
@bot.message_handler(commands=['start'])
def start(message):

    if not check_subscription(message.from_user.id):

        markup = types.InlineKeyboardMarkup()
        join = types.InlineKeyboardButton(
            "📢 Rejoindre le canal",
            url="https://t.me/caporal_signal_vip"
        )
        markup.add(join)

        bot.send_message(
            message.chat.id,
            "⚠️ Tu dois rejoindre le canal pour utiliser le bot.",
            reply_markup=markup
        )
        return

    msg = bot.send_message(
        message.chat.id,
        "🔐 Entre le code d'accès :"
    )

    bot.register_next_step_handler(msg, check_code)

# vérifier code
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

        bot.send_message(message.chat.id,"❌ Code incorrect.")

# LOGIN
@bot.message_handler(func=lambda m: m.text == "🔑 Login")
def login(message):

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
            "⚠️ Connecte ton Player ID d'abord."
        )
        return

    crash = round(random.uniform(1.20,5.00),2)

    bot.send_message(
        message.chat.id,
        f"🚀 SIGNAL\n\nMultiplier : {crash}x\n\nCashout avant {crash}x"
    )

# HISTORY
@bot.message_handler(func=lambda m: m.text == "📊 Odds History")
def history(message):

    odds = []

    for i in range(5):
        odds.append(str(round(random.uniform(1.10,5.00),2))+"x")

    bot.send_message(
        message.chat.id,
        "📊 Historique\n\n"+"\n".join(odds)
    )

print("Bot lancé...")
bot.infinity_polling()