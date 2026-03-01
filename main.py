import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🔑 Récupération du token Railway
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

bankroll = 10000
profit_total = 0


def main_menu():
    keyboard = [
        [InlineKeyboardButton("💣 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("📊 Statistiques", callback_data="stats")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💜 MINES PRO 20.7\n\nChoisis un jeu 👇",
        reply_markup=main_menu(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            "💣 Clique une case :",
            reply_markup=InlineKeyboardMarkup(grid),
        )

    elif query.data.startswith("cell_"):
        number = query.data.split("_")[1]
        result = random.choice(["safe", "bomb"])

        if result == "safe":
            gain = random.randint(500, 1500)
            bankroll += gain
            profit_total += gain
            text = f"✅ Case {number}\n+{gain}\nBankroll: {bankroll}"
        else:
            loss = random.randint(500, 1500)
            bankroll -= loss
            profit_total -= loss
            text = f"💣 BOOM {number}\n-{loss}\nBankroll: {bankroll}"

        await query.edit_message_text(text)

    elif query.data == "lucky":
        multiplier = round(random.uniform(1.2, 5.0), 2)
        gain = int(1000 * multiplier)
        bankroll += gain
        profit_total += gain

        await query.edit_message_text(
            f"🚀 Lucky Jet\nMultiplicateur x{multiplier}\n+{gain}\nBankroll: {bankroll}"
        )

    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 Statistiques\n\nBankroll: {bankroll}\nProfit total: {profit_total}"
        )


def main():
    if not TOKEN:
        print("❌ BOT_TOKEN manquant")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot lancé avec succès")
    app.run_polling()


if __name__ == "__main__":
    main()