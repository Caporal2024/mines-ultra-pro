 import os
TOKEN = os.getenv("TOKEN"import sqlite3
import random
import time
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# ==============================
# CONFIGURATION
# ==============================

TOKEN = "TON_TOKEN_ICI"
ADMIN_ID = 8094967191   # Mets ton ID Telegram ici
MAX_GAIN = 10000
MINES_COUNT = 3
BET_AMOUNT = 200

# ==============================
# LOGGING
# ==============================

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================
# DATABASE
# ==============================

conn = sqlite3.connect("casino.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 10000,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0
)
""")
conn.commit()

# ==============================
# MEMORY
# ==============================

games = {}
last_click = {}

# ==============================
# UTIL FUNCTIONS
# ==============================

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return get_user(user_id)

    return user

def update_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def update_stats(user_id, win=False):
    if win:
        cursor.execute("UPDATE users SET wins = wins + 1 WHERE user_id=?", (user_id,))
    else:
        cursor.execute("UPDATE users SET losses = losses + 1 WHERE user_id=?", (user_id,))
    conn.commit()

def is_spamming(user_id):
    now = time.time()
    if user_id in last_click:
        if now - last_click[user_id] < 1:
            return True
    last_click[user_id] = now
    return False

# ==============================
# GRID
# ==============================

def generate_grid(game=None, reveal_all=False):
    keyboard = []

    for row in range(5):
        line = []
        for col in range(5):
            index = row * 5 + col

            if game:
                if reveal_all:
                    if index in game["mines"]:
                        symbol = "💣"
                    elif index in game["revealed"]:
                        symbol = "🟩"
                    else:
                        symbol = "⬜"
                else:
                    if index in game["revealed"]:
                        symbol = "🟩"
                    else:
                        symbol = "⬜"
            else:
                symbol = "⬜"

            line.append(
                InlineKeyboardButton(symbol, callback_data=f"cell_{index}")
            )

        keyboard.append(line)

    keyboard.append([InlineKeyboardButton("💰 Cashout", callback_data="cashout")])

    return InlineKeyboardMarkup(keyboard)

# ==============================
# COMMANDS
# ==============================

async def start(update, context):
    user_id = update.effective_user.id
    user = get_user(user_id)

    text = f"""
━━━━━━━━━━━━━━
💎 MINES 5x5 PRO
━━━━━━━━━━━━━━
💰 Solde : {user[1]} FCFA
🏆 Victoires : {user[2]}
💣 Défaites : {user[3]}
━━━━━━━━━━━━━━
"""

    keyboard = [
        [InlineKeyboardButton("🎮 Jouer", callback_data="play")]
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_stats(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(balance) FROM users")
    total_balance = cursor.fetchone()[0]

    await update.message.reply_text(
        f"👑 ADMIN PANEL\n\n"
        f"👥 Utilisateurs : {total_users}\n"
        f"💰 Total soldes : {total_balance} FCFA"
    )

# ==============================
# GAME LOGIC
# ==============================

async def start_game(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)

    if user_id in games:
        await query.answer("⚠️ Partie déjà en cours", show_alert=True)
        return

    if user[1] < BET_AMOUNT:
        await query.answer("❌ Solde insuffisant", show_alert=True)
        return

    update_balance(user_id, -BET_AMOUNT)

    mines = random.sample(range(25), MINES_COUNT)

    games[user_id] = {
        "bet": BET_AMOUNT,
        "mines": mines,
        "revealed": []
    }

    logging.info(f"User {user_id} started game")

    await query.edit_message_text(
        "🎮 Partie lancée\nClique sur une case",
        reply_markup=generate_grid(games[user_id])
    )

async def handle_click(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in games:
        return

    if is_spamming(user_id):
        logging.warning(f"Spam detected from {user_id}")
        await query.answer("⏳ Trop rapide !", show_alert=True)
        return

    game = games[user_id]
    data = query.data

    if data.startswith("cell_"):
        index = int(data.split("_")[1])

        if index in game["revealed"]:
            return

        if index in game["mines"]:
            update_stats(user_id, win=False)
            logging.info(f"User {user_id} lost")
            await query.edit_message_text(
                "💥 BOOM ! Perdu.",
                reply_markup=generate_grid(game, reveal_all=True)
            )
            del games[user_id]
            return

        game["revealed"].append(index)

        total_cells = 25
        safe_cells = total_cells - MINES_COUNT
        revealed = len(game["revealed"])

        multiplier = safe_cells / (safe_cells - revealed)
        gain = int(game["bet"] * multiplier)

        if gain > MAX_GAIN:
            gain = MAX_GAIN

        await query.edit_message_text(
            f"""
💎 MINES 5x5 PRO
━━━━━━━━━━━━━━
💰 Mise : {game['bet']} FCFA
📈 Multiplicateur : x{multiplier:.2f}
💵 Gain potentiel : {gain} FCFA
━━━━━━━━━━━━━━
""",
            reply_markup=generate_grid(game)
        )

    elif data == "cashout":

        if len(game["revealed"]) == 0:
            await query.answer("⚠️ Clique au moins une case", show_alert=True)
            return

        total_cells = 25
        safe_cells = total_cells - MINES_COUNT
        revealed = len(game["revealed"])

        multiplier = safe_cells / (safe_cells - revealed)
        gain = int(game["bet"] * multiplier)

        if gain > MAX_GAIN:
            gain = MAX_GAIN

        update_balance(user_id, gain)
        update_stats(user_id, win=True)

        logging.info(f"User {user_id} won {gain}")

        del games[user_id]

        await query.edit_message_text(f"💰 Cashout réussi\nGain : {gain} FCFA")

# ==============================
# MAIN
# ==============================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", admin_stats))
app.add_handler(CallbackQueryHandler(start_game, pattern="play"))
app.add_handler(CallbackQueryHandler(handle_click))

app.run_polling()