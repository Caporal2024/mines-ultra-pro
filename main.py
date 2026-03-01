import os
import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================= CONFIG =================
STOP_LOSS = -3000
TARGET_PROFIT = 4000
MIN_BET = 100
MAX_BET = 5000

users = {}

# ================= USER SYSTEM =================
def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "start_balance": 10000,
            "wins": 0,
            "losses": 0,
            "game_active": False,
            "mines": [],
            "revealed": [],
            "bet": 1000,
            "multiplier": 1.0,
        }
    return users[user_id]

def check_limits(user):
    profit = user["balance"] - user["start_balance"]
    if profit <= STOP_LOSS:
        return "⛔ Stop Loss atteint."
    if profit >= TARGET_PROFIT:
        return "🎯 Target Profit atteint."
    return None

# ================= MENU =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 MINES 5x5 PRO", callback_data="mines")],
        [InlineKeyboardButton("✈️ LUCKY JET LIVE", callback_data="lucky")],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("💰 Capital", callback_data="capital"),
        ],
    ]

    await update.message.reply_text(
        "🎰 CASINO PRO STABLE\n\nChoisis ton jeu :",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ================= CAPITAL =================
async def show_capital(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(f"💰 Capital : {user['balance']} FCFA")

# ================= STATS =================
async def show_stats(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(
        f"📊 Stats\n\n"
        f"Victoires : {user['wins']}\n"
        f"Défaites : {user['losses']}\n"
        f"Solde : {user['balance']} FCFA"
    )

# ================= LUCKY JET =================
async def lucky_game(query):
    user = get_user(query.from_user.id)

    if user["game_active"]:
        await query.answer("⚠️ Partie déjà en cours.")
        return

    if user["balance"] < user["bet"]:
        await query.edit_message_text("❌ Solde insuffisant.")
        return

    user["game_active"] = True
    multiplier = 1.00
    crashed_at = round(random.uniform(1.2, 3.0), 2)

    msg = await query.edit_message_text("✈️ Lucky Jet LIVE\n🚀 x1.00")

    while multiplier < crashed_at:
        multiplier += 0.1
        await msg.edit_text(f"✈️ Lucky Jet LIVE\n🚀 x{round(multiplier,2)}")
        await asyncio.sleep(0.5)

    user["balance"] -= user["bet"]
    user["losses"] += 1
    user["game_active"] = False

    await msg.edit_text(
        f"💥 Crash à x{crashed_at}\n\n❌ Perdu {user['bet']} FCFA\n💰 Solde : {user['balance']} FCFA"
    )

# ================= MINES =================
async def mines_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("3 Mines", callback_data="m3"),
            InlineKeyboardButton("5 Mines", callback_data="m5"),
            InlineKeyboardButton("7 Mines", callback_data="m7"),
        ]
    ]
    await query.edit_message_text(
        "💣 Choisis le nombre de mines :",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def start_mines(query, mines_count):
    user = get_user(query.from_user.id)

    if user["game_active"]:
        await query.answer("⚠️ Partie déjà en cours.")
        return

    if user["balance"] < user["bet"]:
        await query.edit_message_text("❌ Solde insuffisant.")
        return

    user["game_active"] = True
    user["mines"] = random.sample(range(25), mines_count)
    user["revealed"] = []
    user["multiplier"] = 1.0

    await show_grid(query, user)

async def show_grid(query, user):
    keyboard = []
    for i in range(25):
        text = "💎" if i in user["revealed"] else "⬜"
        keyboard.append(InlineKeyboardButton(text, callback_data=f"c{i}"))

    grid = [keyboard[i:i + 5] for i in range(0, 25, 5)]
    grid.append([InlineKeyboardButton("💰 Cashout", callback_data="cash")])

    await query.edit_message_text(
        f"💣 MINES 5x5\nMultiplier : x{user['multiplier']}",
        reply_markup=InlineKeyboardMarkup(grid),
    )

async def click_cell(query, index):
    user = get_user(query.from_user.id)

    if index in user["mines"]:
        user["balance"] -= user["bet"]
        user["losses"] += 1
        user["game_active"] = False
        await query.edit_message_text(
            f"💥 BOOM !\n❌ Perdu {user['bet']} FCFA\n💰 Solde : {user['balance']} FCFA"
        )
        return

    if index not in user["revealed"]:
        user["revealed"].append(index)
        user["multiplier"] += 0.3

    await show_grid(query, user)

async def cashout(query):
    user = get_user(query.from_user.id)

    gain = int(user["bet"] * user["multiplier"])
    user["balance"] += gain
    user["wins"] += 1
    user["game_active"] = False

    await query.edit_message_text(
        f"💰 Cashout réussi !\nGain : {gain} FCFA\n💰 Solde : {user['balance']} FCFA"
    )

# ================= HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    user = get_user(query.from_user.id)
    limit_message = check_limits(user)
    if limit_message:
        await query.edit_message_text(limit_message)
        return

    if data == "mines":
        await mines_menu(query)
    elif data in ["m3", "m5", "m7"]:
        await start_mines(query, int(data[1]))
    elif data.startswith("c"):
        await click_cell(query, int(data[1:]))
    elif data == "cash":
        await cashout(query)
    elif data == "lucky":
        await lucky_game(query)
    elif data == "stats":
        await show_stats(query)
    elif data == "capital":
        await show_capital(query)

# ================= RUN =================
TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

print("🔥 CASINO PRO STABLE LANCÉ 🔥")

app.run_polling()