import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN manquant ! Ajoute-le dans Railway → Variables")

user_sessions = {}

# ================= MENU =================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 MINES 5x5 PRO", callback_data="mines")],
        [InlineKeyboardButton("🚀 CRASH IA", callback_data="crash")],
        [InlineKeyboardButton("🤖 MODE AUTO", callback_data="auto")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 PRO MAX CASINO IA 💎\n\nChoisis un mode 👇",
        reply_markup=main_menu()
    )

# ================= CRASH =================
async def crash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    multiplier = round(random.uniform(1.0, 5.0), 2)

    if multiplier < 1.5:
        advice = "⚠️ Zone froide - Attendre"
    elif multiplier > 3:
        advice = "🔥 Zone chaude - Petite mise"
    else:
        advice = "🎯 Entrée normale"

    await query.edit_message_text(
        f"🚀 CRASH RESULT\n\nMultiplicateur: {multiplier}x\n\n🧠 IA: {advice}",
        reply_markup=main_menu()
    )

# ================= MINES =================
def generate_mines():
    return random.sample(range(25), 3)

def build_mines_keyboard(user_id):
    data = user_sessions[user_id]
    keyboard = []

    for i in range(25):
        if i in data["opened"]:
            button = InlineKeyboardButton("✅", callback_data="ignore")
        else:
            button = InlineKeyboardButton("⬜", callback_data=f"cell_{i}")
        keyboard.append(button)

    rows = [keyboard[i:i+5] for i in range(0, 25, 5)]
    rows.append([InlineKeyboardButton("💰 ENCAISSER", callback_data="cashout")])

    return InlineKeyboardMarkup(rows)

async def mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_sessions[query.from_user.id] = {
        "mines": generate_mines(),
        "opened": []
    }

    await query.edit_message_text(
        "💣 MINES 5x5 PRO\n\nChoisis une case 👇",
        reply_markup=build_mines_keyboard(query.from_user.id)
    )

async def cell_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = user_sessions.get(user_id)

    if not data:
        await query.edit_message_text("Session expirée.", reply_markup=main_menu())
        return

    cell = int(query.data.split("_")[1])

    if cell in data["opened"]:
        return

    if cell in data["mines"]:
        await query.edit_message_text(
            "💥 BOOM ! Mine touchée !",
            reply_markup=main_menu()
        )
        return

    data["opened"].append(cell)

    remaining_mines = 3
    remaining_cells = 25 - len(data["opened"])
    risk = round((remaining_mines / remaining_cells) * 100, 2)

    await query.edit_message_text(
        f"✅ SAFE\n\n📊 Risque actuel: {risk}%",
        reply_markup=build_mines_keyboard(user_id)
    )

async def cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "💰 Tu as encaissé avec succès !",
        reply_markup=main_menu()
    )

# ================= AUTO =================
async def auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    decision = random.choice(["ENTRER", "ATTENDRE"])
    cashout_value = round(random.uniform(1.5, 3.0), 2)

    await query.edit_message_text(
        f"🤖 MODE AUTO\n\nDécision: {decision}\nAuto cashout: {cashout_value}x",
        reply_markup=main_menu()
    )

# ================= HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "mines":
        await mines(update, context)
    elif query.data == "crash":
        await crash(update, context)
    elif query.data == "auto":
        await auto(update, context)
    elif query.data.startswith("cell_"):
        await cell_click(update, context)
    elif query.data == "cashout":
        await cashout(update, context)
    elif query.data == "ignore":
        return

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

print("🔥 BOT LANCÉ 🔥")
app.run_polling()