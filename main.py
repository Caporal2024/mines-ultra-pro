import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "MET_TON_TOKEN_ICI"

# =========================
# MESSAGE DE DEMARRAGE
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 Bot Actif", callback_data="active")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👑 Empire Ultra est en ligne !",
        reply_markup=reply_markup
    )

# =========================
# MINES
# =========================
async def mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Exemple: /mines 100")
        return

    try:
        mise = float(context.args[0])
    except:
        await update.message.reply_text("❌ Montant invalide.")
        return

    multiplicateur = round(random.uniform(1.20, 3.50), 2)
    gain = round(mise * multiplicateur, 2)

    message = f"""
💣 MINES PREDICTION

💵 Mise : {mise}
📈 Multiplicateur conseillé : x{multiplicateur}
💰 Gain estimé : {gain}

🔥 Mode Premium Activé
"""

    await update.message.reply_text(message)

# =========================
# LUCKYJET
# =========================
async def luckyjet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Exemple: /luckyjet 200")
        return

    try:
        mise = float(context.args[0])
    except:
        await update.message.reply_text("❌ Montant invalide.")
        return

    multiplicateur = round(random.uniform(1.50, 5.00), 2)
    gain = round(mise * multiplicateur, 2)

    message = f"""
🚀 LUCKYJET PREDICTION

💵 Mise : {mise}
📈 Auto Cashout conseillé : x{multiplicateur}
💰 Gain estimé : {gain}

🎰 Empire Ultra Premium
"""

    await update.message.reply_text(message)

# =========================
# LANCEMENT BOT
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mines", mines))
app.add_handler(CommandHandler("luckyjet", luckyjet))

print("🔥 Empire Ultra Bot Actif...")
app.run_polling()