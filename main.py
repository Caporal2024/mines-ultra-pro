import telebot
from telebot import types
import os
import random
import time
from datetime import datetime, timedelta

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# 🔐 Code d'accès
ACCESS_CODES = ["CAPORAL123"]

authorized_users = []
players = {}

# 📋 Menu
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🔑 Login")
    btn2 = types.KeyboardButton("🚀 Start Signal")

    markup.add(btn1)
    markup.add(btn2)

    return markup


# ▶️ START
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    if user_id in authorized_users:
        bot.send_message(user_id,"✅ Bienvenue CAPORAL PCS AVIATOR",reply_markup=menu())
    else:
        msg = bot.send_message(user_id,"🔐 Entrez votre code d'accès :")
        bot.register_next_step_handler(msg,check_code)


# 🔐 Vérification code
def check_code(message):

    user_id = message.from_user.id
    code = message.text

    if code in ACCESS_CODES:

        authorized_users.append(user_id)

        bot.send_message(user_id,"✅ Accès autorisé",reply_markup=menu())

    else:

        bot.send_message(user_id,"❌ Code incorrect")


# 🔑 LOGIN
@bot.message_handler(func=lambda m: m.text == "🔑 Login")
def login(message):

    msg = bot.send_message(message.chat.id,"Send Player ID")
    bot.register_next_step_handler(msg,save_player)


# 💾 Sauvegarde Player ID
def save_player(message):

    players[message.from_user.id] = message.text

    bot.send_message(message.chat.id,"✅ Player ID enregistré")


# 🚀 SIGNAL AVIATOR AVEC HEURE
@bot.message_handler(func=lambda m: m.text == "🚀 Start Signal")
def aviator_live(message):

    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id,"🔐 Accès refusé")
        return

    # 📉 Cotes réduites
    crash = round(random.uniform(1.40,3.50),2)

    # 🕒 heure du signal
    signal_time = datetime.now() + timedelta(seconds=10)
    heure = signal_time.strftime("%H:%M:%S")

    bot.send_message(message.chat.id,
f"""
🚀 SIGNAL AVIATOR

🕒 Heure : {heure}
🎯 Entrée : 1.20x
💰 Cashout conseillé : {crash}x

Préparez votre mise...
""")

    time.sleep(10)

    msg = bot.send_message(message.chat.id,"🚀 AVIATOR LIVE\n\n1.00x")

    multiplier = 1.00

    while multiplier < crash:

        time.sleep(0.4)

        multiplier += round(random.uniform(0.10,0.35),2)

        try:
            bot.edit_message_text(
                f"🚀 AVIATOR LIVE\n\n{round(multiplier,2)}x",
                message.chat.id,
                msg.message_id
            )
        except:
            pass

    bot.edit_message_text(
        f"""
💥 CRASH

Final : {crash}x

CAPORAL PCS SIGNAL
""",
        message.chat.id,
        msg.message_id
    )


bot.infinity_polling()