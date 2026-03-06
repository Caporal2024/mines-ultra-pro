import telebot

# Ajoute ton TOKEN Telegram ici
TOKEN = ""

bot = telebot.TeleBot(TOKEN)

# Code secret (il ne sera jamais affiché dans le bot)
SECRET_CODE = "PCS9087"

# Liste des utilisateurs autorisés
users_autorises = []

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔐 Bienvenue sur le Bot Aviator\n\n"
        "Veuillez entrer votre code d'accès pour continuer."
    )

@bot.message_handler(func=lambda message: True)
def verifier(message):

    # Si l'utilisateur est déjà autorisé
    if message.chat.id in users_autorises:
        bot.send_message(
            message.chat.id,
            "✈️ Bot Aviator activé.\n\n"
            "📊 Prédiction Aviator : 2.10x"
        )
        return

    # Vérifie le code
    if message.text == SECRET_CODE:

        users_autorises.append(message.chat.id)

        bot.send_message(
            message.chat.id,
            "✅ Accès autorisé.\n"
            "Bienvenue dans le bot Aviator."
        )

    else:
        bot.send_message(
            message.chat.id,
            "❌ Code incorrect. Réessayez."
        )

bot.infinity_polling()