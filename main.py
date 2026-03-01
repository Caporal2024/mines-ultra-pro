import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("TOKEN")

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 1000,
            "wins": 0,
            "losses": 0,
            "game": None,
            "mines": [],
            "revealed": [],
            "bet": 100,
            "multiplier": 1.0
        }
    return users[user_id]

# ================= MENU =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("✈️ Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("💰 Capital", callback_data="capital")]
    ]

    await update.message.reply_text(
        "🎰 CASINO ULTRA PRO\nChoisis un jeu :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= CAPITAL =================

async def show_capital(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(f"💰 Capital : {user['balance']} FCFA")

async def show_stats(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(
        f"📊 Stats\n\n"
        f"Victoires : {user['wins']}\n"
        f"Pertes : {user['losses']}\n"
        f"Capital : {user['balance']} FCFA"
    )

# ================= MINES =================

async def mines_menu(query):
    keyboard = [
        [InlineKeyboardButton("💣 3 Mines", callback_data="m3")],
        [InlineKeyboardButton("💣 5 Mines", callback_data="m5")],
        [InlineKeyboardButton("💣 7 Mines", callback_data="m7")]
    ]
    await query.edit_message_text(
        "Choisis le nombre de mines :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_mines(query, mines_count):
    user = get_user(query.from_user.id)

    if user["balance"] < user["bet"]:
        await query.edit_message_text("Solde insuffisant ❌")
        return

    user["balance"] -= user["bet"]
    user["game"] = "mines"
    user["multiplier"] = 1.0
    user["revealed"] = []
    user["mines"] = random.sample(range(25), mines_count)

    await update_board(query)

async def update_board(query):
    user = get_user(query.from_user.id)

    buttons = []
    for i in range(25):
        if i in user["revealed"]:
            text = "💎"
        else:
            text = "❓"
        buttons.append(InlineKeyboardButton(text, callback_data=f"c{i}"))

    grid = [buttons[i:i+5] for i in range(0, 25, 5)]
    grid.append([InlineKeyboardButton("💰 Cashout", callback_data="cash")])

    await query.edit_message_text(
        f"Mines 5x5\nMultiplicateur : x{round(user['multiplier'],2)}",
        reply_markup=InlineKeyboardMarkup(grid)
    )

async def click_cell(query, index):
    user = get_user(query.from_user.id)

    if user["game"] != "mines":
        return

    if index in user["mines"]:
        user["losses"] += 1
        user["game"] = None
        await query.edit_message_text("💣 BOOM ! Perdu.")
        return

    user["revealed"].append(index)
    user["multiplier"] += 0.3
    await update_board(query)

async def cashout(query):
    user = get_user(query.from_user.id)

    if user["game"] != "mines":
        return

    gain = int(user["bet"] * user["multiplier"])
    user["balance"] += gain
    user["wins"] += 1
    user["game"] = None

    await query.edit_message_text(f"💰 Gain : {gain} FCFA")

# ================= LUCKY JET =================

async def lucky_game(query):
    user = get_user(query.from_user.id)

    if user["balance"] < user["bet"]:
        await query.edit_message_text("Solde insuffisant ❌")
        return

    user["balance"] -= user["bet"]
    crash = round(random.uniform(1.2, 5.0), 2)

    gain = int(user["bet"] * crash)
    user["balance"] += gain
    user["wins"] += 1

    await query.edit_message_text(
        f"✈️ Crash à x{crash}\n💰 Gain : {gain} FCFA"
    )

# ================= HANDLER =================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "mines":
        await mines_menu(query)

    elif data in ["m3", "m5", "m7"]:
        mines_count = int(data[1])
        await start_mines(query, mines_count)

    elif data.startswith("c"):
        index = int(data[1:])
        await click_cell(query, index)

    elif data == "cash":
        await cashout(query)

    elif data == "lucky":
        await lucky_game(query)

    elif data == "stats":
        await show_stats(query)

    elif data == "capital":
        await show_capital(query)

# ================= RUN =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

print("🔥 CASINO LANCÉ 🔥")
app.run_polling()