import os
import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

users = {}

# ================= USER SYSTEM =================

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 20000,
            "wins": 0,
            "losses": 0,
            "total_games": 0,
            "game": None
        }
    return users[user_id]

# ================= MENU =================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 Mines", callback_data="mines")],
        [InlineKeyboardButton("🔥 Mines High Risk (15)", callback_data="mines_hr")],
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("⚽ Penalty", callback_data="penalty")],
        [InlineKeyboardButton("💰 Solde", callback_data="balance")],
        [InlineKeyboardButton("📊 Stats détaillées", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎰 CASINO PRO MAX", reply_markup=main_menu())

# ================= STATS =================

async def show_balance(query, user):
    await query.edit_message_text(
        f"💰 Solde: {user['balance']} FCFA",
        reply_markup=main_menu()
    )

async def show_stats(query, user):
    await query.edit_message_text(
        f"""📊 STATISTIQUES
🎮 Parties: {user['total_games']}
🏆 Victoires: {user['wins']}
❌ Défaites: {user['losses']}
💰 Solde actuel: {user['balance']} FCFA""",
        reply_markup=main_menu()
    )

# ================= MINES =================

GRID_SIZE = 5

def generate_mines(count):
    return random.sample(range(GRID_SIZE * GRID_SIZE), count)

def build_mines_keyboard(user):
    keyboard = []
    for i in range(GRID_SIZE):
        row = []
        for j in range(GRID_SIZE):
            index = i * GRID_SIZE + j
            if index in user["revealed"]:
                row.append(InlineKeyboardButton("💎", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton("⬜", callback_data=f"cell_{index}"))
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("💣 Auto Reveal", callback_data="auto"),
        InlineKeyboardButton("💰 Cashout", callback_data="cashout")
    ])

    return InlineKeyboardMarkup(keyboard)

async def start_mines_game(query, user, mines_count, bet):
    if user["balance"] < bet:
        await query.edit_message_text("❌ Solde insuffisant", reply_markup=main_menu())
        return

    user["game"] = "mines"
    user["bet"] = bet
    user["mines"] = generate_mines(mines_count)
    user["revealed"] = []
    user["mines_count"] = mines_count
    user["balance"] -= bet
    user["total_games"] += 1

    await query.edit_message_text(
        f"💣 Mines {mines_count} bombes\nMise: {bet} FCFA",
        reply_markup=build_mines_keyboard(user)
    )

async def handle_mines(query, user, data):
    index = int(data.split("_")[1])

    if index in user["mines"]:
        user["losses"] += 1
        user["game"] = None
        await query.edit_message_text("💥 BOOM ! Perdu.", reply_markup=main_menu())
        return

    user["revealed"].append(index)
    multiplier = 1 + len(user["revealed"]) * (0.3 if user["mines_count"] == 15 else 0.2)

    await query.edit_message_text(
        f"💎 Safe\nMultiplicateur: x{round(multiplier,2)}",
        reply_markup=build_mines_keyboard(user)
    )

async def auto_reveal(query, user):
    safe_cells = [i for i in range(25) if i not in user["mines"] and i not in user["revealed"]]

    for cell in safe_cells[:3]:
        user["revealed"].append(cell)
        await asyncio.sleep(0.5)

    multiplier = 1 + len(user["revealed"]) * 0.2
    await query.edit_message_text(
        f"🤖 Auto Reveal activé\nMultiplicateur: x{round(multiplier,2)}",
        reply_markup=build_mines_keyboard(user)
    )

async def mines_cashout(query, user):
    multiplier = 1 + len(user["revealed"]) * (0.3 if user["mines_count"] == 15 else 0.2)
    gain = int(user["bet"] * multiplier)

    user["balance"] += gain
    user["wins"] += 1
    user["game"] = None

    await query.edit_message_text(
        f"💰 Gain: {gain} FCFA",
        reply_markup=main_menu()
    )

# ================= LUCKY JET =================

async def start_lucky(query, user):
    bet = 3000  # mode 3G
    if user["balance"] < bet:
        await query.edit_message_text("❌ Solde insuffisant", reply_markup=main_menu())
        return

    user["balance"] -= bet
    user["total_games"] += 1

    multiplier = round(random.uniform(1.1, 8.0), 2)

    if multiplier < 2:
        user["losses"] += 1
        await query.edit_message_text(f"🚀 Crash x{multiplier}\n❌ Perdu", reply_markup=main_menu())
        return

    gain = int(bet * multiplier)
    user["balance"] += gain
    user["wins"] += 1

    await query.edit_message_text(
        f"🚀 Lucky Jet\nMultiplicateur: x{multiplier}\n💰 Gain: {gain} FCFA",
        reply_markup=main_menu()
    )

# ================= PENALTY =================

async def start_penalty(query, user):
    bet = 10000  # mode 10G
    if user["balance"] < bet:
        await query.edit_message_text("❌ Solde insuffisant", reply_markup=main_menu())
        return

    user["balance"] -= bet
    user["total_games"] += 1

    keeper = random.choice(["left","center","right"])
    player = random.choice(["left","center","right"])

    if keeper == player:
        user["losses"] += 1
        await query.edit_message_text("🧤 Arrêt ! Perdu.", reply_markup=main_menu())
        return

    gain = bet * 2
    user["balance"] += gain
    user["wins"] += 1

    await query.edit_message_text(
        f"⚽ BUT ! Gain: {gain} FCFA",
        reply_markup=main_menu()
    )

# ================= HANDLER =================

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)
    data = query.data

    if data == "balance":
        await show_balance(query, user)

    elif data == "stats":
        await show_stats(query, user)

    elif data == "mines":
        await start_mines_game(query, user, 5, 1000)

    elif data == "mines_hr":
        await start_mines_game(query, user, 15, 3000)

    elif data.startswith("cell_"):
        await handle_mines(query, user, data)

    elif data == "auto":
        await auto_reveal(query, user)

    elif data == "cashout":
        await mines_cashout(query, user)

    elif data == "lucky":
        await start_lucky(query, user)

    elif data == "penalty":
        await start_penalty(query, user)

# ================= MAIN =================

def main():
    if not TOKEN:
        print("TOKEN manquant")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))

    print("Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()