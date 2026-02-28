import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ==============================
# CONFIGURATION
# ==============================

TOKEN = "TON_TOKEN_ICI"  # ⚠️ Mets ton token ici
ADMIN_ID = 8094967191

# ==============================
# STOCKAGE UTILISATEUR
# ==============================

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "wins": 0,
            "losses": 0,
            "history": []
        }
    return users[user_id]

def is_admin(user_id):
    return user_id == ADMIN_ID

# ==============================
# MENU PRINCIPAL
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Accès refusé.")
        return

    keyboard = [
        [InlineKeyboardButton("💣 Mine 💎", callback_data="mine_menu")],
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("⚽️ Pénalité", callback_data="penalty")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ]

    await update.message.reply_text(
        "🎰 CASINO PRO MAX 👀\n📈📉🧠 Mode Intelligent Activé\n\nChoisis ton jeu 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# MENU MINE (3-5-7)
# ==============================

async def mine_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("💎 3", callback_data="mine_3"),
            InlineKeyboardButton("💎 5", callback_data="mine_5"),
            InlineKeyboardButton("💎 7", callback_data="mine_7"),
        ],
        [InlineKeyboardButton("⬅ Retour", callback_data="menu")]
    ]

    await query.edit_message_text(
        "💣 MINE PRO MAX\nChoisis nombre de bombes 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# PRÉDICTION MINE (TOUT S’OUVRE)
# ==============================

async def send_mine(query, user_id, bombs):
    user = get_user(user_id)

    grid = ""
    bomb_positions = random.sample(range(25), bombs)

    for i in range(25):
        if i in bomb_positions:
            grid += "💣 "
        else:
            grid += "💎 "
        if (i + 1) % 5 == 0:
            grid += "\n"

    user["history"].append("Mine")
    user["wins"] += 1

    await query.edit_message_text(
        f"💣 MINE {bombs} Bombes\n\n{grid}"
    )

# ==============================
# LUCKY JET
# ==============================

async def send_lucky(query, user_id):
    user = get_user(user_id)
    multiplier = round(random.uniform(1.20, 3.50), 2)

    trend = "📈" if multiplier > 2 else "📉"

    user["history"].append("Lucky")
    user["wins"] += 1

    await query.edit_message_text(
        f"🚀 LUCKY JET PRO MAX\n\n🔥 Cashout conseillé : {multiplier}x {trend}"
    )

# ==============================
# PÉNALITÉ
# ==============================

async def send_penalty(query, user_id):
    user = get_user(user_id)
    direction = random.choice(["⬅️ Gauche", "➡️ Droite", "⬆️ Centre"])

    user["history"].append("Penalty")
    user["wins"] += 1

    await query.edit_message_text(
        f"⚽️ PÉNALITÉ PRO MAX\n\n🎯 Tire ici : {direction}"
    )

# ==============================
# STATS
# ==============================

async def send_stats(query, user_id):
    user = get_user(user_id)

    await query.edit_message_text(
        f"📊 STATISTIQUES PRO MAX\n\n"
        f"🎮 Jeux joués : {len(user['history'])}\n"
        f"🏆 Succès : {user['wins']}\n"
        f"🧠 Mode intelligent actif 👀"
    )

# ==============================
# HANDLER GLOBAL
# ==============================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not is_admin(user_id):
        return

    if query.data == "menu":
        await start(update, context)

    elif query.data == "mine_menu":
        await mine_menu(query)

    elif query.data.startswith("mine_"):
        bombs = int(query.data.split("_")[1])
        await send_mine(query, user_id, bombs)

    elif query.data == "lucky":
        await send_lucky(query, user_id)

    elif query.data == "penalty":
        await send_penalty(query, user_id)

    elif query.data == "stats":
        await send_stats(query, user_id)

# ==============================
# LANCEMENT BOT
# ==============================

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🎰 CASINO PRO MAX ACTIF 🚀")
    app.run_polling()