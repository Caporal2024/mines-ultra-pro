import os
import random
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8094967191  # 👑 TON ID ADMIN

# ================= DATABASE ================= #

conn = sqlite3.connect("casino.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 10000
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()

    if data is None:
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 10000))
        conn.commit()
        return {"balance": 10000}
    else:
        return {"balance": data[0]}

def update_balance(user_id, new_balance):
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()

# ================= GAME MEMORY ================= #

games = {}

def get_game(user_id):
    if user_id not in games:
        games[user_id] = {
            "mines": [],
            "revealed": [],
            "active": False,
            "bet": 1000
        }
    return games[user_id]

# ================= START ================= #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="luckyjet")],
        [InlineKeyboardButton("💣 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("📊 Balance", callback_data="balance")]
    ]

    await update.message.reply_text(
        "🟣══════════════════🟣\n"
        "     🎰 CASINO PRO MAX 🎰\n"
        "🟣══════════════════🟣\n\n"
        "💎 Interface Violet Néon\n"
        "🔥 Système Premium Activé\n",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= MINES ================= #

async def start_mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)
    game = get_game(user_id)

    if user["balance"] < game["bet"]:
        await query.answer("❌ Solde insuffisant", show_alert=True)
        return

    game["mines"] = random.sample(range(25), 5)
    game["revealed"] = []
    game["active"] = True

    update_balance(user_id, user["balance"] - game["bet"])
    await update_grid(query, user_id)

async def update_grid(query, user_id, game_over=False):
    user = get_user(user_id)
    game = get_game(user_id)

    buttons = []

    for i in range(25):
        if i in game["revealed"] or game_over:
            text = "💥" if i in game["mines"] else "⭐"
        else:
            text = "🟦"

        buttons.append(
            InlineKeyboardButton(text, callback_data=f"cell_{i}")
        )

    grid = [buttons[i:i+5] for i in range(0, 25, 5)]

    if game["active"]:
        grid.append([InlineKeyboardButton("💰 CASHOUT", callback_data="cashout")])

    await query.edit_message_text(
        f"💣 Mines 5x5\n\n💰 Balance: {user['balance']} FCFA",
        reply_markup=InlineKeyboardMarkup(grid)
    )

async def handle_cell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)
    game = get_game(user_id)

    if not game["active"]:
        return

    index = int(query.data.split("_")[1])

    if index in game["revealed"]:
        return

    game["revealed"].append(index)

    if index in game["mines"]:
        game["active"] = False
        await update_grid(query, user_id, True)
        await query.answer("💥 BOOM ! Mise perdue", show_alert=True)
    else:
        reward = 500
        update_balance(user_id, user["balance"] + reward)
        await update_grid(query, user_id)
        await query.answer(f"⭐ SAFE +{reward} FCFA", show_alert=True)

async def cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)
    game = get_game(user_id)

    if not game["active"]:
        return

    gain = len(game["revealed"]) * 300
    update_balance(user_id, user["balance"] + gain)
    game["active"] = False

    await update_grid(query, user_id, True)
    await query.answer(f"💰 Cashout +{gain} FCFA", show_alert=True)

# ================= LUCKY JET ================= #

async def luckyjet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)

    bet = 1000

    if user["balance"] < bet:
        await query.answer("❌ Solde insuffisant", show_alert=True)
        return

    crash = round(random.uniform(1.1, 5.0), 2)

    update_balance(user_id, user["balance"] - bet)
    gain = int(bet * crash)
    update_balance(user_id, get_user(user_id)["balance"] + gain)

    await query.edit_message_text(
        f"🚀 LUCKY JET\n\n"
        f"💥 Crash à {crash}x\n"
        f"💰 Gain : {gain} FCFA\n\n"
        f"Balance : {get_user(user_id)['balance']} FCFA"
    )

# ================= BALANCE ================= #

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)
    await query.edit_message_text(f"💰 Balance : {user['balance']} FCFA")

# ================= ADMIN ================= #

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Accès refusé")
        return

    await update.message.reply_text(
        "👑 PANEL ADMIN\n\n"
        "/add <id> <montant>\n"
        "/set <id> <montant>"
    )

async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    amount = int(context.args[1])

    user = get_user(user_id)
    update_balance(user_id, user["balance"] + amount)

    await update.message.reply_text("✅ Solde ajouté")

async def set_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    amount = int(context.args[1])

    update_balance(user_id, amount)
    await update.message.reply_text("✅ Solde modifié")

# ================= MAIN ================= #

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("add", add_balance))
    app.add_handler(CommandHandler("set", set_balance))

    app.add_handler(CallbackQueryHandler(start_mines, pattern="mines"))
    app.add_handler(CallbackQueryHandler(handle_cell, pattern="cell_"))
    app.add_handler(CallbackQueryHandler(cashout, pattern="cashout"))
    app.add_handler(CallbackQueryHandler(luckyjet, pattern="luckyjet"))
    app.add_handler(CallbackQueryHandler(balance, pattern="balance"))

    print("CASINO PRO MAX COMPLET 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()