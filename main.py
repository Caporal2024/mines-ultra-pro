import json
import random
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ===============================
# CONFIGURATION
# ===============================

TOKEN = ""  # <-- METS TON TOKEN ICI
START_BALANCE = 100000
DATA_FILE = "users.json"

# ===============================
# GESTION UTILISATEURS
# ===============================

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

def get_user(users, user_id):
    user_id = str(user_id)

    if user_id not in users:
        users[user_id] = {
            "balance": START_BALANCE,
            "wins": 0,
            "losses": 0
        }
    return users[user_id]

users = load_users()

# ===============================
# MENU PRINCIPAL
# ===============================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("💎 Mines", callback_data="mines")],
        [InlineKeyboardButton("⚽ Penalty", callback_data="penalty")],
        [InlineKeyboardButton("🚀 Lucky Jet", callback_data="lucky")],
        [InlineKeyboardButton("🏆 Classement", callback_data="leaderboard")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===============================
# JEUX
# ===============================

def play_mines(user):
    bet = 10000

    if user["balance"] < bet:
        return "❌ Solde insuffisant"

    user["balance"] -= bet

    if random.random() < 0.7:
        gain = int(bet * 1.5)
        user["balance"] += gain
        user["wins"] += 1
        return f"💎 SAFE !\nGain: {gain}"
    else:
        user["losses"] += 1
        return "💣 BOOM ! Perdu"

def play_penalty(user):
    bet = 10000

    if user["balance"] < bet:
        return "❌ Solde insuffisant"

    user["balance"] -= bet

    keeper = random.choice(["⬅️", "⬆️", "➡️"])
    player = random.choice(["⬅️", "⬆️", "➡️"])

    if keeper == player:
        user["losses"] += 1
        return f"""
⚽ Tir: {player}
🧤 Gardien: {keeper}

🧤 ARRÊT !
"""
    else:
        gain = bet * 2
        user["balance"] += gain
        user["wins"] += 1
        return f"""
⚽ Tir: {player}
🧤 Gardien: {keeper}

⚽ BUT !!!
💰 Gain: {gain}
"""

def play_lucky(user):
    bet = 10000

    if user["balance"] < bet:
        return "❌ Solde insuffisant"

    user["balance"] -= bet

    multiplier = round(random.uniform(1.1, 5.0), 2)

    if multiplier > 2:
        gain = int(bet * multiplier)
        user["balance"] += gain
        user["wins"] += 1
        return f"""
🚀 Lucky Jet
Crash à {multiplier}x

💰 Gain: {gain}
"""
    else:
        user["losses"] += 1
        return f"""
🚀 Lucky Jet
Crash à {multiplier}x

💥 Perdu
"""

# ===============================
# HANDLERS
# ===============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(users, update.effective_user.id)
    save_users(users)

    await update.message.reply_text(
        f"""
🎰 CASINO BOT

💰 Solde: {user['balance']}
🏆 Victoires: {user['wins']}
❌ Défaites: {user['losses']}
""",
        reply_markup=main_menu()
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(users, query.from_user.id)

    if query.data == "mines":
        result = play_mines(user)

    elif query.data == "penalty":
        result = play_penalty(user)

    elif query.data == "lucky":
        result = play_lucky(user)

    elif query.data == "leaderboard":
        top = sorted(users.items(), key=lambda x: x[1]["wins"], reverse=True)[:5]
        text = "🏆 TOP 5 JOUEURS\n\n"
        for i,(uid,data) in enumerate(top,1):
            text += f"{i}. {data['wins']} victoires\n"

        await query.edit_message_text(text, reply_markup=main_menu())
        return

    save_users(users)

    await query.edit_message_text(
        f"""
{result}

💰 Solde: {user['balance']}
""",
        reply_markup=main_menu()
    )

# ===============================
# LANCEMENT BOT
# ===============================

def main():
    if TOKEN == "":
        print("⚠️ Mets ton TOKEN dans le fichier avant de lancer.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))

    print("Bot lancé...")
    app.run_polling()

if __name__ == "__main__":
    main()