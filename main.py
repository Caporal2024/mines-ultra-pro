import os
import threading
from flask import Flask, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")

if not TOKEN:
    raise ValueError("BOT_TOKEN non trouvé.")

if not WEBAPP_URL:
    raise ValueError("WEBAPP_URL non trouvé.")

# ===== Flask (serveur Web App) =====
web = Flask(__name__)

@web.route("/")
def serve():
    return send_from_directory("webapp", "index.html")


def run_web():
    port = int(os.environ.get("PORT", 8080))
    web.run(host="0.0.0.0", port=port)


# ===== Bot Telegram =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "🎮 Ouvrir Apple of Fortune",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ]

    await update.message.reply_text(
        "🎰 Casino Premium\n\nClique pour jouer :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()