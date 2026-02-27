from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random

# 🔐 COLLE TON TOKEN ICI
TOKEN = "COLLE_TON_TOKEN_ICI"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✈️ Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("🛩 Aviator", callback_data="aviator")],
        [InlineKeyboardButton("💣 Mines", callback_data="mines")],
        [InlineKeyboardButton("⚽ Penalty", callback_data="penalty")],
        [InlineKeyboardButton("🪙 CoinFlip", callback_data="coinflip")],
        [InlineKeyboardButton("🍎 Apple of Fortune", callback_data="apple")],
        [InlineKeyboardButton("🎡 Roue de la Fortune", callback_data="wheel")]
    ]

    await update.message.reply_text(
        "🎰 SUPER CASINO PRO MAX\n\nChoisissez votre jeu :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "coinflip":
        result = random.choice(["🪙 FACE", "🪙 PILE"])
        await query.edit_message_text(f"Résultat CoinFlip : {result}")

    elif query.data == "lucky":
        crash = round(random.uniform(1.00, 10.00), 2)
        await query.edit_message_text(f"✈️ Lucky Jet Crash à : {crash}x")

    elif query.data == "aviator":
        crash = round(random.uniform(1.00, 20.00), 2)
        await query.edit_message_text(f"🛩 Aviator Crash à : {crash}x")

    elif query.data == "penalty":
        goal = random.choice(["⚽ GOAL !!!", "🧤 Arrêt du gardien"])
        await query.edit_message_text(goal)

    elif query.data == "apple":
        gain = random.choice(["🍎 Gagné 2x", "💣 Bombe ! Perdu"])
        await query.edit_message_text(gain)

    elif query.data == "wheel":
        prize = random.choice(["💰 100 FCFA", "💎 VIP", "❌ Rien", "🔥 500 FCFA"])
        await query.edit_message_text(f"🎡 Résat : {prize}")

    elif query.data == "mines":
        await query.edit_message_text("💣 Mode Mines bientôt disponible...")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("Bot démarré...")
app.run_polling()
