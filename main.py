import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "TON_TOKEN_ICI"

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "wins": 0,
            "losses": 0,
            "game": None
        }
    return users[user_id]

# ==============================
# 🏠 MENU
# ==============================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 Mines", callback_data="mines")],
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("⚽ Penalty", callback_data="penalty")],
        [InlineKeyboardButton("💰 Solde", callback_data="balance")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎰 Casino Bot Pro Max",
        reply_markup=main_menu()
    )

async def show_balance(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(
        f"💰 Solde: {user['balance']} FCFA",
        reply_markup=main_menu()
    )

async def show_stats(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(
        f"📊 Victoires: {user['wins']}\n❌ Défaites: {user['losses']}",
        reply_markup=main_menu()
    )

# ==============================
# 🎮 MINES
# ==============================

MINES_COUNT = 5
GRID_SIZE = 5

def generate_mines():
    return random.sample(range(GRID_SIZE * GRID_SIZE), MINES_COUNT)

def build_mines_keyboard(revealed):
    keyboard = []
    for i in range(GRID_SIZE):
        row = []
        for j in range(GRID_SIZE):
            index = i * GRID_SIZE + j
            if index in revealed:
                row.append(InlineKeyboardButton("💎", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton("⬜", callback_data=f"cell_{index}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("💰 Cashout", callback_data="cashout")])
    return InlineKeyboardMarkup(keyboard)

async def start_mines(query, user):
    user["game"] = "mines"
    user["bet"] = 1000
    user["mines"] = generate_mines()
    user["revealed"] = []
    user["balance"] -= user["bet"]

    await query.edit_message_text(
        "💣 Mines 5x5\nMise: 1000 FCFA",
        reply_markup=build_mines_keyboard([])
    )

async def handle_mines(query, user, data):
    index = int(data.split("_")[1])

    if index in user["mines"]:
        user["losses"] += 1
        user["game"] = None
        await query.edit_message_text("💥 BOOM ! Perdu.", reply_markup=main_menu())
        return

    user["revealed"].append(index)
    multiplier = 1 + len(user["revealed"]) * 0.2

    await query.edit_message_text(
        f"💎 Safe\nMultiplicateur: x{round(multiplier,2)}",
        reply_markup=build_mines_keyboard(user["revealed"])
    )

async def mines_cashout(query, user):
    multiplier = 1 + len(user["revealed"]) * 0.2
    gain = int(user["bet"] * multiplier)

    user["balance"] += gain
    user["wins"] += 1
    user["game"] = None

    await query.edit_message_text(
        f"💰 Gain: {gain} FCFA",
        reply_markup=main_menu()
    )

# ==============================
# 🚀 LUCKY JET
# ==============================

async def start_lucky(query, user):
    user["game"] = "lucky"
    user["bet"] = 1000
    user["balance"] -= user["bet"]

    multiplier = 1.0
    crash = random.uniform(1.5, 5.0)

    message = await query.edit_message_text(
        "🚀 Lucky Jet\nx1.0",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Cashout", callback_data="lucky_cashout")]
        ])
    )

    while multiplier < crash:
        await asyncio.sleep(1)
        multiplier += 0.3
        try:
            await message.edit_text(
                f"🚀 Lucky Jet\nx{round(multiplier,2)}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💰 Cashout", callback_data="lucky_cashout")]
                ])
            )
        except:
            return

    user["losses"] += 1
    user["game"] = None
    await message.edit_text("💥 Crash !", reply_markup=main_menu())

async def lucky_cashout(query, user):
    text = query.message.text
    multiplier = float(text.split("x")[1])
    gain = int(user["bet"] * multiplier)

    user["balance"] += gain
    user["wins"] += 1
    user["game"] = None

    await query.edit_message_text(
        f"💰 Gain: {gain} FCFA",
        reply_markup=main_menu()
    )

# ==============================
# ⚽ PENALTY
# ==============================

async def start_penalty(query, user):
    user["game"] = "penalty"
    user["bet"] = 1000
    user["balance"] -= user["bet"]

    keyboard = [[
        InlineKeyboardButton("⬅️", callback_data="left"),
        InlineKeyboardButton("⬆️", callback_data="center"),
        InlineKeyboardButton("➡️", callback_data="right")
    ]]

    await query.edit_message_text(
        "⚽ Choisis une direction",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_penalty(query, user, choice):
    keeper = random.choice(["left","center","right"])

    if choice == keeper:
        user["losses"] += 1
        result = "🧤 Arrêt ! Perdu."
    else:
        gain = user["bet"] * 2
        user["balance"] += gain
        user["wins"] += 1
        result = f"⚽ BUT ! Gain: {gain} FCFA"

    user["game"] = None
    await query.edit_message_text(result, reply_markup=main_menu())

# ==============================
# 🎛 HANDLER
# ==============================

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)
    data = query.data

    if data == "balance":
        await show_balance(query)
    elif data == "stats":
        await show_stats(query)
    elif data == "mines":
        await start_mines(query, user)
    elif data.startswith("cell_"):
        await handle_mines(query, user, data)
    elif data == "cashout":
        await mines_cashout(query, user)
    elif data == "lucky":
        await start_lucky(query, user)
    elif data == "lucky_cashout":
        await lucky_cashout(query, user)
    elif data == "penalty":
        await start_penalty(query, user)
    elif data in ["left","center","right"]:
        await handle_penalty(query, user, data)

# ==============================
# 🚀 MAIN
# ==============================

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.run_polling()

if __name__ == "__main__":
    main()