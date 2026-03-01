import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🔐 On récupère le token depuis Railway (variable d'environnement)
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN non trouvé. Ajoute-le dans Railway > Variables.")

users = {}
games = {}

BET_AMOUNT = 1000


def get_user(user_id):
    if user_id not in users:
        users[user_id] = {"balance": 10000}
    return users[user_id]


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    keyboard = [
        [InlineKeyboardButton("🍎 Jouer Apple", callback_data="play_apple")],
        [InlineKeyboardButton("💰 Voir solde", callback_data="balance")]
    ]

    await update.message.reply_text(
        f"🎰 Casino Premium\n\n💰 Solde : {user['balance']} FCFA",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ===== HANDLE BUTTONS =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)

    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Ton solde : {user['balance']} FCFA"
        )

    elif query.data == "play_apple":

        if user["balance"] < BET_AMOUNT:
            await query.edit_message_text("❌ Solde insuffisant.")
            return

        user["balance"] -= BET_AMOUNT
        bomb_position = random.randint(0, 24)

        games[user_id] = {
            "bomb": bomb_position,
            "multiplier": 1.0,
            "revealed": []
        }

        await show_grid(query, user_id)


    elif query.data.startswith("cell_"):

        index = int(query.data.split("_")[1])
        game = games.get(user_id)

        if not game:
            return

        if index in game["revealed"]:
            return

        if index == game["bomb"]:
            del games[user_id]
            await query.edit_message_text("💣 BOOM ! Tu as perdu.")
            return

        game["revealed"].append(index)
        game["multiplier"] += 0.3

        await show_grid(query, user_id)


    elif query.data == "cashout":

        game = games.get(user_id)
        if not game:
            return

        win = int(BET_AMOUNT * game["multiplier"])
        user["balance"] += win

        del games[user_id]

        await query.edit_message_text(
            f"💰 Encaissement réussi !\n\nGain : {win} FCFA\n\nNouveau solde : {user['balance']} FCFA"
        )


async def show_grid(query, user_id):
    game = games[user_id]

    keyboard = []
    for i in range(5):
        row = []
        for j in range(5):
            index = i * 5 + j

            if index in game["revealed"]:
                text = "🍎"
            else:
                text = "❓"

            row.append(InlineKeyboardButton(text, callback_data=f"cell_{index}"))
        keyboard.append(row)

    keyboard.append(
        [InlineKeyboardButton("💰 Encaisser", callback_data="cashout")]
    )

    await query.edit_message_text(
        f"🍎 Apple of Fortune\n\nMultiplicateur : x{round(game['multiplier'],2)}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot lancé...")
    app.run_polling()


if __name__ == "__main__":
    main()