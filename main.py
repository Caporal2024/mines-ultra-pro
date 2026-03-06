import telebot
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 Bot Aviator démarré avec succès!")

print("Bot lancé...")

bot.infinity_polling()