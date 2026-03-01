import os
import random
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ==============================
# CONFIG
# ==============================

OWNER_ID = 8094967191  # Ton ID Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Railway Variable

logging.basicConfig(level=logging.INFO)

# ==============================
# VARIABLES LIVE
# ==============================

bankroll = 10000
current_profit = 0

# ==============================
# DESIGN
# ==============================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("💣 Mines 5x5 LIVE", callback_data="mines")],
        [InlineKeyboardButton("🚀 Lucky Jet LIVE", callback_data="lucky")],
        [InlineKeyboardButton("📊 Bankroll Graph", callback_data="graph")],
        [InlineKeyboardButton("👑 Admin", callback_data="admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==============================
# START
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
💜 <b>MINES ULTRA PRO - LIVE</b>

🎨 Interface Violet Néon Premium
🚀 Version Ultra Rapide
📊 Gestion Intelligente Activée

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
    global bankroll, current_profit

    query = update.callback_query
    await query.answer()

    if query.data == "mines":

        grid = []
        for i in range(5):
            row = []
            for j in range(5):
                number = i * 5 + j + 1
                row.append(
                    InlineKeyboardButton(
                        f"{number}",
                        callback_data=f"cell_{number}"
                    )
                )
            grid.append(row)

        await query.edit_message_text(
            "💣 <b>MINES 5x5 LIVE</b>\n\nClique une case 👇",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(grid)
        )

    elif query.data.startswith("cell_"):

        number = query.data.split("_")[1]
        result = random.choice(["safe", "bomb"])

        if result == "safe":
            gain = random.randint(500, 1500)
            bankroll += gain
            current_profit += gain
            text = f"✅ Case {number} SAFE\n\n💰 +{gain}\n📊 Bankroll: {bankroll}"
        else:
            loss = random.randint(500, 1500)
            bankroll -= loss
            current_profit -= loss
            text = f"💣 BOOM Case {number}\n\n❌ -{loss}\n📊 Bankroll: {bankroll}"

        await query.edit_message_text(text, parse_mode="HTML")

    elif query.data == "lucky":

        multiplier = round(random.uniform(1.1, 5.0), 2)
        gain = int(1000 * multiplier)

        bankroll += gain
        current_profit += gain

        text = f"""
🚀 <b>LUCKY JET LIVE</b>

🔥 Multiplier : x{multiplier}
💰 Gain : {gain}
📊 Bankroll : {bankroll}
"""
        await query.edit_message_text(text, parse_mode="HTML")

    elif query.data == "graph":

        text = f"""
📊 <b>STATISTIQUES LIVE</b>

💰 Bankroll actuelle : {bankroll}
📈 Profit total : {current_profit}

🔮 Mode Intelligence Active
"""
        await query.edit_message_text(text, parse_mode="HTML")

    elif query.data == "admin":

        if query.from_user.id == OWNER_ID:
            await query.edit_message_text(
                "👑 ADMIN PANEL\n\nAccès autorisé.",
                parse_mode="HTML"
            )
        else:
            await query.edit_message_text(
                "⛔ Accès refusé.",
                parse_mode="HTML"
            )

# ==============================
# RUN
# ==============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    app.run_polling()

if __name__ == "__main__":
    main()