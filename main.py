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
    return random.sample(range(25), 3)

def build_grid(game, game_over=False):
    keyboard = []

    for i in range(25):
        if i in game["revealed"]:
            text = "💎"
        elif game_over and i in game["mines"]:
            text = "💣"
        else:
            text = "⬜"

        keyboard.append(
            InlineKeyboardButton(text, callback_data=f"cell_{i}")
        )

    grid = [keyboard[i:i+5] for i in range(0, 25, 5)]

    if not game_over:
        grid.append([InlineKeyboardButton("💰 Cashout", callback_data="cashout")])
    else:
        grid.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])

    return InlineKeyboardMarkup(grid)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "menu":
        await query.edit_message_text("Menu principal 👇", reply_markup=main_menu())
        return

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
            reply_markup=build_grid(games[user_id])
        )

    elif query.data.startswith("cell_"):
        if user_id not in games:
            return

        index = int(query.data.split("_")[1])
        game = games[user_id]

        if index in game["revealed"]:
            return  # empêche double clic

        if index in game["mines"]:
            users[user_id]["losses"] += 1
            await query.edit_message_text(
                "💣 BOOM ! Vous avez perdu.",
                reply_markup=build_grid(game, game_over=True)
            )
            del games[user_id]
        else:
            game["revealed"].append(index)
            multiplier = 1 + (len(game["revealed"]) * 0.5)
            potential = int(game["bet"] * multiplier)

            await query.edit_message_text(
                f"💎 Safe !\n\nCases ouvertes : {len(game['revealed'])}\nMultiplicateur : x{multiplier}\nGain potentiel : {potential} FCFA",
                reply_markup=build_grid(game)
            )

    elif query.data == "cashout":
        if user_id not in games:
            return

        game = games[user_id]
        multiplier = 1 + (len(game["revealed"]) * 0.5)
        win = int(game["bet"] * multiplier)

        users[user_id]["balance"] += win
        users[user_id]["wins"] += 1

        await query.edit_message_text(
            f"💰 Cashout réussi !\nGain : {win} FCFA",
            reply_markup=main_menu()
        )

        del games[user_id]

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(menu_handler))

app.run_polling()