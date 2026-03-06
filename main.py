import telebot

TOKEN = "TON_TOKEN_ICI"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Bot Aviator actif !")

print("Bot démarré...")
bot.infinity_polling()