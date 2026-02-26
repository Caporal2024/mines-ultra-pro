import os
import random
import hashlib
import sqlite3
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("TOKEN")  # Mets ton token Telegram

# ================= DATABASE =================

conn = sqlite3.connect("mines.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    score INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    gain INTEGER,
    timestamp INTEGER
)
""")

conn.commit()

# ================= UTILITIES =================

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

def generate_board_from_seed(server_seed, client_seed, nonce):
    combined = f"{server_seed}:{client_seed}:{nonce}"
    hash_result = hashlib.sha256(combined.encode()).hexdigest()

    random.seed(hash_result)
    mines = random.sample(range(25), 3)

    return mines, hash_result

def calculate_multiplier(revealed):
    base = 1.07
    return round(base ** revealed, 2)

def build_grid():
    keyboard = []
    for i in range(5):
        row = []
        for j in range(5):
            index = i * 5 + j
            row.append(
                InlineKeyboardButton("⬜", callback_data=f"cell_{index}")
            )
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_user(user_id)

    keyboard = [
        [InlineKeyboardButton("🎮 Jouer", callback_data="play")],
        [InlineKeyboardButton("🔐 Provably Fair", callback_data="provably")],
        [InlineKeyboardButton("🧮 Vérifier Hash", callback_data="verify")],
        [InlineKeyboardButton("📈 Historique", callback_data="history")]
    ]

    await update.message.reply_text(
        "💎 MINES SIMULATION BOT 💎\n\n"
        "Choisis une option :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BUTTON HANDLER =================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    get_user(user_id)

    # PLAY
    if query.data == "play":
        server_seed = str(random.random())
        client_seed = str(user_id)
        nonce = int(time.time())

        mines, hash_result = generate_board_from_seed(server_seed, client_seed, nonce)

        context.user_data["mines"] = mines
        context.user_data["revealed"] = 0
        context.user_data["server_seed"] = server_seed
        context.user_data["client_seed"] = client_seed
        context.user_data["nonce"] = nonce
        context.user_data["hash"] = hash_result

        await query.edit_message_text(
            "💣 Partie commencée !\n\n"
            f"Hash (preuve) :\n{hash_result}\n\n"
            "Choisis une case :",
            reply_markup=build_grid()
        )

    # CLICK CELL
    elif query.data.startswith("cell_"):
        index = int(query.data.split("_")[1])
        mines = context.user_data.get("mines", [])
        revealed = context.user_data.get("revealed", 0)

        if index in mines:
            await query.edit_message_text(
                "💥 BOOM ! Mine touchée.\n\n"
                "Server Seed révélé :\n"
                f"{context.user_data['server_seed']}"
            )
        else:
            revealed += 1
            context.user_data["revealed"] = revealed

            multiplier = calculate_multiplier(revealed)
            gain = int(10 * multiplier)

            cursor.execute(
                "UPDATE users SET score = score + ? WHERE user_id=?",
                (gain, user_id)
            )
            cursor.execute(
                "INSERT INTO history (user_id, gain, timestamp) VALUES (?,?,?)",
                (user_id, gain, int(time.time()))
            )
            conn.commit()

            await query.edit_message_text(
                f"✅ Safe !\n"
                f"💎 Gain : {gain}\n"
                f"⚡ Multiplicateur : x{multiplier}"
            )

    # PROVABLY FAIR EXPLANATION
    elif query.data == "provably":
        await query.edit_message_text(
            "🔐 PROVABLY FAIR\n\n"
            "1️⃣ Le serveur génère un Server Seed secret\n"
            "2️⃣ Le hash SHA256 est affiché\n"
            "3️⃣ Après la partie, le seed est révélé\n"
            "4️⃣ Tu peux recalculer le hash pour vérifier"
        )

    # VERIFY HASH
    elif query.data == "verify":
        await query.edit_message_text(
            "🧮 Pour vérifier un hash :\n\n"
            "Format :\n"
            "/check server_seed client_seed nonce hash"
        )

    # HISTORY
    elif query.data == "history":
        cursor.execute(
            "SELECT gain FROM history WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (user_id,)
        )
        rows = cursor.fetchall()

        if not rows:
            await query.edit_message_text("Aucun historique.")
            return

        message = "📈 Derniers gains :\n\n"
        for i, row in enumerate(rows, 1):
            message += f"{i}. +{row[0]} pts\n"

        await query.edit_message_text(message)

# ================= HASH CHECK COMMAND =================

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        server_seed = context.args[0]
        client_seed = context.args[1]
        nonce = context.args[2]
        given_hash = context.args[3]

        combined = f"{server_seed}:{client_seed}:{nonce}"
        calculated = hashlib.sha256(combined.encode()).hexdigest()

        if calculated == given_hash:
            await update.message.reply_text("✅ Hash valide")
        else:
            await update.message.reply_text("❌ Hash invalide")

    except:
        await update.message.reply_text("Format incorrect.")

# ================= RUN =================

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()