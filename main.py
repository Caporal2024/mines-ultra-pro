import telebot

# METS TON TOKEN TELEGRAM ICI
TOKEN = "TON_TOKEN_ICI"

bot = telebot.TeleBot(TOKEN)

# Nouveau code secret (il ne sera pas affiché)
SECRET_CODE = "PCS9087"

# Liste des utilisateurs autorisés
users_autorises = []

# Commande start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔐 Bienvenue sur le Bot Aviator\n\n"
        "Veuillez entrer votre code d'accès pour continuer."
    )

# Vérification du code
@bot.message_handler(func=lambda message: True)
def verifier(message):

    if message.chat.id in users_autorises:
        bot.send_message(
            message.chat.id,
            "✈️ Bot Aviator actif\n\n"
            "📊 Prédiction Aviator : 2.35x"
        )
        return

    if message.text == SECRET_CODE:

        users_autorises.append(message.chat.id)

        bot.send_message(
            message.chat.id,
            "✅ Accès autorisé\n\n"
            "🚀 Bot Aviator activé.\n"
            "Les prédictions vont commencer."
        )

    else:
        bot.send_message(
            message.chat.id,
            "❌ Code incorrect.\n"
            "Réessayez."
        )

bot.infinity_polling()