import telebot
from telebot import types
import os
import random
import time

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# 🔐 Codes autorisés
ACCESS_CODES = ["CAPORAL123"]

authorized_users = []
players = {}

# 📋 Menu principal
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
        bot.send_message(user_id,"✅ Bienvenue sur CAPORAL PCS AVIATOR",reply_markup=menu())
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

    msg = bot.send_message(message.chat.id,"🆔 Send Player ID")
    bot.register_next_step_handler(msg,save_player)

# 💾 Sauvegarde Player ID
def save_player(message):

    players[message.from_user.id] = message.text

    bot.send_message(message.chat.id,"✅ Player ID enregistré")

# 🚀 SIGNAL AVIATOR LIVE
@bot.message_handler(func=lambda m: m.text == "🚀 Start Signal")
def aviator_live(message):

    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id,"🔐 Accès refusé")
        return

    crash = round(random.uniform(2,10),2)

    msg = bot.send_message(message.chat.id,"🚀 AVIATOR LIVE\n\n1.00x")

    multiplier = 1.00

    while multiplier < crash:

        time.sleep(1)

        multiplier += round(random.uniform(0.20,0.80),2)

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

💰 Cashout conseillé avant crash
CAPORAL PCS SIGNAL
""",
        message.chat.id,
        msg.message_id
    )

bot.infinity_polling()