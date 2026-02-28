import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# On récupère le TOKEN depuis Railway Variables
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Le TOKEN n'est pas défini dans les variables Railway.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot actif !")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commandes disponibles :\n/start\n/help")

def main():
    print("Bot en cours de démarrage...")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    app.run_polling()

if __name__ == "__main__":
    main()