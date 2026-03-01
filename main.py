import random
import asyncio
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

START_BALANCE = 10000
BET_AMOUNT = 500
MAX_LOSS = -3000
PROFIT_TARGET = 4000

users = {}
ai_data = {}

# ======================
# INITIALISATION USER
# ======================

def init_user(user_id):
    if user_id not in users:
        users[user_id] = START_BALANCE
    if user_id not in ai_data:
        ai_data[user_id] = {
            "start_balance": START_BALANCE,
            "wins": 0,
            "losses": 0
        }

def ai_control(user_id):
    profit = users[user_id] - ai_data[user_id]["start_balance"]
    if profit <= MAX_LOSS:
        return "stop"
    if profit >= PROFIT_TARGET:
        return "target"
    return "ok"

# ======================
# MENU PRINCIPAL (GROS)
# ======================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("💣💣💣  MINES 3 LIVE  💣💣💣", callback_data="mines_3")],
        [InlineKeyboardButton("💣💣💣  MINES 5 LIVE  💣💣💣", callback_data="mines_5")],
        [InlineKeyboardButton("💣💣💣  MINES 7 LIVE  💣💣💣", callback_data="mines_7")],
        [InlineKeyboardButton("🚀🚀🚀  LUCKY JET LIVE  🚀🚀🚀", callback_data="jet")],
        [InlineKeyboardButton("🧠🧠🧠  GESTION CAPITAL IA  🧠🧠🧠", callback_data="capital")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ======================
# START
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    init_user(user_id)

    await update.message.reply_text(
        f"🎰 CASINO LIVE PRO\n\n💰 Solde: {users[user_id]}",
        reply_markup=main_menu()
    )

# ======================
# MINES 5x5 NUMÉROTÉ
# ======================

def generate_grid(game):
    keyboard = []
    for row in range(5):
        row_buttons = []
        for col in range(5):
            index = row * 5 + col
            number = index + 1

            if index in game["revealed"]:
                row_buttons.append(InlineKeyboardButton("⭐", callback_data="ignore"))
            else:
                row_buttons.append(InlineKeyboardButton(str(number), callback_data=f"cell_{index}"))

        keyboard.append(row_buttons)
    return InlineKeyboardMarkup(keyboard)

async def start_mines(update: Update, context: ContextTypes.DEFAULT_TYPE, mines_count):
    query = update.callback_query
    user_id = query.from_user.id
    init_user(user_id)

    if ai_control(user_id) != "ok":
        await query.answer("🛑 Limite IA atteinte")
        return

    bombs = random.sample(range(25), mines_count)
    context.user_data["mines"] = {
        "bombs": bombs,
        "revealed": []
    }

    await query.edit_message_text(
        f"💣 Mines 5x5 LIVE ({mines_count} bombes)\nClique un numéro 👇",
        reply_markup=generate_grid(context.user_data["mines"])
    )

async def handle_mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if "mines" not in context.user_data:
        return

    game = context.user_data["mines"]
    index = int(query.data.split("_")[1])

    if index in game["bombs"]:
        users[user_id] -= BET_AMOUNT
        ai_data[user_id]["losses"] += 1

        await query.edit_message_text(
            f"💥 BOOM ! Bombe explosée\n💰 Solde: {users[user_id]}",
            reply_markup=main_menu()
        )
        context.user_data.pop("mines")
    else:
        users[user_id] += 300
        ai_data[user_id]["wins"] += 1
        game["revealed"].append(index)

        await query.edit_message_reply_markup(
            reply_markup=generate_grid(game)
        )

# ======================
# LUCKY JET LIVE RAPIDE
# ======================

async def start_jet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    init_user(user_id)

    if ai_control(user_id) != "ok":
        await query.answer("🛑 Limite IA atteinte")
        return

    crash = round(random.uniform(1.5, 4.0), 2)
    multiplier = 1.0

    msg = await query.edit_message_text("🚀 LUCKY JET LIVE\n")

    while multiplier < crash:
        multiplier += 0.6
        await msg.edit_text(f"🚀 x{round(multiplier,2)}")
        await asyncio.sleep(0.2)

    users[user_id] -= BET_AMOUNT
    ai_data[user_id]["losses"] += 1

    await msg.edit_text(
        f"💥 CRASH à x{crash}\n💰 Solde: {users[user_id]}",
        reply_markup=main_menu()
    )

# ======================
# CAPITAL IA
# ======================

async def capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    init_user(user_id)

    profit = users[user_id] - ai_data[user_id]["start_balance"]

    await query.edit_message_text(
        f"""🧠 GESTION CAPITAL IA

💰 Solde: {users[user_id]}
📈 Profit: {profit}
✅ Victoires: {ai_data[user_id]['wins']}
❌ Pertes: {ai_data[user_id]['losses']}

Stop Loss: {MAX_LOSS}
Objectif: {PROFIT_TARGET}
""",
        reply_markup=main_menu()
    )

# ======================
# MAIN
# ======================

def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        print("BOT_TOKEN non défini")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(lambda u,c: start_mines(u,c,3), pattern="mines_3"))
    app.add_handler(CallbackQueryHandler(lambda u,c: start_mines(u,c,5), pattern="mines_5"))
    app.add_handler(CallbackQueryHandler(lambda u,c: start_mines(u,c,7), pattern="mines_7"))
    app.add_handler(CallbackQueryHandler(start_jet, pattern="jet"))
    app.add_handler(CallbackQueryHandler(capital, pattern="capital"))
    app.add_handler(CallbackQueryHandler(handle_mines, pattern="cell_"))

    app.run_polling()

if __name__ == "__main__":
    main()