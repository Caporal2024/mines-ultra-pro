import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN manquant dans Railway Variables")

def menu():
    keyboard = [
        [InlineKeyboardButton("💣 Mines", callback_data="mines")],
        [InlineKeyboardButton("🚀 Crash", callback_data="crash")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟣 CASINO MINI PRO 🟣\n\nChoisis un jeu 👇",
        reply_markup=menu()
    )

async def handle_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    multiplier = round(random.uniform(1.0, 5.0), 2)

    if multiplier > 2:
        result = f"🎰 x{multiplier}\n\n💎 GAGNÉ !"
    else:
        result = f"🎰 x{multiplier}\n\n💥 PERDU !"

    await query.edit_message_text(result, reply_markup=menu())

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_game))

    print("BOT ACTIF")
    app.run_polling()

if __name__ == "__main__":
    main()