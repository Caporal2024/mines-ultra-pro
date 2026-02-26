import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

# Base de données simple en mémoire
users = {}

# Liste VIP (remplace par TON ID Telegram)
VIP_USERS = [8094967191]

# Menu principal
keyboard = [
    ["💣 Jouer", "💎 VIP"],
    ["💰 Mon Solde", "📊 Statistiques"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"solde": 0}

    await update.message.reply_text(
        "🔥 *MINES ULTRA PRO* 🔥\n\n"
        "🤖 IA intelligente activée\n"
        "💎 Version Premium disponible\n\n"
        "Choisissez une option 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in users:
        users[user_id] = {"solde": 0}

    if text == "💣 Jouer":
        users[user_id]["solde"] += 10
        await update.message.reply_text(
            f"💣 Mine détectée !\n\n"
            f"💰 Gain +10\n"
            f"Solde actuel : {users[user_id]['solde']} FCFA"
        )

    elif text == "💎 VIP":
        if user_id in VIP_USERS:
            await update.message.reply_text("💎 Accès VIP activé !")
        else:
            await update.message.reply_text("❌ Réservé aux membres VIP.")

    elif text == "💰 Mon Solde":
        solde = users[user_id]["solde"]
        await update.message.reply_text(f"💰 Ton solde : {solde} FCFA")

    elif text == "📊 Statistiques":
        await update.message.reply_text(
            "📊 Statistiques IA\n\n"
            "🎯 Taux réussite : 87%\n"
            "⚡ Mode agressif : ON\n"
            "🔮 Prédiction intelligente activée"
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot en cours d'exécution...")
    app.run_polling()