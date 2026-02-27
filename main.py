from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "TON_TOKEN_ICI"

# ========= COMMANDE /start =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✈️ Aviator", callback_data="aviator")],
        [InlineKeyboardButton("💣 Mines", callback_data="mines")],
        [InlineKeyboardButton("⚽ Penalty", callback_data="penalty")],
        [InlineKeyboardButton("🍎 Apple", callback_data="apple")],
        [InlineKeyboardButton("🎡 Wheel", callback_data="wheel")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎮 Bienvenue sur le BOT PRO MAX\n\nChoisissez un jeu :",
        reply_markup=reply_markup
    )

# ========= GESTION DES BOUTONS =========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "aviator":
        await query.edit_message_text("✈️ Signal Aviator en préparation...")

    elif query.data == "mines":
        await query.edit_message_text("💣 Mines 5x5 PRO activé...")

    elif query.data == "penalty":
        await query.edit_message_text("⚽ Penalty Predictor en cours...")

    elif query.data == "apple":
        await query.edit_message_text("🍎 Apple Fortune lancé...")

    elif query.data == "wheel":
        await query.edit_message_text("🎡 Wheel Spin en cours...")

# ========= LANCEMENT =========
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot en marche...")
app.run_polling()