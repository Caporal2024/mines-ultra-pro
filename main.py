import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

capital = 10000

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💣 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("🚀 Lucky Jet Live", callback_data="crash")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎮 MENU PRINCIPAL\nChoisis un jeu :",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global capital
    query = update.callback_query
    await query.answer()

    if query.data == "mines":
        grid = ""
        bombs = random.sample(range(1, 26), 5)
        for i in range(1, 26):
            if i in bombs:
                grid += "💣 "
            else:
                grid += "💎 "
            if i % 5 == 0:
                grid += "\n"
        await query.edit_message_text(f"💣 MINES 5x5 PRO\n\n{grid}\nCapital: {capital} FCFA")

    if query.data == "crash":
        multiplier = round(random.uniform(1.00, 3.00), 2)
        if multiplier < 1.30:
            capital -= 500
            result = f"💥 CRASH à {multiplier}x\n❌ -500 FCFA"
        else:
            gain = 500
            capital += gain
            result = f"🚀 Cashout {multiplier}x\n✅ +{gain} FCFA"

        await query.edit_message_text(f"{result}\n\n💰 Capital: {capital} FCFA")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()