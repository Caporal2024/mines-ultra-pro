import os
import random
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("TOKEN")

# =========================
# STOCKAGE SIMPLE EN MEMOIRE
# =========================

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

# =========================
# MENU PRINCIPAL
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Mines 5x5", callback_data="mines_menu")],
        [InlineKeyboardButton("✈️ Lucky Jet", callback_data="lucky_start")],
        [InlineKeyboardButton("📊 Statistiques", callback_data="stats")],
        [InlineKeyboardButton("💰 Mon Capital", callback_data="capital")]
    ]

    await update.message.reply_text(
        "🎰 CASINO ULTRA PRO\n\nChoisis un jeu :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# CAPITAL & STATS
# =========================

async def show_capital(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(f"💰 Capital actuel : {user['balance']} FCFA")

async def show_stats(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(
        f"📊 Statistiques\n\n"
        f"✅ Victoires : {user['wins']}\n"
        f"❌ Pertes : {user['losses']}\n"
        f"💰 Capital : {user['balance']} FCFA"
    )

# =========================
# MINES
# =========================

async def mines_menu(query):
    keyboard = [
        [InlineKeyboardButton("💣 3 Mines", callback_data="mines_3")],
        [InlineKeyboardButton("💣 5 Mines", callback_data="mines_5")],
        [InlineKeyboardButton("💣 7 Mines", callback_data="mines_7")]
    ]
    await query.edit_message_text(
        "Choisis le nombre de mines :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_mines(query, mines_count):
    user = get_user(query.from_user.id)

    if user["balance"] < user["bet"]:
        await query.edit_message_text("❌ Solde insuffisant.")
        return

    user["game"] = "mines"
    user["balance"] -= user["bet"]
    user["multiplier"] = 1.0
    user["revealed"] = []
    user["mines"] = random.sample(range(25), mines_count)

    await update_mines_board(query)

async def update_mines_board(query):
    user = get_user(query.from_user.id)

    keyboard = []
    for i in range(25):
        if i in user["revealed"]:
            text = "💎"
        else:
            text = "❓"
        keyboard.append(
            InlineKeyboardButton(text, callback_data=f"cell_{i}")
        )

    grid = [keyboard[i:i+5] for i in range(0, 25, 5)]

    grid.append([InlineKeyboardButton("💰 Cashout", callback_data="cashout")])

    await query.edit_message_text(
        f"🎮 Mines 5x5\n💰 Capital: {user['balance']} FCFA\n"
        f"🎯 Multiplicateur: x{round(user['multiplier'],2)}",
        reply_markup=InlineKeyboardMarkup(grid)
    )

async def handle_cell(query, index):
    user = get_user(query.from_user.id)

    if user["game"] != "mines":
        return

    if index in user["revealed"]:
        return

    if index in user["mines"]:
        user["losses"] += 1
        user["game"] = None
        await query.edit_message_text("💣 BOOM ! Tu as perdu.")
        return

    user["revealed"].append(index)
    user["multiplier"] += 0.3
    await update_mines_board(query)

async def cashout(query):
    user = get_user(query.from_user.id)

    if user["game"] != "mines":
        return

    gain = int(user["bet"] * user["multiplier"])
    user["balance"] += gain
    user["wins"] += 1
    user["game"] = None

    await query.edit_message_text(f"💰 Gain : {gain} FCFA")

# =========================
# LUCKY JET
# =========================

async def lucky_start(query):
    user = get_user(query.from_user.id)

    if user["balance"] < user["bet"]:
        await query.edit_message_text("❌ Solde insuffisant.")
        return

    user["balance"] -= user["bet"]
    crash = round(random.uniform(1.2, 5.0), 2)

    keyboard = [
        [InlineKeyboardButton("💰 Cashout", callback_data=f"lucky_cash_{crash}")]
    ]

    await query.edit_message_text(
        f"✈️ Lucky Jet\n\nMultiplicateur monte...\n"
        f"(Crash à x{crash})",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def lucky_cash(query, crash):
    user = get_user(query.from_user.id)

    win = int(user["bet"] * crash)
    user["balance"] += win
    user["wins"] += 1

    await query.edit_message_text(f"💰 Tu as gagné {win} FCFA !")

# =========================
# CALLBACK HANDLER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "mines_menu":
        await mines_menu(query)

    elif data.startswith("mines_"):
        mines_count = int(data.split("_")[1])
        await start_mines(query, mines_count)

    elif data.startswith("cell_"):
        index = int(data.split("_")[1])
        await handle_cell(query, index)

    elif data == "cashout":
        await cashout(query)

    elif data == "lucky_start":
        await lucky_start(query)

    elif data.startswith("lucky_cash_"):
        crash = float(data.split("_")[2])
        await lucky_cash(query, crash)

    elif data == "stats":
        await show_stats(query)

    elif data == "capital":
        await show_capital(query)

# =========================
# LANCEMENT BOT
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

print("🔥 CASINO ULTRA PRO LANCE 🔥")
app.run_polling()