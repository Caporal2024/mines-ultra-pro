import os
import telebot

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 Bot démarré avec succès !")

print("Bot en cours de démarrage...")
bot.infinity_polling()