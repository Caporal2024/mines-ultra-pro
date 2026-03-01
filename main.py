import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Récupère le token depuis Railway
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot démarré 🚀")

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN non défini dans Railway")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Bot en cours de démarrage...")
    app.run_polling()

if __name__ == "__main__":
    main()