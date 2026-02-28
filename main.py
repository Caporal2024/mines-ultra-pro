import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# On récupère le token depuis Railway
TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Mines Ultra Pro est en ligne !")

def main():
    if not TOKEN:
        print("ERREUR : TOKEN non trouvé.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()