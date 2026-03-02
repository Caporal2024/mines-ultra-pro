import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", 8000))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Railway fonctionne !")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Bot démarré...")

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=f"https://{os.environ.get('RAILWAY_STATIC_URL')}"
)