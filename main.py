import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("TOKEN")

users = {}
games = {}

# ===============================
# SYSTEME VIP
# ===============================

def get_vip_level(solde):
    if solde > 10000:
        return "💎 VIP GOLD"
    elif solde > 5000:
        return "🥈 VIP SILVER"
    else:
        return "🥉 STANDARD"

# ===============================
# START
# ===============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = 1000

    await update.message.reply_text(
        f"🔥 Casino Actif\n"
        f"💰 Solde : {users[user_id]} FCFA\n"
        f"Utilise /luckyjet ou /mines"
    )

# ===============================
# BALANCE
# ===============================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    solde = users.get(user_id, 0)
    vip = get_vip_level(solde)

    await update.message.reply_text(
        f"💰 Solde : {solde} FCFA\n"
        f"🏆 Statut : {vip}"
    )

# ===============================
# LUCKYJET AVEC CASHOUT
# ===============================

async def luckyjet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) == 0:
        await update.message.reply_text("Utilisation : /luckyjet 200")
        return

    mise = int(context.args[0])

    if users.get(user_id, 0) < mise:
        await update.message.reply_text("❌ Solde insuffisant")
        return

    users[user_id] -= mise

    multiplier = 1.00
    crash = round(random.uniform(1.5, 4.0), 2)

    keyboard = [[InlineKeyboardButton("💰 CASHOUT", callback_data="cashout")]]

    msg = await update.message.reply_text(
        f"🚀 Décollage...\nMultiplicateur : x{multiplier}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    games[user_id] = {
        "crash": crash,
        "current": multiplier,
        "mise": mise,
        "message": msg,
    }

    while multiplier < crash:
        await asyncio.sleep(1)
        multiplier += round(random.uniform(0.1, 0.4), 2)
        games[user_id]["current"] = multiplier

        await msg.edit_text(
            f"🚀 En vol...\nMultiplicateur : x{round(multiplier,2)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    if user_id in games:
        await msg.edit_text(f"💥 Crash à x{crash}")
        del games[user_id]

async def cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in games:
        return

    game = games[user_id]

    gain = int(game["mise"] * game["current"])
    users[user_id] += gain

    await query.edit_message_text(
        f"💰 CASHOUT réussi !\n"
        f"x{round(game['current'],2)}\n"
        f"Gain : {gain} FCFA\n"
        f"Nouveau solde : {users[user_id]}"
    )

    del games[user_id]

# ===============================
# MINES
# ===============================

async def mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    mines_positions = random.sample(range(25), 3)

    games[user_id] = {
        "mines": mines_positions,
        "revealed": [],
        "multiplier": 1.0
    }

    keyboard = []
    for i in range(5):
        row = []
        for j in range(5):
            index = i * 5 + j
            row.append(InlineKeyboardButton("❓", callback_data=f"mine_{index}"))
        keyboard.append(row)

    await update.message.reply_text(
        "💣 Mines - Trouve les cases sûres !",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def mines_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if user_id not in games:
        return

    index = int(data.split("_")[1])
    game = games[user_id]

    if index in game["mines"]:
        await query.edit_message_text("💥 BOOM ! Tu as touché une mine.")
        del games[user_id]
        return

    if index not in game["revealed"]:
        game["revealed"].append(index)
        game["multiplier"] += 0.3

    keyboard = []
    for i in range(5):
        row = []
        for j in range(5):
            idx = i * 5 + j
            if idx in game["revealed"]:
                row.append(InlineKeyboardButton("💎", callback_data="safe"))
            else:
                row.append(InlineKeyboardButton("❓", callback_data=f"mine_{idx}"))
        keyboard.append(row)

    await query.edit_message_text(
        f"💎 Safe !\nMultiplicateur : x{round(game['multiplier'],2)}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===============================
# LANCEMENT
# ===============================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("luckyjet", luckyjet))
app.add_handler(CommandHandler("mines", mines))
app.add_handler(CallbackQueryHandler(mines_click, pattern="mine_"))
app.add_handler(CallbackQueryHandler(cashout, pattern="cashout"))

print("🔥 CASINO DEMARRE")
app.run_polling()