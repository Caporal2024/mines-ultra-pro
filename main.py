import random
import asyncio
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔐 COLLE TON TOKEN ENTRE LES GUILLEMETS
TOKEN = "PASTE_YOUR_TOKEN_HERE"

# ================= DATABASE =================
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 10000,
    total_profit INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    vip INTEGER DEFAULT 0
)
""")
conn.commit()

crash_history = []

# ================= UTILS =================
def get_user(user_id):
    cursor.execute("SELECT balance, total_profit, wins, losses, vip FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 10000, 0, 0, 0, 0

    return user

def update_user(user_id, balance, profit, wins, losses, vip):
    cursor.execute(
        "UPDATE users SET balance=?, total_profit=?, wins=?, losses=?, vip=? WHERE user_id=?",
        (balance, profit, wins, losses, vip, user_id)
    )
    conn.commit()

# ================= KEYBOARDS =================
def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Crash IA", callback_data="crash")],
        [InlineKeyboardButton("💣 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("💰 Dépôt +2000", callback_data="deposit")],
        [InlineKeyboardButton("💎 Activer VIP", callback_data="vip")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ])

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 MENU", callback_data="menu")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 CASINO PRO MAX\n\nClique MENU 👇",
        reply_markup=back_menu()
    )

# ================= CRASH =================
async def crash_game(message, user_id):
    balance, profit, wins, losses, vip = get_user(user_id)
    bet = max(int(balance * 0.02), 200)

    if balance < bet:
        await message.edit_text("❌ Solde insuffisant", reply_markup=back_menu())
        return

    multiplier = round(random.uniform(1.0, 7.0), 2)
    crash_history.append(multiplier)
    if len(crash_history) > 10:
        crash_history.pop(0)

    await message.edit_text("🚀 1.00x")
    live = 1.0

    while live < multiplier and live < 3:
        await asyncio.sleep(0.4)
        live += 0.4
        try:
            await message.edit_text(f"🚀 {round(live,2)}x")
        except:
            break

    await asyncio.sleep(0.5)
    auto_cashout = 2.0 if vip else 1.8

    if multiplier >= auto_cashout:
        gain = bet
        balance += gain
        profit += gain
        wins += 1
        result = f"💰 GAIN {gain} FCFA"
    else:
        balance -= bet
        profit -= bet
        losses += 1
        result = f"💥 PERTE {bet} FCFA"

    update_user(user_id, balance, profit, wins, losses, vip)

    history = " | ".join([f"{x}x" for x in crash_history])

    await message.edit_text(
        f"💥 Crash à {multiplier}x\n\n"
        f"{result}\n\n"
        f"💰 Solde: {balance}\n"
        f"📜 Historique: {history}",
        reply_markup=back_menu()
    )

# ================= MINES =================
async def mines_game(message, user_id):
    balance, profit, wins, losses, vip = get_user(user_id)
    bet = 500

    if balance < bet:
        await message.edit_text("❌ Solde insuffisant", reply_markup=back_menu())
        return

    mine_position = random.randint(1, 25)
    pick = random.randint(1, 25)

    if pick == mine_position:
        balance -= bet
        profit -= bet
        losses += 1
        result = "💣 BOOM ! Mine touchée"
    else:
        gain = bet
        balance += gain
        profit += gain
        wins += 1
        result = "💎 Case sécurisée → Gain"

    update_user(user_id, balance, profit, wins, losses, vip)

    await message.edit_text(
        f"{result}\n\n💰 Solde: {balance}",
        reply_markup=back_menu()
    )

# ================= HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "menu":
        await query.edit_message_text("🎰 CASINO PRO MAX\n\nChoisis 👇", reply_markup=menu_keyboard())

    elif query.data == "crash":
        msg = await query.edit_message_text("🚀 Préparation...")
        await crash_game(msg, user_id)

    elif query.data == "mines":
        msg = await query.edit_message_text("💣 Mines en cours...")
        await mines_game(msg, user_id)

    elif query.data == "deposit":
        balance, profit, wins, losses, vip = get_user(user_id)
        balance += 2000
        update_user(user_id, balance, profit, wins, losses, vip)
        await query.edit_message_text(f"💰 Dépôt ajouté\n\nSolde: {balance}", reply_markup=back_menu())

    elif query.data == "vip":
        balance, profit, wins, losses, vip = get_user(user_id)
        vip = 1
        update_user(user_id, balance, profit, wins, losses, vip)
        await query.edit_message_text("💎 VIP ACTIVÉ (Auto 2.0x)", reply_markup=back_menu())

    elif query.data == "stats":
        balance, profit, wins, losses, vip = get_user(user_id)
        total = wins + losses
        rate = (wins / total * 100) if total > 0 else 0

        await query.edit_message_text(
            f"📊 STATS\n\n"
            f"💰 Solde: {balance}\n"
            f"📈 Profit: {profit}\n"
            f"🏆 Victoires: {wins}\n"
            f"💥 Défaites: {losses}\n"
            f"📊 Taux: {round(rate,2)}%",
            reply_markup=back_menu()
        )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("BOT LANCÉ 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()