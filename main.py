import telebot
import random
import time
import threading

TOKEN = "METS_TON_TOKEN_ICI"

bot = telebot.TeleBot(TOKEN)

# Code secret (non affiché dans le bot)
SECRET_CODE = "CAPORALPCS"

users_unlocked = set()


@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "🔐 Bienvenue sur le Bot Aviator\n\n"
        "Entre ton code d'accès pour activer les signaux."
    )


@bot.message_handler(func=lambda message: True)
def check_access(message):

    user_id = message.from_user.id
    text = message.text.strip()

    # Si l'utilisateur n'a pas encore accès
    if user_id not in users_unlocked:

        if text == SECRET_CODE:

            users_unlocked.add(user_id)

            bot.send_message(
                message.chat.id,
                "✅ Accès activé\n\n"
                "Les signaux Aviator arrivent..."
            )

            threading.Thread(target=signals, args=(message.chat.id,)).start()

        else:

            bot.send_message(
                message.chat.id,
                "❌ Code incorrect.\nRéessaie."
            )

    else:

        bot.send_message(
            message.chat.id,
            "⚡ Les signaux sont déjà actifs."
        )


def signals(chat_id):

    while True:

        entree = round(random.uniform(1.20, 1.60), 2)
        cashout = round(random.uniform(2.00, 5.00), 2)
        attente = random.randint(5, 20)

        msg = f"""
🎯 Entrée : {entree}x
💰 Cashout : {cashout}x

⏱ Attendre {attente} secondes

⚡ Parier maintenant
"""

        bot.send_message(chat_id, msg)

        time.sleep(60)


print("Bot démarré...")

bot.infinity_polling()