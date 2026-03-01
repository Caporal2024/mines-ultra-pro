import os
import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================= CONFIG =================
DEFAULT_BET = 1000
users = {}

# ================= IA SIMPLE 🤖 =================
def ai_adjustment(user):
    # IA simple : ajuste le multiplicateur selon performance
    if user["losses"] > user["wins"]:
        return 1.2   # un peu plus favorable
    elif user["wins"] > user["losses"]:
        return 0.9   # un peu plus risqué
    return 1.0

# ================= USER SYSTEM =================
def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "wins": 0,
            "losses": 0,
            "game_active": False,
            "mines": [],
            "revealed": [],
            "bet": DEFAULT_BET,
            "multiplier": 1.0,
        }
    return users[user_id]

# ================= MENU =================
async def show_main_menu(target):
    keyboard = [
        [InlineKeyboardButton("🎮🎮🎮 MINES 5x5 PRO 🎮🎮🎮", callback_data="mines")],
        [InlineKeyboardButton("✈️✈️✈️ LUCKY JET LIVE ⚡✈️✈️✈️", callback_data="lucky")],
        [InlineKeyboardButton("📊📊 MES STATS 📊📊", callback_data="stats")],
        [InlineKeyboardButton("💰💰 MON CAPITAL 💰💰", callback_data="capital")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if hasattr(target, "message"):
        await target.message.reply_text(
            "🎰 CASINO PRO IA 🤖\n\nChoisis ton jeu :",
            reply_markup=markup,
        )
    else:
        await target.edit_message_text(
            "🎰 CASINO PRO IA 🤖\n\nChoisis ton jeu :",
            reply_markup=markup,
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update)

# ================= CAPITAL =================
async def show_capital(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(
        f"💰 CAPITAL : {user['balance']} FCFA",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🏠🏠🏠 MENU PRINCIPAL 🏠🏠🏠", callback_data="menu")]]
        ),
    )

# ================= STATS =================
async def show_stats(query):
    user = get_user(query.from_user.id)
    await query.edit_message_text(
        f"📊 STATS\n\n"
        f"✅ Victoires : {user['wins']}\n"
        f"❌ Défaites : {user['losses']}\n"
        f"💰 Solde : {user['balance']} FCFA",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🏠🏠🏠 MENU PRINCIPAL 🏠🏠🏠", callback_data="menu")]]
        ),
    )

# ================= LUCKY JET RAPIDE + IA =================
async def lucky_game(query):
    user = get_user(query.from_user.id)

    if user["game_active"]:
        await query.answer("⚠️ Partie déjà en cours.")
        return

    if user["balance"] < user["bet"]:
        await query.edit_message_text("❌ Solde insuffisant.")
        return

    user["game_active"] = True

    ai_factor = ai_adjustment(user)
    multiplier = 1.00
    crash_point = round(random.uniform(1.5, 3.0) * ai_factor, 2)

    msg = await query.edit_message_text("✈️ LUCKY JET LIVE 🤖\n🚀 x1.00")

    while multiplier < crash_point:
        multiplier += 0.25  # plus rapide
        await msg.edit_text(f"✈️ LUCKY JET LIVE 🤖\n🚀 x{round(multiplier,2)}")
        await asyncio.sleep(0.2)

    user["balance"] -= user["bet"]
    user["losses"] += 1
    user["game_active"] = False

    await msg.edit_text(
        f"💥 CRASH à x{crash_point}\n\n"
        f"❌ Perdu {user['bet']} FCFA\n"
        f"💰 Solde : {user['balance']} FCFA",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🏠🏠🏠 MENU PRINCIPAL 🏠🏠🏠", callback_data="menu")]]
        ),
    )

# ================= MINES =================
async def mines_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("💣 3 MINES", callback_data="m3"),
            InlineKeyboardButton("💣 5 MINES", callback_data="m5"),
            InlineKeyboardButton("💣 7 MINES", callback_data="m7"),
        ],
        [InlineKeyboardButton("🏠🏠🏠 MENU PRINCIPAL 🏠🏠🏠", callback_data="menu")],
    ]
    await query.edit_message_text(
        "🎮 MINES 5x5 PRO 🤖\nChoisis niveau :",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def start_mines(query, mines_count):
    user = get_user(query.from_user.id)

    if user["game_active"]:
        await query.answer("⚠️ Partie déjà en cours.")
        return

    if user["balance"] < user["bet"]:
        await query.edit_message_text("❌ Solde insuffisant.")
        return

    user["game_active"] = True
    user["mines"] = random.sample(range(25), mines_count)
    user["revealed"] = []
    user["multiplier"] = 1.0

    await show_grid(query, user)

async def show_grid(query, user):
    keyboard = []
    for i in range(25):
        text = "💎" if i in user["revealed"] else "⬜"
        keyboard.append(InlineKeyboardButton(text, callback_data=f"c{i}"))

    grid = [keyboard[i:i+5] for i in range(0, 25, 5)]
    grid.append([InlineKeyboardButton("💰 CASHOUT", callback_data="cash")])
    grid.append([InlineKeyboardButton("🏠🏠🏠 MENU PRINCIPAL 🏠🏠🏠", callback_data="menu")])

    await query.edit_message_text(
        f"💣 MINES 5x5\nMultiplier : x{user['multiplier']}",
        reply_markup=InlineKeyboardMarkup(grid),
    )

async def click_cell(query, index):
    user = get_user(query.from_user.id)

    if index in user["mines"]:
        user["balance"] -= user["bet"]
        user["losses"] += 1
        user["game_active"] = False
        await query.edit_message_text(
            f"💥 BOOM !\n❌ Perdu {user['bet']} FCFA\n💰 Solde : {user['balance']} FCFA",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🏠🏠🏠 MENU PRINCIPAL 🏠🏠🏠", callback_data="menu")]]
            ),
        )
        return

    if index not in user["revealed"]:
        user["revealed"].append(index)
        user["multiplier"] += 0.4

    await show_grid(query, user)

async def cashout(query):
    user = get_user(query.from_user.id)

    gain = int(user["bet"] * user["multiplier"])
    user["balance"] += gain
    user["wins"] += 1
    user["game_active"] = False

    await query.edit_message_text(
        f"💰 CASHOUT RÉUSSI\n"
        f"Gain : {gain} FCFA\n"
        f"💰 Solde : {user['balance']} FCFA",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🏠🏠🏠 MENU PRINCIPAL 🏠🏠🏠", callback_data="menu")]]
        ),
    )

# ================= HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu":
        await show_main_menu(query)
    elif data == "mines":
        await mines_menu(query)
    elif data in ["m3", "m5", "m7"]:
        await start_mines(query, int(data[1]))
    elif data.startswith("c"):
        await click_cell(query, int(data[1:]))
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

print("🔥 CASINO PRO IA LANCÉ 🔥")

app.run_polling()