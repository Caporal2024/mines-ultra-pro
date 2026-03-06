import os
import telebot
import random

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# code secret pour accéder au bot
CODE_SECRET = "CAPORAL123"

# stockage simple des utilisateurs connectés
users = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
    "🔐 Bienvenue sur le Bot Aviator\n\n"
    "Tape d'abord :\n"
    "code CAPORAL123")

@bot.message_handler(func=lambda m: True)
def messages(message):

    user = message.chat.id
    text = message.text.lower()

    # vérification du code
    if text.startswith("code"):
        code = message.text.split(" ")[1]

        if code == CODE_SECRET:
            bot.send_message(user,
            "🔑 Accès autorisé\n\n"
            "Envoie ton Player ID pour te connecter.")
            users[user] = "login"
        else:
            bot.send_message(user,"❌ Code incorrect")

    # connexion player id
    elif user in users and users[user] == "login":

        player_id = message.text
        users[user] = player_id

        bot.send_message(user,
        f"✅ Connecté\n\n"
        f"Player ID : {player_id}\n\n"
        f"⚡ Tape SIGNAL pour recevoir une prédiction.")

    # envoyer signal aviator
    elif text == "signal" and user in users:

        entree = round(random.uniform(1.20,1.80),2)
        cashout = round(random.uniform(2.00,3.50),2)

        bot.send_message(user,
        f"""
🎯 SIGNAL AVIATOR

🎯 Entrée : {entree}x
💰 Cashout : {cashout}x

⏱ Attendre 2 tours
🔥 Mise conseillée : 200f

⚡ Parier maintenant
""")

    else:
        bot.send_message(user,"❗ Tu dois d'abord entrer le code.")

print("Bot lancé...")
bot.infinity_polling()