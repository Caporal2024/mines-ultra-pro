import os
import random
import time
import sqlite3
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("TOKEN")

# ================= DATABASE =================

conn = sqlite3.connect("mines.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    score INTEGER DEFAULT 0,
    games INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    multiplier REAL DEFAULT 1.0,
    last_bonus INTEGER DEFAULT 0,
    daily_mission INTEGER DEFAULT 0,
    mission_progress INTEGER DEFAULT 0
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

VIP_USERS = [8094967191]

# ================= UTILITIES =================

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    return user

def create_board():
    safe_zone = random.randint(0, 24)
    mines = random.sample([x for x in range(25) if x != safe_zone], 3)
    return mines

def build_grid():
    keyboard = []
    for i in range(5):
        row = []
        for j in range(5):
            index = i * 5 + j
            row.append(InlineKeyboardButton("⬜", callback_data=f"cell_{index}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_user(user_id)

    status = "👑 VIP" if user_id in VIP_USERS else "👤 STANDARD"

    keyboard = [
        [InlineKeyboardButton("🎮 Jouer", callback_data="play")],
        [InlineKeyboardButton("🏆 Classement", callback_data="leaderboard")],
        [InlineKeyboardButton("🎁 Bonus", callback_data="bonus")],
        [InlineKeyboardButton("🎯 Missions", callback_data="missions")],
        [InlineKeyboardButton("📈 Progression", callback_data="progress")],
    ]

    await update.message.reply_text(
        "╔════════════════════╗\n"
        " 💎 MINES ULTRA PRO MAX 💎\n"
        "╚════════════════════╝\n\n"
        f"Statut : {status}\n\n"
        "Choisissez une option 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ================= BUTTON HANDLER =================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    get_user(user_id)

    # PLAY
    if query.data == "play":
        context.user_data["board"] = create_board()
        await query.edit_message_text(
            "💣 Partie commencée ! Choisis une case :",
            reply_markup=build_grid()
        )

    # CELL CLICK
    elif query.data.startswith("cell_"):
        index = int(query.data.split("_")[1])
        board = context.user_data.get("board", [])

        if index in board:
            cursor.execute(
                "UPDATE users SET games=games+1, multiplier=1.0 WHERE user_id=?",
                (user_id,)
            )
            conn.commit()
            await query.edit_message_text("💥 BOOM ! Mine touchée.")
        else:
            cursor.execute("SELECT multiplier FROM users WHERE user_id=?", (user_id,))
            multiplier = cursor.fetchone()[0] + 0.2
            gain = int(10 * multiplier)

            cursor.execute("""
                UPDATE users
                SET score=score+?,
                    multiplier=?,
                    wins=wins+1
                WHERE user_id=?
            """, (gain, multiplier, user_id))

            cursor.execute(
                "INSERT INTO history (user_id, gain, timestamp) VALUES (?,?,?)",
                (user_id, gain, int(time.time()))
            )

            conn.commit()

            await query.edit_message_text(
                f"✅ Safe !\n"
                f"💎 Gain : {gain}\n"
                f"⚡ Multiplicateur : x{multiplier:.1f}"
            )

    # LEADERBOARD
    elif query.data == "leaderboard":
        cursor.execute(
            "SELECT user_id, score FROM users ORDER BY score DESC LIMIT 10"
        )
        players = cursor.fetchall()

        medals = ["🥇", "🥈", "🥉"]
        message = "🏆 CLASSEMENT 🏆\n\n"

        for i, (uid, score) in enumerate(players):
            medal = medals[i] if i < 3 else "⭐"
            vip = " 👑" if uid in VIP_USERS else ""
            message += f"{medal} {uid} — {score} pts{vip}\n"

        await query.edit_message_text(message)

    # BONUS
    elif query.data == "bonus":
        cursor.execute("SELECT last_bonus FROM users WHERE user_id=?", (user_id,))
        last = cursor.fetchone()[0]
        now = int(time.time())

        if now - last >= 86400:
            bonus = 50
            cursor.execute("""
                UPDATE users
                SET score=score+?, last_bonus=?
                WHERE user_id=?
            """, (bonus, now, user_id))
            conn.commit()
            await query.edit_message_text(
                f"🎁 Bonus reçu ! +{bonus} points"
            )
        else:
            await query.edit_message_text("⏳ Bonus déjà utilisé aujourd'hui.")

    # MISSIONS
    elif query.data == "missions":
        cursor.execute(
            "SELECT daily_mission, mission_progress FROM users WHERE user_id=?",
            (user_id,)
        )
        mission, progress = cursor.fetchone()

        if mission == 0:
            mission = random.randint(3, 7)
            cursor.execute("""
                UPDATE users
                SET daily_mission=?, mission_progress=0
                WHERE user_id=?
            """, (mission, user_id))
            conn.commit()

        await query.edit_message_text(
            f"🎯 Mission : Jouer {mission} parties\n"
            f"Progression : {progress}/{mission}"
        )

    # PROGRESS
    elif query.data == "progress":
        cursor.execute(
            "SELECT gain FROM history WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (user_id,)
        )
        rows = cursor.fetchall()

        if not rows:
            await query.edit_message_text("📉 Aucun historique.")
            return

        message = "📈 Progression récente\n\n"
        for i, row in enumerate(reversed(rows), start=1):
            message += f"Partie {i} ➜ +{row[0]} pts\n"

        await query.edit_message_text(message)

# ================= RUN =================

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()