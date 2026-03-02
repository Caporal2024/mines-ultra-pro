import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Récupération du token depuis Railway
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN non trouvé dans les variables Railway")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot démarré avec succès !\n\n"
        "Bienvenue sur ton bot Mines 5x5 Pro 🔥"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot en cours de démarrage...")
    app.run_polling()

if __name__ == "__main__":
    main()