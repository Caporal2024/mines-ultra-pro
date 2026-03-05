import telebot
from telebot import types
import random
import time
import os

# 🔑 Token Railway
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# ⏱ Intervalle entre signaux (4 minutes)
INTERVAL = 240
last_signal_time = 0

# 🔗 Tes liens
AVIATOR_LINK = "https://tonsite.com/aviator"
LUCKYJET_LINK = "https://tonsite.com/luckyjet"
CHANNEL_LINK = "https://t.me/toncanal"

# 📊 Historique
history = []

def generate_signal():
    return round(random.uniform(1.70, 2.30), 2)

# 🚀 Commande START
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.InlineKeyboardMarkup(row_width=1)

    aviator_btn = types.InlineKeyboardButton(
        "🎮 Ouvrir Aviator",
        url=AVIATOR_LINK
    )

    luckyjet_btn = types.InlineKeyboardButton(
        "🎮 Ouvrir Lucky Jet",
        url=LUCKYJET_LINK
    )

    channel_btn = types.InlineKeyboardButton(
        "📢 Rejoindre le canal",
        url=CHANNEL_LINK
    )

    markup.add(aviator_btn)
    markup.add(luckyjet_btn)
    markup.add(channel_btn)

    bot.send_message(
        message.chat.id,
        """
👑 *CAPORAL PCS SIGNAL*

Bot de signaux Aviator ⚡

Commandes disponibles :

/signal → Recevoir un signal  
/stats → Voir les statistiques
""",
        parse_mode="Markdown",
        reply_markup=markup
    )

# 📊 Commande STATS
@bot.message_handler(commands=['stats'])
def stats(message):

    if not history:
        bot.send_message(message.chat.id, "Aucune statistique pour le moment.")
        return

    text = "📊 Derniers multiplicateurs :\n\n"

    for m in history[-10:]:
        text += f"• {m}x\n"

    bot.send_message(message.chat.id, text)

# 🚀 Commande SIGNAL
@bot.message_handler(commands=['signal'])
def send_signal(message):

    global last_signal_time

    now = time.time()

    if now - last_signal_time < INTERVAL:

        remaining = int((INTERVAL - (now - last_signal_time)) / 60) + 1

        bot.send_message(
            message.chat.id,
            f"⏳ Prochain signal dans {remaining} minute(s)"
        )
        return

    last_signal_time = now
    multiplier = generate_signal()

    history.append(multiplier)

    # 🚀 NEW ROUND
    bot.send_message(message.chat.id, "🚀 *NEW ROUND* 🚀", parse_mode="Markdown")

    time.sleep(2)

    markup = types.InlineKeyboardMarkup(row_width=1)

    logo_btn = types.InlineKeyboardButton(
        "👑 CAPORAL PCS SIGNAL",
        url=CHANNEL_LINK
    )

    aviator_btn = types.InlineKeyboardButton(
        "🎮 Ouvrir Aviator",
        url=AVIATOR_LINK
    )

    luckyjet_btn = types.InlineKeyboardButton(
        "🎮 Ouvrir Lucky Jet",
        url=LUCKYJET_LINK
    )

    markup.add(logo_btn)
    markup.add(aviator_btn)
    markup.add(luckyjet_btn)

    bot.send_message(
        message.chat.id,
        f"""
🟢 *SIGNAL LIVE*

🎯 Cashout conseillé : *{multiplier}x*  
⚠️ Mise recommandée : *5% bankroll*

📊 Utilise /stats pour voir l'historique

💼 CAPORAL PCS SIGNAL
""",
        parse_mode="Markdown",
        reply_markup=markup
    )

# 🔄 Lancer le bot
bot.infinity_polling()