import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN manquant dans Railway Variables")

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = 10000
    return users[user_id]

def menu():
    keyboard = [
        [InlineKeyboardButton("💣 Mines", callback_data="mines")],
        [InlineKeyboardButton("🚀 Crash", callback_data="crash")],
        [InlineKeyboardButton("✈️ Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("💰 Mon Solde", callback_data="balance")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance = get_user(update.effective_user.id)

    await update.message.reply_text(
        f"🟣 CASINO PRO MAX 🟣\n\n💰 Solde: {balance} FCFA\n\nChoisis ton jeu 👇",
        reply_markup=menu()
    )

async def handle_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    balance = get_user(user_id)

    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Ton solde actuel est : {balance} FCFA",
            reply_markup=menu()
        )
        return

    bet = 1000

    if balance < bet:
        await query.edit_message_text("❌ Solde insuffisant", reply_markup=menu())
        return

    # ================= MINES =================
    if query.data == "mines":
        multiplier = round(random.uniform(1.2, 2.5), 2)

        if multiplier > 1.8:
            gain = int(bet * multiplier)
            users[user_id] += gain
            result = f"💣 MINES\n🎯 Multiplicateur: x{multiplier}\n💎 GAGNÉ {gain} FCFA"
        else:
            users[user_id] -= bet
            result = f"💣 MINES\n🎯 Multiplicateur: x{multiplier}\n💥 PERDU {bet} FCFA"

    # ================= CRASH =================
    elif query.data == "crash":
        multiplier = round(random.uniform(1.0, 10.0), 2)

        if multiplier > 3:
            gain = int(bet * multiplier)
            users[user_id] += gain
            result = f"🚀 CRASH\n🔥 Explosion à x{multiplier}\n💎 GAGNÉ {gain} FCFA"
        else:
            users[user_id] -= bet
            result = f"🚀 CRASH\n💥 Crash à x{multiplier}\n❌ PERDU {bet} FCFA"

    # ================= LUCKY JET =================
    elif query.data == "lucky":
        multiplier = round(random.uniform(1.0, 6.0), 2)

        if multiplier > 2.2:
            gain = int(bet * multiplier)
            users[user_id] += gain
            result = f"✈️ LUCKY JET\n🌤️ Vol à x{multiplier}\n💎 GAGNÉ {gain} FCFA"
        else:
            users[user_id] -= bet
            result = f"✈️ LUCKY JET\n🌪️ Crash à x{multiplier}\n❌ PERDU {bet} FCFA"

    await query.edit_message_text(result, reply_markup=menu())

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_game))

    print("BOT ACTIF PRO MAX")
    app.run_polling()

if __name__ == "__main__":
    main()