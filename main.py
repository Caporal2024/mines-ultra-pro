import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ==============================
# CONFIG
# ==============================

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Token via Railway
OWNER_ID = 8094967191

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

bankroll = 10000
profit_total = 0

# ==============================
# MENU PRINCIPAL
# ==============================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("💣 Mines 5x5 LIVE", callback_data="mines")],
        [InlineKeyboardButton("🚀 Lucky Jet LIVE", callback_data="lucky")],
        [InlineKeyboardButton("📊 Statistiques", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==============================
# START
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
💜 <b>MINES ULTRA PRO</b>

🎨 Interface Violet Néon Premium
🚀 Version LIVE Ultra Rapide
📊 Gestion Bankroll Active

Choisis un mode 👇
"""
    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )

# ==============================
# CALLBACK
# ==============================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bankroll, profit_total

    query = update.callback_query
    await query.answer()

    if query.data == "mines":
        grid = []
        for i in range(5):
            row = []
            for j in range(5):
                num = i * 5 + j + 1
                row.append(
                    InlineKeyboardButton(str(num), callback_data=f"cell_{num}")
                )
            grid.append(row)

        await query.edit_message_text(
            "💣 <b>MINES 5x5 LIVE</b>\n\nClique une case :",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(grid)
        )

    elif query.data.startswith("cell_"):
        number = query.data.split("_")[1]
        result = random.choice(["safe", "bomb"])

        if result == "safe":
            gain = random.randint(500, 1500)
            bankroll += gain
            profit_total += gain
            message = f"✅ Case {number} SAFE\n💰 +{gain}\n📊 Bankroll: {bankroll}"
        else:
            loss = random.randint(500, 1500)
            bankroll -= loss
            profit_total -= loss
            message = f"💣 BOOM Case {number}\n❌ -{loss}\n📊 Bankroll: {bankroll}"

        await query.edit_message_text(message)

    elif query.data == "lucky":
        multiplier = round(random.uniform(1.1, 5.0), 2)
        gain = int(1000 * multiplier)
        bankroll += gain
        profit_total += gain

        await query.edit_message_text(
            f"🚀 <b>Lucky Jet LIVE</b>\n\n🔥 x{multiplier}\n💰 +{gain}\n📊 Bankroll: {bankroll}",
            parse_mode="HTML"
        )

    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 <b>Statistiques</b>\n\n💰 Bankroll: {bankroll}\n📈 Profit Total: {profit_total}",
            parse_mode="HTML"
        )

# ==============================
# RUN
# ==============================

def main():
    if not BOT_TOKEN:
        print("ERREUR: BOT_TOKEN manquant dans Railway Variables")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Bot is running...")

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()