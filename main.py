import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

# ==============================
# STOCKAGE GLOBAL
# ==============================
users = {}
mines_games = {}

# ==============================
# UTILISATEUR
# ==============================
def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "wins": 0,
            "losses": 0,
            "profit": 0
        }
    return users[user_id]

# ==============================
# MENU PRINCIPAL
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💣 Mine", callback_data="mine_menu")],
        [InlineKeyboardButton("🥅 Penalty", callback_data="penalty_menu")],
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="jet")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ]
    await update.message.reply_text(
        "🎰 CASINO PRO MAX\n\nChoisis un jeu 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# MINE MENU
# ==============================
async def mine_menu(query):
    keyboard = [
        [InlineKeyboardButton("🟢 3 Bombes", callback_data="mine_3")],
        [InlineKeyboardButton("🟡 5 Bombes", callback_data="mine_5")],
        [InlineKeyboardButton("🔴 7 Bombes", callback_data="mine_7")],
        [InlineKeyboardButton("⬅ Retour", callback_data="menu")]
    ]
    await query.edit_message_text(
        "💣 Choisis le niveau Mine",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# CREER PARTIE MINE
# ==============================
async def start_mine_game(query, user_id, bombs):
    grid_size = 25
    bomb_positions = random.sample(range(grid_size), bombs)

    mines_games[user_id] = {
        "bombs": bomb_positions,
        "revealed": [],
        "bomb_count": bombs,
        "multiplier": 1.0,
        "active": True
    }

    await render_mine_grid(query, user_id)

# ==============================
# AFFICHER GRILLE
# ==============================
async def render_mine_grid(query, user_id, reveal_all=False):
    game = mines_games[user_id]
    user = get_user(user_id)

    buttons = []

    for i in range(25):
        if reveal_all:
            text = "💣" if i in game["bombs"] else "💎"
        elif i in game["revealed"]:
            text = "💎"
        else:
            text = "⬜"

        buttons.append(
            InlineKeyboardButton(text, callback_data=f"cell_{i}")
        )

    grid = [buttons[i:i+5] for i in range(0, 25, 5)]

    if game["active"]:
        grid.append([InlineKeyboardButton("💰 Cashout", callback_data="mine_cashout")])

    await query.edit_message_text(
        f"💣 Mine ({game['bomb_count']} bombes)\n"
        f"💰 Balance: {user['balance']}\n"
        f"📈 Multiplier: x{round(game['multiplier'],2)}",
        reply_markup=InlineKeyboardMarkup(grid)
    )

# ==============================
# CLIQUER CASE
# ==============================
async def handle_cell(query, user_id, index):
    game = mines_games[user_id]
    user = get_user(user_id)

    if not game["active"] or index in game["revealed"]:
        return

    if index in game["bombs"]:
        game["active"] = False
        user["balance"] -= 1000
        user["losses"] += 1
        user["profit"] -= 1000
        await render_mine_grid(query, user_id, reveal_all=True)
    else:
        game["revealed"].append(index)
        game["multiplier"] += 0.2
        await render_mine_grid(query, user_id)

# ==============================
# CASHOUT
# ==============================
async def mine_cashout(query, user_id):
    game = mines_games[user_id]
    user = get_user(user_id)

    if not game["active"]:
        return

    gain = int(1000 * game["multiplier"])
    user["balance"] += gain
    user["wins"] += 1
    user["profit"] += gain
    game["active"] = False

    await render_mine_grid(query, user_id, reveal_all=True)

# ==============================
# PENALTY
# ==============================
async def penalty_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("⬅ Gauche", callback_data="shoot_left"),
            InlineKeyboardButton("⬆ Centre", callback_data="shoot_center"),
            InlineKeyboardButton("➡ Droite", callback_data="shoot_right")
        ],
        [InlineKeyboardButton("⬅ Retour", callback_data="menu")]
    ]

    await query.edit_message_text(
        "🥅 Choisis où tirer ⚽",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def penalty_shot(query, user_id, direction):
    keeper = random.choice(["left", "center", "right"])
    user = get_user(user_id)

    visual = {
        "left": "🧤 ⬜ ⬜",
        "center": "⬜ 🧤 ⬜",
        "right": "⬜ ⬜ 🧤"
    }

    if direction == keeper:
        user["balance"] -= 1000
        user["losses"] += 1
        user["profit"] -= 1000
        result = "❌ Arrêt !"
    else:
        user["balance"] += 1500
        user["wins"] += 1
        user["profit"] += 1500
        result = "⚽ BUT !"

    await query.edit_message_text(
        f"{visual[keeper]}\n\n{result}\n💰 Balance: {user['balance']}"
    )

# ==============================
# LUCKY JET
# ==============================
async def lucky_jet(query, user_id):
    user = get_user(user_id)
    multiplier = round(random.uniform(1.1, 5.0), 2)

    if multiplier > 2:
        gain = int(1000 * multiplier)
        user["balance"] += gain
        user["wins"] += 1
        user["profit"] += gain
        result = f"🚀 x{multiplier} 💎 +{gain}"
    else:
        user["balance"] -= 1000
        user["losses"] += 1
        user["profit"] -= 1000
        result = f"💥 x{multiplier} ❌ -1000"

    keyboard = [[InlineKeyboardButton("🔄 Rejouer", callback_data="jet")]]

    await query.edit_message_text(
        f"{result}\n💰 Balance: {user['balance']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# STATS
# ==============================
async def show_stats(query, user_id):
    user = get_user(user_id)
    await query.edit_message_text(
        f"📊 Stats\n\n"
        f"💰 Balance: {user['balance']}\n"
        f"🏆 Wins: {user['wins']}\n"
        f"❌ Losses: {user['losses']}\n"
        f"📈 Profit: {user['profit']}"
    )

# ==============================
# HANDLER GLOBAL
# ==============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "menu":
        await start(update, context)

    elif query.data == "mine_menu":
        await mine_menu(query)

    elif query.data.startswith("mine_"):
        bombs = int(query.data.split("_")[1])
        await start_mine_game(query, user_id, bombs)

    elif query.data.startswith("cell_"):
        index = int(query.data.split("_")[1])
        await handle_cell(query, user_id, index)

    elif query.data == "mine_cashout":
        await mine_cashout(query, user_id)

    elif query.data == "penalty_menu":
        await penalty_menu(query)

    elif query.data.startswith("shoot_"):
        direction = query.data.split("_")[1]
        await penalty_shot(query, user_id, direction)

    elif query.data == "jet":
        await lucky_jet(query, user_id)

    elif query.data == "stats":
        await show_stats(query, user_id)

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("CASINO PRO MAX ACTIF 🚀")
    app.run_polling()