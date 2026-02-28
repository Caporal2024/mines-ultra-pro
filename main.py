import os
import random
import asyncio
import threading
import sqlite3
from flask import Flask, render_template
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 8080))
ADMIN_ID = 8094967191

if not TOKEN:
    raise ValueError("TOKEN manquant")

# ================= WEB SERVER =================
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "CASINO PRO MAX ONLINE 💎"

@app_web.route("/casino")
def casino():
    return render_template("index.html")

def run_web():
    app_web.run(host="0.0.0.0", port=PORT)

# ================= DATABASE =================
conn = sqlite3.connect("casino.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 1000,
    vip INTEGER DEFAULT 0
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT balance, vip FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()

    if not data:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return {"balance": 1000, "vip": 0}

    return {"balance": data[0], "vip": data[1]}

def update_balance(user_id, new_balance):
    cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    keyboard = [
        [
            InlineKeyboardButton(
                "🎰 OUVRIR CASINO",
                web_app=WebAppInfo(url="https://TON-LIEN-RAILWAY.up.railway.app/casino")
            )
        ]
    ]

    await update.message.reply_text(
        f"""
━━━━━━━━━━━━━━━
🎰 CASINO PRO MAX
━━━━━━━━━━━━━━━
💰 Solde : {user['balance']} FCFA
🏆 VIP : {'Oui' if user['vip'] else 'Non'}

Commandes :
/luckyjet 200 2
/mines 100
/stats
━━━━━━━━━━━━━━━
""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= STATS =================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"💰 Solde actuel : {user['balance']} FCFA"
    )

# ================= LUCKYJET AUTO =================
async def luckyjet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if len(context.args) < 1:
        await update.message.reply_text("Utilise: /luckyjet montant auto")
        return

    bet = int(context.args[0])
    auto = float(context.args[1]) if len(context.args) > 1 else None

    if bet > user["balance"]:
        await update.message.reply_text("❌ Solde insuffisant")
        return

    update_balance(user_id, user["balance"] - bet)

    crash = random.uniform(1.2, 4.0) if user["vip"] else random.uniform(1.1, 3.0)
    multi = 1.00

    msg = await update.message.reply_text("🚀 x1.00")

    while multi < crash:
        await asyncio.sleep(0.4)
        multi += 0.05

        if auto and multi >= auto:
            gain = int(bet * auto)
            update_balance(user_id, get_user(user_id)["balance"] + gain)
            await msg.edit_text(f"🎯 AUTO CASHOUT x{auto}\n💰 Gain : {gain}")
            return

        await msg.edit_text(f"🚀 x{multi:.2f}")

    await msg.edit_text(f"💥 CRASH à x{crash:.2f}")

# ================= MINES =================
def generate_board():
    board = ["💎"] * 25
    for pos in random.sample(range(25), 5):
        board[pos] = "💣"
    return board

async def mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not context.args:
        await update.message.reply_text("Utilise: /mines montant")
        return

    bet = int(context.args[0])

    if bet > user["balance"]:
        await update.message.reply_text("❌ Solde insuffisant")
        return

    update_balance(user_id, user["balance"] - bet)

    context.user_data["board"] = generate_board()
    context.user_data["revealed"] = ["⬜"] * 25
    context.user_data["bet"] = bet

    await show_mines(update, context)

async def show_mines(update_or_query, context):
    revealed = context.user_data["revealed"]

    keyboard = []
    for i in range(5):
        row = []
        for j in range(5):
            row.append(
                InlineKeyboardButton(
                    revealed[i*5+j],
                    callback_data=f"cell_{i*5+j}"
                )
            )
        keyboard.append(row)

    markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_query, "message"):
        await update_or_query.message.reply_text(
            "💣 MINES 5x5 PRO",
            reply_markup=markup
        )
    else:
        await update_or_query.edit_message_reply_markup(reply_markup=markup)

async def handle_mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    index = int(query.data.split("_")[1])
    board = context.user_data["board"]
    revealed = context.user_data["revealed"]
    bet = context.user_data["bet"]

    user_id = query.from_user.id
    user = get_user(user_id)

    if board[index] == "💣":
        revealed[index] = "💣"
        await query.edit_message_text("💥 BOOM ! Partie terminée.")
        return

    revealed[index] = "💎"
    gain = int(bet * 1.3)
    update_balance(user_id, user["balance"] + gain)

    await show_mines(query, context)

# ================= VIP ADMIN =================
async def givevip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    cursor.execute("UPDATE users SET vip=1 WHERE user_id=?", (user_id,))
    conn.commit()

    await update.message.reply_text("👑 VIP activé")

# ================= MAIN =================
def main():
    threading.Thread(target=run_web).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("luckyjet", luckyjet))
    app.add_handler(CommandHandler("mines", mines))
    app.add_handler(CommandHandler("givevip", givevip))
    app.add_handler(CallbackQueryHandler(handle_mine, pattern="^cell_"))

    app.run_polling()

if __name__ == "__main__":
    main()