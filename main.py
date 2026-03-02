import random
import asyncio
import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN non défini")

# ================= DATABASE =================
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 10000,
    total_profit INTEGER DEFAULT 0
)
""")
conn.commit()

# ================= UTILS =================
def get_user(user_id):
    cursor.execute("SELECT balance, total_profit FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 10000, 0

    return user

def update_user(user_id, balance, profit):
    cursor.execute("UPDATE users SET balance=?, total_profit=? WHERE user_id=?",
                   (balance, profit, user_id))
    conn.commit()

# ================= KEYBOARDS =================
def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Jouer", callback_data="play")],
        [InlineKeyboardButton("⚡ Auto Mode", callback_data="auto")],
        [InlineKeyboardButton("🏆 Classement", callback_data="leaderboard")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ])

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 MENU", callback_data="menu")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 *CRASH PRO MAX*\n\nClique MENU 👇",
        parse_mode="Markdown",
        reply_markup=back_menu()
    )

# ================= GAME =================
async def play_round(message, user_id):
    balance, total_profit = get_user(user_id)

    bet = 500
    if balance < bet:
        await message.edit_text("❌ Solde insuffisant", reply_markup=back_menu())
        return

    multiplier = round(random.uniform(1.0, 7.0), 2)

    await message.edit_text("🚀 1.00x")

    live = 1.0
    steps = min(int((multiplier - 1) / 0.4), 7)

    for _ in range(steps):
        await asyncio.sleep(0.4)
        live += 0.4
        try:
            await message.edit_text(f"🚀 {round(live,2)}x")
        except:
            break

    await asyncio.sleep(0.5)

    if multiplier >= 2:
        gain = bet
        balance += gain
        total_profit += gain
        result = f"💰 GAIN {gain} FCFA"
    else:
        balance -= bet
        total_profit -= bet
        result = f"💥 PERTE {bet} FCFA"

    update_user(user_id, balance, total_profit)

    final = (
        "━━━━━━━━━━━━━━━\n"
        f"💥 *CRASH à {multiplier}x*\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"{result}\n\n"
        f"💰 Solde: {balance} FCFA\n"
        "━━━━━━━━━━━━━━━"
    )

    await message.edit_text(final, parse_mode="Markdown", reply_markup=back_menu())

# ================= HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    balance, profit = get_user(user_id)

    if query.data == "menu":
        await query.edit_message_text(
            "💎 *CRASH PRO MAX*\n\nChoisis 👇",
            parse_mode="Markdown",
            reply_markup=menu_keyboard()
        )

    elif query.data == "play":
        msg = await query.edit_message_text("🚀 Préparation...")
        await play_round(msg, user_id)

    elif query.data == "auto":
        msg = await query.edit_message_text("⚡ MODE AUTO ACTIVÉ (3 rounds)")
        for _ in range(3):
            await asyncio.sleep(5)
            await play_round(msg, user_id)

    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 *STATS*\n\n💰 Solde: {balance}\n📈 Profit total: {profit}",
            parse_mode="Markdown",
            reply_markup=back_menu()
        )

    elif query.data == "leaderboard":
        cursor.execute("SELECT user_id, total_profit FROM users ORDER BY total_profit DESC LIMIT 10")
        top = cursor.fetchall()

        text = "🏆 *TOP 10*\n\n"
        for i, (uid, prof) in enumerate(top, 1):
            text += f"{i}. {uid} → {prof} FCFA\n"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_menu())

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot PRO MAX lancé 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()