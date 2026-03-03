import os
import telebot
from flask import Flask
import threading

# Récupère le TOKEN depuis Railway Variables
TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise Exception("TOKEN manquant dans Railway Variables")

bot = telebot.TeleBot(TOKEN)

# Commande /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 Bot actif et fonctionnel !")

# Lance le bot dans un thread
def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot).start()

# Petit serveur Flask obligatoire pour Railway
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)