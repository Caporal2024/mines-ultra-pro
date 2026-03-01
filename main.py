import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("TOKEN")  # ⚠️ Ton token sera ajouté dans Railway/Render

INITIAL_CAPITAL = 10000
BET = 1000

user_data_store = {}

# =========================
# INITIALISATION UTILISATEUR
# =========================

def init_user(user_id):
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            "capital": INITIAL_CAPITAL,
            "wins": 0,
            "losses": 0,
            "games": 0,
            "user_mines": [],
            "opened_cells": [],
            "mines_game_active": False,
            "current_multiplier": 1.0,
            "mines_count": 3
        }

# =========================
# MENU PRINCIPAL
# =========================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 MINES PRO MAX", callback_data="config_mines")],
        [InlineKeyboardButton("🚀 LIVE CRASH IA", callback_data="live_crash")],
        [InlineKeyboardButton("💰 GUICHET", callback_data="guichet")],
        [InlineKeyboardButton("📊 STATISTIQUES", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

# =========================
# COMMANDE START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    init_user(user_id)

    await update.message.reply_text(
        "💎 BIENVENUE DANS PRO MAX CASINO 💎",
        reply_markup=main_menu()
    )

# =========================
# MINES CONFIG
# =========================

def mines_config_menu():
    keyboard = [
        [InlineKeyboardButton("🟢 3 Mines", callback_data="mines_3")],
        [InlineKeyboardButton("🟠 5 Mines", callback_data="mines_5")],
        [InlineKeyboardButton("🔴 7 Mines", callback_data="mines_7")],
        [InlineKeyboardButton("🔙 Retour", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def open_mines_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎮 Choisis le nombre de mines :",
        reply_markup=mines_config_menu()
    )

# =========================
# GENERATION MINES
# =========================

def generate_mines(count):
    return random.sample(range(25), count)

def mines_keyboard(opened):
    keyboard = []
    for i in range(25):
        if i in opened:
            text = "💎"
        else:
            text = "🟪"
        keyboard.append(InlineKeyboardButton(text, callback_data=f"cell_{i}"))

    grid = [keyboard[i:i+5] for i in range(0, 25, 5)]
    grid.append([InlineKeyboardButton("💰 ENCAISSER", callback_data="cashout")])
    return InlineKeyboardMarkup(grid)

# =========================
# START MINES
# =========================

async def choose_mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    init_user(user_id)

    count = int(query.data.split("_")[1])
    user_data_store[user_id]["mines_count"] = count
    user_data_store[user_id]["user_mines"] = generate_mines(count)
    user_data_store[user_id]["opened_cells"] = []
    user_data_store[user_id]["current_multiplier"] = 1.0
    user_data_store[user_id]["mines_game_active"] = True

    await query.edit_message_text(
        f"🎮 MINES PRO MAX\nMines : {count}\nMultiplier : x1.0",
        reply_markup=mines_keyboard([])
    )

# =========================
# CLIC CASE
# =========================

async def handle_mine_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    init_user(user_id)

    if not user_data_store[user_id]["mines_game_active"]:
        return

    index = int(query.data.split("_")[1])
    mines = user_data_store[user_id]["user_mines"]
    opened = user_data_store[user_id]["opened_cells"]

    if index in mines:
        user_data_store[user_id]["capital"] -= BET
        user_data_store[user_id]["losses"] += 1
        user_data_store[user_id]["games"] += 1
        user_data_store[user_id]["mines_game_active"] = False

        await query.edit_message_text(
            "💥 BOOM ! Mine touchée !",
            reply_markup=main_menu()
        )
        return

    opened.append(index)
    risk_factor = user_data_store[user_id]["mines_count"] / 3
    new_multiplier = round(1 + (len(opened) * 0.4 * risk_factor), 2)
    user_data_store[user_id]["current_multiplier"] = new_multiplier

    await query.edit_message_text(
        f"💎 Safe !\nCases ouvertes : {len(opened)}\nMultiplier : x{new_multiplier}",
        reply_markup=mines_keyboard(opened)
    )

# =========================
# CASHOUT
# =========================

async def cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    init_user(user_id)

    multiplier = user_data_store[user_id]["current_multiplier"]
    gain = int(BET * multiplier)

    user_data_store[user_id]["capital"] += gain
    user_data_store[user_id]["wins"] += 1
    user_data_store[user_id]["games"] += 1
    user_data_store[user_id]["mines_game_active"] = False

    await query.edit_message_text(
        f"💰 Gain encaissé !\n+{gain} FCFA\nCapital : {user_data_store[user_id]['capital']} FCFA",
        reply_markup=main_menu()
    )

# =========================
# LIVE CRASH
# =========================

async def live_crash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    multiplier = round(random.uniform(1.1, 5.0), 2)

    await query.edit_message_text(
        f"🚀 LIVE CRASH\nMultiplier sorti : x{multiplier}",
        reply_markup=main_menu()
    )

# =========================
# GUICHET
# =========================

async def guichet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "💰 GUICHET\n\nDépôt et Retrait en simulation.\nContact admin pour réel.",
        reply_markup=main_menu()
    )

# =========================
# STATS
# =========================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    init_user(user_id)
    data = user_data_store[user_id]

    await query.edit_message_text(
        f"📊 STATISTIQUES\n\n"
        f"Capital : {data['capital']} FCFA\n"
        f"Parties : {data['games']}\n"
        f"Victoires : {data['wins']}\n"
        f"Défaites : {data['losses']}",
        reply_markup=main_menu()
    )

# =========================
# BACK
# =========================

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Menu principal", reply_markup=main_menu())

# =========================
# LANCEMENT
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(open_mines_config, pattern="config_mines"))
app.add_handler(CallbackQueryHandler(choose_mines, pattern="mines_"))
app.add_handler(CallbackQueryHandler(handle_mine_click, pattern="cell_"))
app.add_handler(CallbackQueryHandler(cashout, pattern="cashout"))
app.add_handler(CallbackQueryHandler(live_crash, pattern="live_crash"))
app.add_handler(CallbackQueryHandler(guichet, pattern="guichet"))
app.add_handler(CallbackQueryHandler(stats, pattern="stats"))
app.add_handler(CallbackQueryHandler(back, pattern="back"))

app.run_polling()