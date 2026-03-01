import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN manquant dans Railway Variables")

# =========================
# STOCKAGE SIMPLE
# =========================

users = {}
mines_games = {}
jet_games = {}

GRID_SIZE = 5
BOMB_COUNT = 3
BET = 1000
JET_BET = 1000


# =========================
# UTILISATEUR
# =========================

def get_user(user_id):
    if user_id not in users:
        users[user_id] = 10000
    return users[user_id]


# =========================
# MENU PRINCIPAL
# =========================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("💣 Mines 5x5", callback_data="play_mines")],
        [InlineKeyboardButton("✈️ Lucky Jet LIVE", callback_data="play_jet")],
        [InlineKeyboardButton("💰 Mon solde", callback_data="balance")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance = get_user(update.effective_user.id)

    await update.message.reply_text(
        f"🎰 CASINO PRO MAX\n\n💰 Solde: {balance} FCFA\n\nChoisis un jeu 👇",
        reply_markup=main_menu()
    )


# =========================
# MINES
# =========================

def create_board():
    board = ["safe"] * 25
    bombs = random.sample(range(25), BOMB_COUNT)
    for b in bombs:
        board[b] = "bomb"
    return board


def build_mines_keyboard(opened):
    keyboard = []
    for i in range(0, 25, GRID_SIZE):
        row = []
        for j in range(GRID_SIZE):
            index = i + j
            if index in opened:
                row.append(InlineKeyboardButton("💎", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton("⬜", callback_data=f"cell_{index}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("💰 Cashout", callback_data="mines_cashout")])
    return InlineKeyboardMarkup(keyboard)


async def start_mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    balance = get_user(user_id)

    if balance < BET:
        await update.callback_query.answer("❌ Solde insuffisant")
        return

    users[user_id] -= BET

    mines_games[user_id] = {
        "board": create_board(),
        "opened": [],
        "multiplier": 1.0
    }

    await update.callback_query.edit_message_text(
        "💣 MINES 5x5\n\nChoisis une case",
        reply_markup=build_mines_keyboard([])
    )


async def handle_mines_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in mines_games:
        return

    game = mines_games[user_id]

    if query.data == "mines_cashout":
        gain = int(BET * game["multiplier"])
        users[user_id] += gain
        del mines_games[user_id]

        await query.edit_message_text(
            f"💰 CASHOUT\nMultiplicateur: x{round(game['multiplier'],2)}\nGain: {gain} FCFA",
            reply_markup=main_menu()
        )
        return

    if query.data.startswith("cell_"):
        index = int(query.data.split("_")[1])

        if index in game["opened"]:
            return

        game["opened"].append(index)

        if game["board"][index] == "bomb":
            del mines_games[user_id]
            await query.edit_message_text(
                "💥 BOOM ! Bombe trouvée !\n\nPartie terminée.",
                reply_markup=main_menu()
            )
            return
        else:
            game["multiplier"] += 0.3

            await query.edit_message_text(
                f"💎 Safe !\nMultiplicateur: x{round(game['multiplier'],2)}",
                reply_markup=build_mines_keyboard(game["opened"])
            )


# =========================
# LUCKY JET LIVE
# =========================

async def start_jet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    balance = get_user(user_id)

    if balance < JET_BET:
        await update.callback_query.answer("❌ Solde insuffisant")
        return

    users[user_id] -= JET_BET

    crash_point = round(random.uniform(1.5, 6.0), 2)

    jet_games[user_id] = {
        "multiplier": 1.0,
        "crash": crash_point,
        "active": True
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Cashout", callback_data="jet_cashout")]
    ])

    message = await update.callback_query.edit_message_text(
        "✈️ LUCKY JET LIVE\n\n🚀 x1.00",
        reply_markup=keyboard
    )

    context.application.create_task(run_jet_live(user_id, message))


async def run_jet_live(user_id, message):
    while user_id in jet_games and jet_games[user_id]["active"]:
        await asyncio.sleep(1)

        game = jet_games[user_id]
        game["multiplier"] += 0.2
        current = round(game["multiplier"], 2)

        if current >= game["crash"]:
            game["active"] = False
            del jet_games[user_id]

            await message.edit_text(
                f"💥 CRASH à x{game['crash']} !\n❌ Perdu {JET_BET} FCFA",
                reply_markup=main_menu()
            )
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Cashout", callback_data="jet_cashout")]
        ])

        await message.edit_text(
            f"✈️ LUCKY JET LIVE\n\n🚀 x{current}",
            reply_markup=keyboard
        )


async def handle_jet_cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in jet_games:
        return

    game = jet_games[user_id]

    if not game["active"]:
        return

    gain = int(JET_BET * game["multiplier"])
    users[user_id] += gain
    game["active"] = False
    del jet_games[user_id]

    await query.edit_message_text(
        f"💎 CASHOUT réussi !\nMultiplicateur: x{round(game['multiplier'],2)}\nGain: {gain} FCFA",
        reply_markup=main_menu()
    )


# =========================
# CALLBACK ROUTER
# =========================

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "play_mines":
        await start_mines(update, context)

    elif query.data == "play_jet":
        await start_jet(update, context)

    elif query.data == "balance":
        balance = get_user(query.from_user.id)
        await query.edit_message_text(
            f"💰 Ton solde: {balance} FCFA",
            reply_markup=main_menu()
        )

    elif query.data.startswith("cell_") or query.data == "mines_cashout":
        await handle_mines_click(update, context)

    elif query.data == "jet_cashout":
        await handle_jet_cashout(update, context)


# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_router))

    print("CASINO PRO MAX ACTIF")
    app.run_polling()


if __name__ == "__main__":
    main()