import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔐 Token récupéré depuis Railway (NE PAS METTRE LE TOKEN ICI)
TOKEN = os.getenv("BOT_TOKEN")

users = {}
game_active = False
current_multiplier = 1.00
crash_point = 2.00

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {
            "balance": 1000,
            "bet": 100,
            "in_game": False,
            "profit": 0
        }

    keyboard = [
        [InlineKeyboardButton("🚀 Jouer (100)", callback_data="play")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ]

    await update.message.reply_text(
        f"🔥 CRASH ULTRA PRO\n\n💰 Solde: {users[user_id]['balance']} FCFA",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- GAME ENGINE ----------
async def crash_engine():
    global game_active, current_multiplier, crash_point

    while True:
        game_active = True
        current_multiplier = 1.00
        crash_point = round(random.uniform(1.5, 5.0), 2)

        while current_multiplier < crash_point:
            await asyncio.sleep(1)
            current_multiplier += 0.10

        game_active = False
        await asyncio.sleep(60)

# ---------- BUTTON ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global game_active, current_multiplier, crash_point

    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "play":
        if not game_active:
            await query.edit_message_text("⏳ Attends le prochain round...")
            return

        if users[user_id]["balance"] < 100:
            await query.edit_message_text("❌ Solde insuffisant")
            return

        users[user_id]["balance"] -= 100
        users[user_id]["in_game"] = True

        keyboard = [
            [InlineKeyboardButton("💰 CASHOUT", callback_data="cashout")]
        ]

        await query.edit_message_text(
            f"🚀 En jeu...\n📈 Multiplicateur: {current_multiplier:.2f}x",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "cashout":
        if not users[user_id]["in_game"]:
            return

        if current_multiplier >= crash_point:
            users[user_id]["in_game"] = False
            await query.edit_message_text("💥 Trop tard ! Crash.")
            return

        gain = int(100 * current_multiplier)
        users[user_id]["balance"] += gain
        users[user_id]["profit"] += gain - 100
        users[user_id]["in_game"] = False

        await query.edit_message_text(
            f"💰 Cashout à {current_multiplier:.2f}x\n"
            f"Gain: {gain} FCFA\n"
            f"Solde: {users[user_id]['balance']} FCFA"
        )

    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 STATS\n"
            f"Profit: {users[user_id]['profit']} FCFA\n"
            f"Solde: {users[user_id]['balance']} FCFA"
        )

# ---------- MAIN ----------
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    asyncio.create_task(crash_engine())

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())