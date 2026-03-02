import os
import random
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8094967191

logging.basicConfig(level=logging.INFO)

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "bankroll": 10000,
            "bomb_count": 3,
            "mines": []
        }
    return users[user_id]

# ================= MENU =================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("💣 Mines 5x5", callback_data="mines_menu")],
        [InlineKeyboardButton("⚡ Lucky Jet LIVE", callback_data="lucky_menu")],
        [InlineKeyboardButton("📊 Statistiques", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

def mines_menu():
    keyboard = [
        [
            InlineKeyboardButton("💣 3", callback_data="bomb_3"),
            InlineKeyboardButton("💣 5", callback_data="bomb_5"),
            InlineKeyboardButton("💣 7", callback_data="bomb_7")
        ],
        [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def lucky_menu():
    keyboard = [
        [InlineKeyboardButton("⚡ DÉMARRER LIVE", callback_data="start_lucky")],
        [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu")]])

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    text = f"""
💎 <b>PRO MAX V7</b>
━━━━━━━━━━━━━━━━━━
💰 Bankroll : <b>{user['bankroll']} FCFA</b>
━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())

# ================= LUCKY JET LIVE =================

async def lucky_live_animation(query):
    multiplier = 1.00
    message = await query.edit_message_text("⚡ Lucky Jet LIVE\n\n🚀 x1.00")

    for _ in range(12):
        await asyncio.sleep(0.35)
        multiplier += random.uniform(0.05, 0.30)
        multiplier = round(multiplier, 2)
        await message.edit_text(f"⚡ Lucky Jet LIVE\n\n🚀 x{multiplier}")

    await asyncio.sleep(0.5)
    await message.edit_text(
        f"""
💥 <b>CRASH</b>
━━━━━━━━━━━━━━━━━━
🎯 Résultat final : <b>x{multiplier}</b>
━━━━━━━━━━━━━━━━━━
""",
        parse_mode="HTML",
        reply_markup=back_menu()
    )

# ================= MINES =================

def generate_mines(count):
    return random.sample(range(25), count)

def build_grid(user, reveal=False):
    grid = []
    for i in range(5):
        row = []
        for j in range(5):
            index = i * 5 + j
            if reveal:
                if index in user["mines"]:
                    row.append(InlineKeyboardButton("💣", callback_data="x"))
                else:
                    row.append(InlineKeyboardButton("✅", callback_data="x"))
            else:
                row.append(InlineKeyboardButton("🟦", callback_data=f"cell_{index}"))
        grid.append(row)
    return InlineKeyboardMarkup(grid)

# ================= HANDLER =================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    if query.data == "menu":
        await query.edit_message_text("💎 MENU PRINCIPAL", reply_markup=main_menu())

    elif query.data == "mines_menu":
        await query.edit_message_text("💣 Choisis 3 - 5 - 7 bombes", reply_markup=mines_menu())

    elif query.data.startswith("bomb_"):
        bomb_count = int(query.data.split("_")[1])
        user["bomb_count"] = bomb_count
        user["mines"] = generate_mines(bomb_count)
        await query.edit_message_text(
            f"💣 Partie lancée avec {bomb_count} bombes\nClique une case",
            reply_markup=build_grid(user)
        )

    elif query.data.startswith("cell_"):
        index = int(query.data.split("_")[1])

        if index in user["mines"]:
            user["bankroll"] -= 1000
            await query.edit_message_text(
                f"""
💥 <b>BOOM</b>
💸 -1000 FCFA
🏦 Bankroll : {user['bankroll']}
""",
                parse_mode="HTML",
                reply_markup=build_grid(user, reveal=True)
            )
        else:
            user["bankroll"] += 500
            await query.edit_message_text(
                f"""
✅ SAFE
💰 +500 FCFA
🏦 Bankroll : {user['bankroll']}
""",
                parse_mode="HTML",
                reply_markup=build_grid(user, reveal=True)
            )

    elif query.data == "lucky_menu":
        await query.edit_message_text("⚡ Lucky Jet LIVE", reply_markup=lucky_menu())

    elif query.data == "start_lucky":
        await lucky_live_animation(query)

    elif query.data == "stats":
        await query.edit_message_text(
            f"""
📊 <b>STATISTIQUES</b>
━━━━━━━━━━━━━━━━━━
💰 Bankroll : {user['bankroll']}
━━━━━━━━━━━━━━━━━━
""",
            parse_mode="HTML",
            reply_markup=back_menu()
        )

# ================= MAIN =================

def main():
    if not TOKEN:
        print("BOT_TOKEN manquant")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("PRO MAX V7 actif")
    app.run_polling()

if __name__ == "__main__":
    main()