import logging
import random
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "TON_TOKEN_ICI"

# ---------------- DATABASE ----------------

conn = sqlite3.connect("casino.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL,
    wins INTEGER,
    losses INTEGER
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def create_user(user_id):
    cursor.execute("INSERT INTO users VALUES (?, 10000, 0, 0)")
    conn.commit()

def update_user(user_id, balance, wins, losses):
    cursor.execute(
        "UPDATE users SET balance=?, wins=?, losses=? WHERE user_id=?",
        (balance, wins, losses, user_id)
    )
    conn.commit()

# ---------------- START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not get_user(user_id):
        create_user(user_id)

    keyboard = [
        [InlineKeyboardButton("🎰 Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("💣 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("📊 Balance", callback_data="balance")]
    ]

    await update.message.reply_text(
        "🎮 Bienvenue dans ton Casino Pro !",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- LUCKY JET ----------------

def play_lucky(bet):
    crash = round(random.uniform(1.0, 5.0), 2)
    auto_cashout = 2.0

    if auto_cashout <= crash:
        profit = bet * auto_cashout - bet
        return True, round(profit, 2), crash
    else:
        return False, -bet, crash

# ---------------- MINES ----------------

def play_mines(bet):
    chance = random.randint(1, 5)
    if chance == 1:
        return False, -bet
    else:
        return True, bet * 0.5

# ---------------- BUTTONS ----------------

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    user = get_user(user_id)
    balance, wins, losses = user[1], user[2], user[3]

    bet = 1000

    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Solde: {balance}\n🏆 Wins: {wins}\n❌ Losses: {losses}"
        )

    elif query.data == "lucky":
        if balance < bet:
            await query.edit_message_text("❌ Solde insuffisant")
            return

        win, result, crash = play_lucky(bet)
        balance += result

        if win:
            wins += 1
            msg = f"🚀 Lucky Jet crash à {crash}x\n✅ Gain: {result}"
        else:
            losses += 1
            msg = f"💥 Crash à {crash}x\n❌ Perdu: {abs(result)}"

        update_user(user_id, balance, wins, losses)
        await query.edit_message_text(msg)

    elif query.data == "mines":
        if balance < bet:
            await query.edit_message_text("❌ Solde insuffisant")
            return

        win, result = play_mines(bet)
        balance += result

        if win:
            wins += 1
            msg = f"💎 Case safe !\n✅ Gain: {result}"
        else:
            losses += 1
            msg = f"💣 BOOM !\n❌ Perdu: {abs(result)}"

        update_user(user_id, balance, wins, losses)
        await query.edit_message_text(msg)

# ---------------- RUN ----------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot lancé...")
    app.run_polling()