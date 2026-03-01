import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =====================
# CONFIG IA CAPITAL
# =====================

START_BALANCE = 10000
BET_AMOUNT = 500
MAX_LOSS = -3000
PROFIT_TARGET = 4000

users = {}
ai_data = {}

# =====================
# INIT USER
# =====================

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
    init_user(user_id)
    current = users[user_id]
    start = ai_data[user_id]["start_balance"]
    profit = current - start

    if profit <= MAX_LOSS:
        return "stop_loss"

    if profit >= PROFIT_TARGET:
        return "target"

    return "ok"

# =====================
# MENU PRINCIPAL
# =====================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("💣 Mines 3 LIVE", callback_data="mines_3"),
            InlineKeyboardButton("💣 Mines 5 LIVE", callback_data="mines_5"),
        ],
        [
            InlineKeyboardButton("💣 Mines 7 LIVE", callback_data="mines_7"),
        ],
        [
            InlineKeyboardButton("🚀 Lucky Jet LIVE", callback_data="jet"),
        ],
        [
            InlineKeyboardButton("🧠 Gestion Capital", callback_data="capital"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# =====================
# START
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    init_user(user_id)

    await update.message.reply_text(
        f"🎰 CASINO LIVE PRO\n\n💰 Solde: {users[user_id]}",
        reply_markup=main_menu()
    )

# =====================
# MINES
# =====================

def generate_grid(game):
    keyboard = []
    for i in range(5):
        row = []
        for j in range(5):
            index = i * 5 + j
            if index in game["revealed"]:
                row.append(InlineKeyboardButton("⭐", callback_data="x"))
            else:
                row.append(InlineKeyboardButton("⬜", callback_data=f"cell_{index}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start_mines(update: Update, context: ContextTypes.DEFAULT_TYPE, mines_count):
    query = update.callback_query
    user_id = query.from_user.id

    if ai_control(user_id) != "ok":
        await query.answer("🛑 Gestion IA bloque le jeu")
        return

    bombs = random.sample(range(25), mines_count)

    context.user_data["mines"] = {
        "bombs": bombs,
        "revealed": [],
        "mines_count": mines_count
    }

    await query.edit_message_text(
        f"💣 Mines LIVE ({mines_count})\nSolde: {users[user_id]}",
        reply_markup=generate_grid(context.user_data["mines"])
    )

async def handle_mines_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if "mines" not in context.user_data:
        return

    game = context.user_data["mines"]

    if data.startswith("cell_"):
        index = int(data.split("_")[1])

        if index in game["bombs"]:
            users[user_id] -= BET_AMOUNT
            ai_data[user_id]["losses"] += 1

            await query.edit_message_text(
                f"💥 BOOM !\n💰 Solde: {users[user_id]}",
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

# =====================
# LUCKY JET
# =====================

async def start_jet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if ai_control(user_id) != "ok":
        await query.answer("🛑 Gestion IA bloque le jeu")
        return

    crash = round(random.uniform(1.5, 5.0), 2)
    multiplier = 1.0

    message = await query.edit_message_text("🚀 Lucky Jet LIVE\n")

    while multiplier < crash:
        multiplier += 0.3
        await message.edit_text(f"🚀 x{round(multiplier,2)}")
        await asyncio.sleep(0.4)

    users[user_id] -= BET_AMOUNT
    ai_data[user_id]["losses"] += 1

    await message.edit_text(
        f"💥 CRASH à x{crash}\n💰 Solde: {users[user_id]}",
        reply_markup=main_menu()
    )

# =====================
# CAPITAL INFO
# =====================

async def capital_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    init_user(user_id)

    profit = users[user_id] - ai_data[user_id]["start_balance"]

    await query.edit_message_text(
        f"""🧠 Gestion Capital

💰 Solde: {users[user_id]}
📈 Profit: {profit}
✅ Victoires: {ai_data[user_id]["wins"]}
❌ Pertes: {ai_data[user_id]["losses"]}

Stop Loss: {MAX_LOSS}
Objectif: {PROFIT_TARGET}
""",
        reply_markup=main_menu()
    )

# =====================
# MAIN
# =====================

def main():
    app = ApplicationBuilder().token("YOUR_TOKEN_HERE").build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(lambda u,c: start_mines(u,c,3), pattern="mines_3"))
    app.add_handler(CallbackQueryHandler(lambda u,c: start_mines(u,c,5), pattern="mines_5"))
    app.add_handler(CallbackQueryHandler(lambda u,c: start_mines(u,c,7), pattern="mines_7"))

    app.add_handler(CallbackQueryHandler(start_jet, pattern="jet"))
    app.add_handler(CallbackQueryHandler(capital_info, pattern="capital"))

    app.add_handler(CallbackQueryHandler(handle_mines_click, pattern="cell_"))

    app.run_polling()

if __name__ == "__main__":
    main()