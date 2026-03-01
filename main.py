import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN manquant dans Railway")

# =============================
# CONFIG IA & CAPITAL
# =============================

START_BALANCE = 10000
BET = 1000
JET_BET = 1000

STOP_LOSS = -3000
PROFIT_TARGET = 4000

GRID_SIZE = 5

# =============================
# STOCKAGE
# =============================

users = {}
user_data = {}
mines_games = {}
jet_games = {}

# =============================
# UTILISATEUR & IA
# =============================

def init_user(user_id):
    if user_id not in users:
        users[user_id] = START_BALANCE

    if user_id not in user_data:
        user_data[user_id] = {
            "start_balance": START_BALANCE
        }

def get_user(user_id):
    init_user(user_id)
    return users[user_id]

def ai_control(user_id):
    current = users[user_id]
    start = user_data[user_id]["start_balance"]
    profit = current - start

    if profit <= STOP_LOSS:
        return "stop"
    if profit >= PROFIT_TARGET:
        return "target"
    return "ok"

# =============================
# MENU PRINCIPAL
# =============================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("💣 Mines 3 Bombes LIVE", callback_data="mines_3")],
        [InlineKeyboardButton("💣 Mines 5 Bombes LIVE", callback_data="mines_5")],
        [InlineKeyboardButton("💣 Mines 7 Bombes LIVE", callback_data="mines_7")],
        [InlineKeyboardButton("✈️ Lucky Jet LIVE", callback_data="jet")],
        [InlineKeyboardButton("💰 Mon solde", callback_data="balance")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"🎰 CASINO IA ELITE\n\n💰 Solde: {balance} FCFA\n\nChoisis ton jeu 👇",
        reply_markup=main_menu()
    )

# =============================
# MINES SYSTEM
# =============================

def create_board(bombs):
    board = ["safe"] * 25
    bomb_positions = random.sample(range(25), bombs)
    for b in bomb_positions:
        board[b] = "bomb"
    return board

def mines_keyboard(opened):
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
    keyboard.append([InlineKeyboardButton("💰 Cashout", callback_data="cashout")])
    return InlineKeyboardMarkup(keyboard)

async def start_mines(update, context, bombs):
    query = update.callback_query
    user_id = query.from_user.id

    init_user(user_id)

    if ai_control(user_id) != "ok":
        await query.answer("🛑 Gestion IA activée")
        return

    if users[user_id] < BET:
        await query.answer("❌ Solde insuffisant")
        return

    users[user_id] -= BET

    mines_games[user_id] = {
        "board": create_board(bombs),
        "opened": [],
        "multiplier": 1.0,
        "bombs": bombs
    }

    await query.edit_message_text(
        f"💣 MINES {bombs} BOMBES LIVE\n\nChoisis une case",
        reply_markup=mines_keyboard([])
    )

async def handle_mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in mines_games:
        return

    game = mines_games[user_id]

    if query.data == "cashout":
        gain = int(BET * game["multiplier"])
        users[user_id] += gain
        del mines_games[user_id]

        await query.edit_message_text(
            f"💰 CASHOUT x{round(game['multiplier'],2)}\nGain: {gain} FCFA",
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
                "💥 BOOM ! Partie perdue.",
                reply_markup=main_menu()
            )
        else:
            # IA ajuste risque
            game["multiplier"] += (0.2 + game["bombs"] * 0.05)

            await query.edit_message_text(
                f"💎 Safe ! x{round(game['multiplier'],2)}",
                reply_markup=mines_keyboard(game["opened"])
            )

# =============================
# LUCKY JET LIVE
# =============================

async def start_jet(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    init_user(user_id)

    if ai_control(user_id) != "ok":
        await query.answer("🛑 Gestion IA activée")
        return

    if users[user_id] < JET_BET:
        await query.answer("❌ Solde insuffisant")
        return

    users[user_id] -= JET_BET

    crash = round(random.uniform(1.5, 6.0), 2)

    jet_games[user_id] = {
        "multiplier": 1.0,
        "crash": crash,
        "active": True
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Cashout", callback_data="jet_cashout")]
    ])

    message = await query.edit_message_text(
        "✈️ LUCKY JET LIVE\n\n🚀 x1.00",
        reply_markup=keyboard
    )

    context.application.create_task(run_jet(user_id, message))

async def run_jet(user_id, message):
    while user_id in jet_games and jet_games[user_id]["active"]:
        await asyncio.sleep(1)

        game = jet_games[user_id]
        game["multiplier"] += 0.25

        current = round(game["multiplier"], 2)

        if current >= game["crash"]:
            del jet_games[user_id]
            await message.edit_text(
                f"💥 CRASH à x{game['crash']}",
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

async def jet_cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in jet_games:
        return

    game = jet_games[user_id]
    gain = int(JET_BET * game["multiplier"])

    users[user_id] += gain
    del jet_games[user_id]

    await query.edit_message_text(
        f"💎 CASHOUT x{round(game['multiplier'],2)}\nGain: {gain} FCFA",
        reply_markup=main_menu()
    )

# =============================
# ROUTER
# =============================

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "mines_3":
        await start_mines(update, context, 3)

    elif query.data == "mines_5":
        await start_mines(update, context, 5)

    elif query.data == "mines_7":
        await start_mines(update, context, 7)

    elif query.data == "jet":
        await start_jet(update, context)

    elif query.data == "balance":
        balance = get_user(query.from_user.id)
        await query.edit_message_text(
            f"💰 Ton solde: {balance} FCFA",
            reply_markup=main_menu()
        )

    elif query.data.startswith("cell_") or query.data == "cashout":
        await handle_mines(update, context)

    elif query.data == "jet_cashout":
        await jet_cashout(update, context)

# =============================
# MAIN
# =============================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(router))

    print("CASINO IA ELITE ACTIF")
    app.run_polling()

if __name__ == "__main__":
    main()