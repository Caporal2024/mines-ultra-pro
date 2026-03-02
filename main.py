import random
import hashlib
import hmac
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# CONFIGURATION
# =========================

GRID_SIZE = 5
TOTAL_CELLS = GRID_SIZE * GRID_SIZE
MINES_COUNT = 3

# =========================
# GAME STORAGE (mémoire simple)
# =========================

games = {}

# =========================
# PROVABLY FAIR FUNCTIONS
# =========================

def generate_server_seed():
    return os.urandom(32).hex()

def hash_server_seed(server_seed):
    return hashlib.sha256(server_seed.encode()).hexdigest()

def generate_game_hash(server_seed, client_seed, nonce):
    message = f"{client_seed}:{nonce}".encode()
    return hmac.new(server_seed.encode(), message, hashlib.sha256).hexdigest()

def generate_mines_positions(game_hash, mines_count):
    positions = []
    index = 0

    while len(positions) < mines_count:
        slice_hash = game_hash[index:index+8]
        number = int(slice_hash, 16)
        position = number % TOTAL_CELLS

        if position not in positions:
            positions.append(position)

        index += 8

    return positions

# =========================
# GAME LOGIC
# =========================

def create_keyboard(revealed=[]):
    keyboard = []
    for i in range(TOTAL_CELLS):
        if i in revealed:
            text = "✅"
        else:
            text = "⬜"

        keyboard.append(
            InlineKeyboardButton(text, callback_data=f"cell_{i}")
        )

    rows = [keyboard[i:i+GRID_SIZE] for i in range(0, TOTAL_CELLS, GRID_SIZE)]
    return InlineKeyboardMarkup(rows)

# =========================
# COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    server_seed = generate_server_seed()
    server_hash = hash_server_seed(server_seed)
    client_seed = str(user_id)
    nonce = 1

    game_hash = generate_game_hash(server_seed, client_seed, nonce)
    mines = generate_mines_positions(game_hash, MINES_COUNT)

    games[user_id] = {
        "server_seed": server_seed,
        "server_hash": server_hash,
        "client_seed": client_seed,
        "nonce": nonce,
        "mines": mines,
        "revealed": [],
        "active": True
    }

    await update.message.reply_text(
        f"🎮 Nouvelle partie Mines 5x5\n\n"
        f"🔒 Hash: {server_hash}\n\n"
        f"Clique une case.",
        reply_markup=create_keyboard()
    )

async def handle_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in games:
        return

    game = games[user_id]

    if not game["active"]:
        return

    cell = int(query.data.split("_")[1])

    if cell in game["mines"]:
        game["active"] = False

        await query.edit_message_text(
            f"💥 BOOM ! Tu as touché une mine.\n\n"
            f"🔓 Server Seed: {game['server_seed']}\n"
            f"🔒 Hash initial: {game['server_hash']}\n\n"
            f"Tu peux vérifier le résultat."
        )
        return

    game["revealed"].append(cell)

    await query.edit_message_reply_markup(
        reply_markup=create_keyboard(game["revealed"])
    )

# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token("PASTE_YOUR_TOKEN_HERE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_click))

    print("Bot lancé...")
    app.run_polling()

if __name__ == "__main__":
    main()