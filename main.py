import os
import json
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

# ================= LOAD / SAVE =================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

users = load_data()

# ================= GAME STATE =================

current_round = {
    "running": False,
    "multiplier": 1.0,
    "crash_point": 0,
    "players": {}
}

crash_history = []

LOSS_LIMIT = -3000
PROFIT_TARGET = 4000

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "wins": 0,
            "losses": 0,
            "profit": 0
        }
        save_data()

    await update.message.reply_text(
        "🎮 CRASH PRO SIMULATION\n\n"
        f"💰 Solde: {users[user_id]['balance']} FCFA\n\n"
        "Commandes:\n"
        "/play 500\n"
        "/stats\n"
        "/history"
    )

# ================= PLAY =================

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if len(context.args) == 0:
        await update.message.reply_text("Utilise: /play montant")
        return

    bet = int(context.args[0])

    if users[user_id]["balance"] < bet:
        await update.message.reply_text("❌ Solde insuffisant.")
        return

    if users[user_id]["profit"] <= LOSS_LIMIT:
        await update.message.reply_text("🛑 Limite de perte atteinte.")
        return

    if users[user_id]["profit"] >= PROFIT_TARGET:
        await update.message.reply_text("🎯 Objectif de profit atteint.")
        return

    users[user_id]["balance"] -= bet
    users[user_id]["profit"] -= bet

    current_round["players"][user_id] = bet

    if not current_round["running"]:
        current_round["running"] = True
        current_round["multiplier"] = 1.0
        current_round["crash_point"] = round(random.expovariate(1/2), 2)
        context.application.create_task(run_round(update))

    save_data()
    await update.message.reply_text("✅ Pari enregistré.")

# ================= RUN ROUND =================

async def run_round(update):
    message = await update.message.reply_text("🚀 1.00x")

    while current_round["multiplier"] < current_round["crash_point"]:
        await asyncio.sleep(0.5)

        current_round["multiplier"] *= 1.08

        keyboard = [[InlineKeyboardButton("💜 CASHOUT", callback_data="cashout")]]

        try:
            await message.edit_text(
                f"🚀 <b>{current_round['multiplier']:.2f}x</b>",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
        except:
            pass

    crash_value = round(current_round["crash_point"], 2)

    crash_history.insert(0, crash_value)
    if len(crash_history) > 15:
        crash_history.pop()

    await message.edit_text(
        f"💥 CRASH à {crash_value}x\n\n"
        f"📜 Historique:\n"
        + " | ".join([f"{x}x" for x in crash_history])
    )

    for user_id in list(current_round["players"].keys()):
        users[user_id]["losses"] += 1

    current_round["players"].clear()
    current_round["running"] = False
    save_data()

    await asyncio.sleep(60)

# ================= CASHOUT =================

async def cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)

    if user_id not in current_round["players"]:
        await query.answer("Pas dans le round.")
        return

    bet = current_round["players"].pop(user_id)
    gain = int(bet * current_round["multiplier"])

    users[user_id]["balance"] += gain
    users[user_id]["profit"] += gain
    users[user_id]["wins"] += 1

    save_data()
    await query.answer(f"💰 +{gain} FCFA")

# ================= STATS =================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = users[user_id]

    await update.message.reply_text(
        "📊 STATS\n\n"
        f"💰 Solde: {data['balance']}\n"
        f"📈 Profit: {data['profit']}\n"
        f"✅ Wins: {data['wins']}\n"
        f"❌ Losses: {data['losses']}"
    )

# ================= HISTORY =================

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not crash_history:
        await update.message.reply_text("Aucun historique.")
        return

    await update.message.reply_text(
        "📜 Derniers Crash:\n\n" +
        " | ".join([f"{x}x" for x in crash_history])
    )

# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CallbackQueryHandler(cashout, pattern="cashout"))

    print("🔥 Crash PRO Simulation lancée")
    app.run_polling()

if __name__ == "__main__":
    main()