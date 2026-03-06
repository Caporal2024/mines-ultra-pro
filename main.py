import telebot

TOKEN = "MET_TON_TOKEN_ICI"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 Bot Aviator démarré avec succès !")

print("Bot en ligne...")
bot.infinity_polling()