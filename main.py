import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN non trouvé dans les variables Railway")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 MINES 5x5 PRO MAX actif !\n\n"
        "Commandes disponibles :\n"
        "/start - Démarrer\n"
        "/stats - Voir tes statistiques"
    )

# Commande /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Statistiques :\n"
        "💰 Solde: 0 FCFA\n"
        "🎮 Parties jouées: 0\n"
        "🏆 Gains: 0 FCFA"
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))

print("🚀 Bot démarré sur Railway...")
app.run_polling()