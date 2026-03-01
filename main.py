import os
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================= USERS STORAGE =================
users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 1000,
            "wins": 0,
            "losses": 0,
            "game": None,
            "mines": [],
            "revealed": [],
            "bet": 100,
            "multiplier": 1.0
        }
    return users[user_id]

# ================= START MENU =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Mines 5x5", callback_data="mines")],
        [InlineKeyboardButton("✈️ Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("💰 Capital", callback_data="capital")]
    ]

    await update.message.reply_text(
        "🎰 CASINO ULTRA PRO\n\nChoisis un jeu :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= CAPITAL =================
async def show_capital(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(f"💰 Capital : {user['balance']} FCFA")

# ================= STATS =================
async def show_stats(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(
        f"📊 Stats\n\n"
        f"Victoires : {user['wins']}\n"
        f"Défaites : {user['losses']}\n"
        f"Capital : {user['balance']} FCFA"
    )

# ================= LUCKY JET =================
async def lucky_game(query):
    user = get_user(query.from_user.id)

    multiplier = round(random.uniform(1.0, 3.0), 2)
    gain = int(user["bet"] * multiplier)

    if multiplier >= 1.5:
        user["balance"] += gain
        user["wins"] += 1
        result = f"🚀 Multiplicateur : x{multiplier}\n✅ Gain : {gain} FCFA"
    else:
        user["balance"] -= user["bet"]
        user["losses"] += 1
        result = f"💥 Crash à x{multiplier}\n❌ Perdu : {user['bet']} FCFA"

    await query.edit_message_text(result)

# ================= MINES MENU =================
async def mines_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("3 Mines", callback_data="m3"),
            InlineKeyboardButton("5 Mines", callback_data="m5"),
            InlineKeyboardButton("7 Mines", callback_data="m7"),
        ]
    ]
    await query.edit_message_text(
        "💣 Choisis le nombre de mines :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= START MINES =================
async def start_mines(query, mines_count):
    user = get_user(query.from_user.id)

    user["game"] = "mines"
    user["mines"] = random.sample(range(25), mines_count)
    user["revealed"] = []
    user["multiplier"] = 1.0

    await show_grid(query, user)

# ================= SHOW GRID =================
async def show_grid(query, user):
    keyboard = []
    for i in range(25):
        if i in user["revealed"]:
            text = "💎"
        else:
            text = "⬜"
        keyboard.append(
            InlineKeyboardButton(text, callback_data=f"c{i}")
        )

    grid = [keyboard[i:i+5] for i in range(0, 25, 5)]

    grid.append([InlineKeyboardButton("💰 Cashout", callback_data="cash")])

    await query.edit_message_text(
        f"💣 Mines Game\nMultiplier : x{user['multiplier']}",
        reply_markup=InlineKeyboardMarkup(grid)
    )

# ================= CLICK CELL =================
async def click_cell(query, index):
    user = get_user(query.from_user.id)

    if index in user["mines"]:
        user["balance"] -= user["bet"]
        user["losses"] += 1
        user["game"] = None
        await query.edit_message_text("💥 BOOM ! Tu as perdu.")
        return

    if index not in user["revealed"]:
        user["revealed"].append(index)
        user["multiplier"] += 0.2

    await show_grid(query, user)

# ================= CASHOUT =================
async def cashout(query):
    user = get_user(query.from_user.id)

    gain = int(user["bet"] * user["multiplier"])
    user["balance"] += gain
    user["wins"] += 1
    user["game"] = None

    await query.edit_message_text(f"💰 Cashout réussi !\nGain : {gain} FCFA")

# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "mines":
        await mines_menu(query)

    elif data in ["m3", "m5", "m7"]:
        mines_count = int(data[1])
        await start_mines(query, mines_count)

    elif data.startswith("c"):
        index = int(data[1:])
        await click_cell(query, index)

    elif data == "cash":
        await cashout(query)

    elif data == "lucky":
        await lucky_game(query)

    elif data == "stats":
        await show_stats(query)

    elif data == "capital":
        await show_capital(query)

# ================= RUN =================
TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

print("🔥 CASINO ULTRA PRO LANCÉ 🔥")

app.run_polling()