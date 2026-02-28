import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")  # Railway va lire le token ici

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 LUCK JEJ Casino Actif !")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Stats bientôt disponibles.")

async def luckyjet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Utilisation : /luckyjet 200")
        return
    
    mise = context.args[0]
    await update.message.reply_text(f"🚀 LuckyJet lancé avec {mise} FCFA")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("luckyjet", luckyjet))

print("🔥 LUCK JEJ démarré...")
app.run_polling()