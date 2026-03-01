import random
import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

users = {}

# =========================
# MENU PRINCIPAL
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💣 MINES 5x5 • 3 Bombes", callback_data="mines_3")],
        [InlineKeyboardButton("💣 MINES 5x5 • 5 Bombes", callback_data="mines_5")],
        [InlineKeyboardButton("💣 MINES 5x5 • 7 Bombes", callback_data="mines_7")],
        [InlineKeyboardButton("🚀 LUCKY JET LIVE ⚡", callback_data="jet")],
        [InlineKeyboardButton("🧠 GESTION CAPITAL IA", callback_data="capital")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("🔥 MENU PRINCIPAL 🔥", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text("🔥 MENU PRINCIPAL 🔥", reply_markup=reply_markup)

# =========================
# GENERER GRILLE
# =========================
def generate_board(bombs):
    board = ["💎"] * 25
    bomb_positions = random.sample(range(25), bombs)
    for pos in bomb_positions:
        board[pos] = "💣"
    return board

# =========================
# LANCER MINES
# =========================
async def start_mines(update: Update, context: ContextTypes.DEFAULT_TYPE, bombs):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    board = generate_board(bombs)

    users[user_id] = {
        "board": board,
        "revealed": []
    }

    await update_grid(query, user_id, bombs)

async def update_grid(query, user_id, bombs):
    game = users[user_id]
    board = game["board"]
    revealed = game["revealed"]

    keyboard = []

    for i in range(25):
        if i in revealed:
            text = board[i]
        else:
            text = "⬛"
        keyboard.append(InlineKeyboardButton(text, callback_data=f"cell_{i}_{bombs}"))

    grid = [keyboard[i:i+5] for i in range(0, 25, 5)]
    grid.append([InlineKeyboardButton("🔙 MENU", callback_data="menu")])

    await query.edit_message_text(
        f"💣 MINES 5x5 ({bombs} bombes)\n\nClique une case 👇",
        reply_markup=InlineKeyboardMarkup(grid)
    )

# =========================
# CLIQUER CASE
# =========================
async def handle_mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data.split("_")

    index = int(data[1])
    bombs = int(data[2])

    game = users.get(user_id)
    if not game:
        return

    if index in game["revealed"]:
        return

    game["revealed"].append(index)

    if game["board"][index] == "💣":
        await query.edit_message_text("💥 BOOM ! Tu as perdu.\n\n/start pour rejouer.")
        users.pop(user_id)
        return

    await update_grid(query, user_id, bombs)

# =========================
# LUCKY JET LIVE RAPIDE
# =========================
async def start_jet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = await query.edit_message_text("🚀 LUCKY JET LIVE ⚡\n\nDémarrage...")

    multiplier = 1.00

    for _ in range(10):
        multiplier += random.uniform(0.10, 0.50)
        multiplier = round(multiplier, 2)
        await asyncio.sleep(0.8)
        await message.edit_text(f"🚀 LUCKY JET LIVE ⚡\n\nMultiplicateur : x{multiplier}")

    await message.edit_text(f"💥 Crash à x{multiplier}\n\n/start")

# =========================
# GESTION CAPITAL IA
# =========================
async def capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    suggestion = random.choice([
        "📊 Mise idéale : 2% du capital",
        "📊 Mise agressive : 5%",
        "🛑 Stop Loss conseillé : -15%",
        "🎯 Objectif profit : +20%"
    ])

    await query.edit_message_text(f"🧠 GESTION CAPITAL IA\n\n{suggestion}\n\n/start")

# =========================
# MAIN
# =========================
def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN non défini dans Railway")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(lambda u,c: start_mines(u,c,3), pattern="mines_3"))
    app.add_handler(CallbackQueryHandler(lambda u,c: start_mines(u,c,5), pattern="mines_5"))
    app.add_handler(CallbackQueryHandler(lambda u,c: start_mines(u,c,7), pattern="mines_7"))
    app.add_handler(CallbackQueryHandler(handle_mines, pattern="cell_"))
    app.add_handler(CallbackQueryHandler(start_jet, pattern="jet"))
    app.add_handler(CallbackQueryHandler(capital, pattern="capital"))
    app.add_handler(CallbackQueryHandler(start, pattern="menu"))

    app.run_polling()

if __name__ == "__main__":
    main()