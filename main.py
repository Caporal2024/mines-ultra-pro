import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ==============================
# 🔐 METS TON TOKEN ICI
# ==============================
TOKEN = "MET_TON_TOKEN_ICI"

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ==============================
# 🎟 MENU PRINCIPAL
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎟 Coupon du jour", callback_data="coupon")],
        [InlineKeyboardButton("📊 Historique", callback_data="historique")],
        [InlineKeyboardButton("💎 VIP", callback_data="vip")],
        [InlineKeyboardButton("⚙️ Menu", callback_data="menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔥 BIENVENUE SUR TON BOT PREMIUM 🔥\n\nChoisis une option :",
        reply_markup=reply_markup
    )

# ==============================
# 🎟 COUPON
# ==============================
async def coupon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = """
━━━━━━━━━━━━━━
🎟 INFORMATIONS SUR LE PARI
━━━━━━━━━━━━━━

🏆 Ligue des Champions

⚽ Atlético Madrid vs Club Bruges
📊 Total tirs : +23.5

⚽ Bayer Leverkusen vs Olympiacos
📊 Total tirs : +24.5

⚽ Inter Milan vs Bodo/Glimt
📊 Total tirs : +29.5

━━━━━━━━━━━━━━
💰 Cote totale : 3.76
━━━━━━━━━━━━━━

⚠ Analyse basée sur statistiques
"""

    keyboard = [
        [InlineKeyboardButton("🔄 Nouveau coupon", callback_data="coupon")],
        [InlineKeyboardButton("🏠 Retour menu", callback_data="menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)

# ==============================
# 📊 HISTORIQUE
# ==============================
async def historique(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📊 Historique bientôt disponible.\n\n🏠 Clique sur /start pour revenir au menu."
    )

# ==============================
# 💎 VIP
# ==============================
async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "💎 Espace VIP\n\nContacte l'administrateur pour plus d'informations."
    )

# ==============================
# ⚙️ MENU
# ==============================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🎟 Coupon du jour", callback_data="coupon")],
        [InlineKeyboardButton("📊 Historique", callback_data="historique")],
        [InlineKeyboardButton("💎 VIP", callback_data="vip")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🏠 MENU PRINCIPAL\n\nChoisis une option :",
        reply_markup=reply_markup
    )

# ==============================
# 🚀 LANCEMENT BOT
# ==============================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(coupon, pattern="coupon"))
    app.add_handler(CallbackQueryHandler(historique, pattern="historique"))
    app.add_handler(CallbackQueryHandler(vip, pattern="vip"))
    app.add_handler(CallbackQueryHandler(menu, pattern="menu"))

    print("Bot en cours...")
    app.run_polling()