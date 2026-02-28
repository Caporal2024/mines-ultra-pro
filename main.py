import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Récupération du token depuis Railway (Variables)
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN non défini dans les variables Railway.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot actif et fonctionnel !")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commande disponible :\n/start - Démarrer le bot")

def main():
    print("Bot démarré...")
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()

if __name__ == "__main__":
    main()