from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random

TOKEN = "TON_TOKEN_ICI"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🪙 CoinFlip", callback_data="coinflip")],
        [InlineKeyboardButton("✈️ Lucky Jet", callback_data="lucky")]
    ]

    await update.message.reply_text(
        "🎰 TEST BOUTONS\n\nClique sur un bouton :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "coinflip":
        result = random.choice(["FACE", "PILE"])
        await query.edit_message_text(f"Résultat : {result}")

    elif query.data == "lucky":
        crash = round(random.uniform(1.00, 5.00), 2)
        await query.edit_message_text(f"Lucky crash à {crash}x")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("✅ Bot démarré correctement...")
app.run_polling()
