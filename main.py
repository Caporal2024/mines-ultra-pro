import json
import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "PUT_YOUR_TOKEN_HERE"

# ===== DATABASE SIMPLE =====
DB_FILE = "database.json"

try:
    with open(DB_FILE, "r") as f:
        db = json.load(f)
except:
    db = {}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

def get_user(user_id):
    if str(user_id) not in db:
        db[str(user_id)] = {
            "balance": 10000,
            "game": None
        }
    return db[str(user_id)]

# ===== MENU =====
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 MINES", callback_data="mines")],
        [InlineKeyboardButton("🚀 CRASH", callback_data="crash")],
        [InlineKeyboardButton("💰 SOLDE", callback_data="balance")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎰 BIENVENUE DANS CRASH PRO MAX",
        reply_markup=main_menu()
    )

# ===== SOLDE =====
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)
    await query.edit_message_text(
        f"💰 Ton solde: {user['balance']} FCFA",
        reply_markup=main_menu()
    )

# ===== MINES =====
def generate_grid(user):
    buttons = []
    for i in range(25):
        if i in user["game"]["revealed"]:
            text = "💎"
        else:
            text = "⬜"
        buttons.append(InlineKeyboardButton(text, callback_data=f"cell_{i}"))

    keyboard = [buttons[i:i+5] for i in range(0, 25, 5)]
    keyboard.append([InlineKeyboardButton("💰 CASHOUT", callback_data="cashout")])
    return InlineKeyboardMarkup(keyboard)

async def mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)

    bombs = random.sample(range(25), 5)

    user["game"] = {
        "type": "mines",
        "bombs": bombs,
        "revealed": [],
        "multiplier": 1.0
    }

    save_db()

    await query.edit_message_text(
        "🎮 MINES 5x5\nClique une case",
        reply_markup=generate_grid(user)
    )

async def handle_cell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)
    index = int(query.data.split("_")[1])

    if not user["game"] or user["game"]["type"] != "mines":
        return

    if index in user["game"]["bombs"]:
        user["balance"] -= 1000
        user["game"] = None
        save_db()
        await query.edit_message_text(
            "💣 CRASH ! -1000 FCFA",
            reply_markup=main_menu()
        )
        return

    user["game"]["revealed"].append(index)
    user["game"]["multiplier"] += 0.2
    save_db()

    await query.edit_message_text(
        f"💎 SAFE\nMultiplicateur: {user['game']['multiplier']:.2f}x",
        reply_markup=generate_grid(user)
    )

async def cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)

    if not user["game"]:
        return

    gain = int(1000 * user["game"]["multiplier"])
    user["balance"] += gain
    user["game"] = None
    save_db()

    await query.edit_message_text(
        f"💰 GAIN {gain} FCFA",
        reply_markup=main_menu()
    )

# ===== CRASH LIVE =====
async def crash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)
    bet = 1000

    if user["balance"] < bet:
        await query.edit_message_text("Solde insuffisant", reply_markup=main_menu())
        return

    user["balance"] -= bet
    save_db()

    multiplier = 1.00
    crash_point = round(random.uniform(1.2, 5.0), 2)

    message = await query.edit_message_text(f"🚀 {multiplier:.2f}x")

    while multiplier < crash_point:
        await asyncio.sleep(0.7)
        multiplier += 0.05

        keyboard = [
            [InlineKeyboardButton("💰 CASHOUT", callback_data="crashout")]
        ]

        await message.edit_text(
            f"🚀 {multiplier:.2f}x\nClique CASHOUT vite !",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["crash_multiplier"] = multiplier
        context.user_data["crash_active"] = True

    context.user_data["crash_active"] = False

    await message.edit_text(
        f"💥 CRASH à {crash_point}x\nPerte: -{bet} FCFA",
        reply_markup=main_menu()
    )

async def crashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)

    if not context.user_data.get("crash_active"):
        return

    multiplier = context.user_data.get("crash_multiplier", 1)
    gain = int(1000 * multiplier)

    user["balance"] += gain
    save_db()

    context.user_data["crash_active"] = False

    await query.edit_message_text(
        f"💰 CASHOUT à {multiplier:.2f}x\nGain: {gain} FCFA",
        reply_markup=main_menu()
    )

# ===== MAIN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(balance, pattern="balance"))
app.add_handler(CallbackQueryHandler(mines, pattern="mines"))
app.add_handler(CallbackQueryHandler(handle_cell, pattern="cell_"))
app.add_handler(CallbackQueryHandler(cashout, pattern="cashout"))
app.add_handler(CallbackQueryHandler(crash, pattern="crash"))
app.add_handler(CallbackQueryHandler(crashout, pattern="crashout"))

print("BOT STARTED...")
app.run_polling()