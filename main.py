from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "TON_TOKEN_ICI"

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

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎰 SUPER CASINO PRO MAX\n\nChoisissez votre jeu :",
        reply_markup=reply_markup
    )

app = 8765706088:AAHEQvqlxuQhl2WHgsJ3g0cd6UdXaNwiqt0