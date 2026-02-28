import os
import threading
from flask import Flask, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# CONFIG (TOKEN via Railway Variables)
# =========================

TOKEN = os.getenv("TOKEN")  # Railway prendra le token depuis Variables
PORT = int(os.getenv("PORT", 8080))

if not TOKEN:
    raise ValueError("TOKEN environment variable not found")

# =========================
# WEB SERVER
# =========================

app_web = Flask(__name__)

@app_web.route("/")
def index():
    return Response("""
    <h1 style='text-align:center;font-family:Arial;'>👑 Empire Ultra Running</h1>
    """, mimetype="text/html")

def run_web():
    app_web.run(host="0.0.0.0", port=PORT)

# =========================
# TELEGRAM BOT
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 Bot Actif", callback_data="ok")]
    ]

    await update.message.reply_text(
        "👑 Empire Ultra est en ligne !",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    threading.Thread(target=run_web).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()