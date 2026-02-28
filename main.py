import random
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from database import *

TOKEN = os.getenv("BOT_TOKEN")  # ← TOKEN vient de Railway
ADMIN_ID = 123456789

active_users = set()
games = {}

# ================= MENU =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    keyboard = [
        [InlineKeyboardButton("💣 Mines", callback_data="mines")],
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="jet")],
        [InlineKeyboardButton("⚽ Penalty", callback_data="penalty")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("🏆 Top", callback_data="top")],
    ]

    await update.message.reply_text(
        f"━━━━━━━━━━━━━━\n"
        f"🎰 CASINO PRO MAX\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"💰 Solde: {user[1]} FCFA\n"
        f"🏆 Wins: {user[2]}\n"
        f"❌ Losses: {user[3]}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= MINES =================

async def start_mines(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)

    if user[1] <= 0:
        await query.edit_message_text("🛑 Solde insuffisant.")
        return

    mines = random.sample(range(25), 4)
    games[user_id] = {"mines": mines, "revealed": []}

    await show_mines_board(query, user_id)


async def show_mines_board(query, user_id):
    keyboard = []

    for i in range(25):
        if i in games[user_id]["revealed"]:
            btn = InlineKeyboardButton("⭐", callback_data="ignore")
        else:
            btn = InlineKeyboardButton("🟦", callback_data=f"mine_{i}")
        keyboard.append(btn)

    rows = [keyboard[i:i+5] for i in range(0, 25, 5)]

    await query.edit_message_text(
        "💣 MINES PRO\nClique sur une case :",
        reply_markup=InlineKeyboardMarkup(rows)
    )


async def mines_click(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    index = int(query.data.split("_")[1])
    bet = get_bet(user_id)

    if index in games[user_id]["mines"]:
        update_balance(user_id, -bet)
        add_loss(user_id)
        add_history(user_id, "Mines", "Loss", bet)
        await query.edit_message_text("💥 BOOM ! Tu as perdu.")
    else:
        update_balance(user_id, bet)
        add_win(user_id)
        add_history(user_id, "Mines", "Win", bet)
        games[user_id]["revealed"].append(index)
        await show_mines_board(query, user_id)


# ================= LUCKY JET =================

async def start_jet(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    bet = get_bet(user_id)

    crash = round(random.uniform(1.5, 6.0), 2)
    current = 1.0
    speed = 0.05

    while current < crash:
        await asyncio.sleep(0.5)
        current += speed
        speed += 0.02

        await query.edit_message_text(
            f"🚀 LUCKY JET\n\nMultiplicateur: x{round(current,2)}"
        )

    update_balance(user_id, -bet)
    add_loss(user_id)
    add_history(user_id, "Jet", "Crash", bet)

    await query.edit_message_text(f"💥 CRASH à x{crash}")


# ================= PENALTY =================

async def start_penalty(update, context):
    query = update.callback_query
    await query.answer()

    keeper = random.choice(["⬅️", "⬆️", "➡️"])
    games[query.from_user.id] = {"keeper": keeper}

    keyboard = [[
        InlineKeyboardButton("⬅️", callback_data="p_left"),
        InlineKeyboardButton("⬆️", callback_data="p_center"),
        InlineKeyboardButton("➡️", callback_data="p_right"),
    ]]

    await query.edit_message_text(
        "⚽ PENALTY\n\nChoisis où tirer :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def penalty_shot(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    bet = get_bet(user_id)

    mapping = {"left": "⬅️", "center": "⬆️", "right": "➡️"}
    player = query.data.split("_")[1]
    keeper = games[user_id]["keeper"]

    if mapping[player] == keeper:
        update_balance(user_id, -bet)
        add_loss(user_id)
        add_history(user_id, "Penalty", "Saved", bet)
        result = "🧤 ARRÊT !"
    else:
        update_balance(user_id, bet)
        add_win(user_id)
        add_history(user_id, "Penalty", "Goal", bet)
        result = "🎉 BUT !"

    await query.edit_message_text(f"⚽ {result}")


# ================= ROUTER =================

async def button_router(update, context):
    query = update.callback_query

    if query.data == "mines":
        await start_mines(update, context)

    elif query.data.startswith("mine_"):
        await mines_click(update, context)

    elif query.data == "jet":
        await start_jet(update, context)

    elif query.data == "penalty":
        await start_penalty(update, context)

    elif query.data.startswith("p_"):
        await penalty_shot(update, context)


# ================= RUN =================

if not TOKEN:
    raise ValueError("BOT_TOKEN non défini dans Railway !")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_router))

print("Casino PRO MAX lancé...")
app.run_polling()