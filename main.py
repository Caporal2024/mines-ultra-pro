import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
app = Application.builder().token(TOKEN).build()

users = {}
games = {}

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("💰 Mon Solde", callback_data="balance")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"balance": 10000, "wins": 0, "losses": 0}

    text = f"""
🎰 ULTRA PRO MAX BOT 🎰

💰 Solde : {users[user_id]['balance']} FCFA
📊 Victoires : {users[user_id]['wins']}
📉 Défaites : {users[user_id]['losses']}

Choisissez un jeu 👇
"""
    await update.message.reply_text(text, reply_markup=main_menu())

def generate_grid():
    mines = random.sample(range(25), 3)
    return mines

def build_grid(revealed, game_over=False):
    keyboard = []
    for i in range(25):
        if i in revealed:
            text = "💎"
        else:
            text = "⬜"
        keyboard.append(InlineKeyboardButton(text, callback_data=f"cell_{i}"))

    grid = [keyboard[i:i+5] for i in range(0, 25, 5)]

    if not game_over:
        grid.append([InlineKeyboardButton("💰 Cashout", callback_data="cashout")])

    return InlineKeyboardMarkup(grid)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Solde actuel : {users[user_id]['balance']} FCFA",
            reply_markup=main_menu()
        )

    elif query.data == "mines":
        bet = int(users[user_id]["balance"] * 0.02)
        if bet <= 0:
            await query.edit_message_text("Solde insuffisant ❌", reply_markup=main_menu())
            return

        users[user_id]["balance"] -= bet

        games[user_id] = {
            "mines": generate_grid(),
            "revealed": [],
            "bet": bet
        }

        await query.edit_message_text(
            f"🎮 Mines lancé !\nMise : {bet} FCFA",
            reply_markup=build_grid([])
        )

    elif query.data.startswith("cell_"):
        if user_id not in games:
            return

        index = int(query.data.split("_")[1])
        game = games[user_id]

        if index in game["mines"]:
            users[user_id]["losses"] += 1
            del games[user_id]
            await query.edit_message_text(
                "💣 BOOM ! Vous avez perdu.",
                reply_markup=main_menu()
            )
        else:
            game["revealed"].append(index)
            multiplier = 1 + (len(game["revealed"]) * 0.5)
            await query.edit_message_reply_markup(
                reply_markup=build_grid(game["revealed"])
            )

    elif query.data == "cashout":
        if user_id not in games:
            return

        game = games[user_id]
        multiplier = 1 + (len(game["revealed"]) * 0.5)
        win = int(game["bet"] * multiplier)

        users[user_id]["balance"] += win
        users[user_id]["wins"] += 1
        del games[user_id]

        await query.edit_message_text(
            f"💰 Cashout réussi !\nGain : {win} FCFA",
            reply_markup=main_menu()
        )

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(menu_handler))

app.run_polling()