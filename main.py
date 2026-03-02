import random
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# =============================
# TOKEN VIA VARIABLE RAILWAY
# =============================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN non défini dans Railway Variables")

# =============================
# CONFIG
# =============================
BASE_BALANCE = 10000
BASE_BET = 500

user_sessions = {}

# =============================
# INIT USER
# =============================
def init_user(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "balance": BASE_BALANCE,
            "history": []
        }

# =============================
# MENU KEYBOARD
# =============================
def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Jouer", callback_data="play")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("📜 Historique", callback_data="history")]
    ])

def back_to_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 MENU", callback_data="menu")]
    ])

# =============================
# START
# =============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 *CRASH PRO MAX*\n\nClique MENU 👇",
        parse_mode="Markdown",
        reply_markup=back_to_menu()
    )

# =============================
# BUTTON HANDLER
# =============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    init_user(user_id)
    session = user_sessions[user_id]

    # ================= MENU =================
    if query.data == "menu":
        await query.edit_message_text(
            "💎 *CRASH PRO MAX*\n\nChoisis une action 👇",
            parse_mode="Markdown",
            reply_markup=menu_keyboard()
        )

    # ================= PLAY =================
    elif query.data == "play":

        multiplier = round(random.uniform(1.0, 7.0), 2)

        message = await query.edit_message_text("🚀 1.00x")

        live = 1.0
        steps = min(int((multiplier - 1) / 0.4), 7)

        for _ in range(steps):
            await asyncio.sleep(0.4)
            live += 0.4
            try:
                await message.edit_text(f"🚀 {round(live,2)}x")
            except:
                break

        await asyncio.sleep(0.6)

        session["history"].insert(0, f"{multiplier}x")
        hist = " | ".join(session["history"][:4])

        final_text = (
            "━━━━━━━━━━━━━━━\n"
            f"💥 *CRASH à {multiplier}x*\n"
            "━━━━━━━━━━━━━━━\n\n"
            "📜 *Historique*\n"
            f"{hist if hist else 'Aucun'}\n\n"
            "━━━━━━━━━━━━━━━"
        )

        await message.edit_text(
            final_text,
            parse_mode="Markdown",
            reply_markup=back_to_menu()
        )

    # ================= STATS =================
    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 *STATISTIQUES*\n\n"
            f"💰 Solde: {session['balance']} FCFA",
            parse_mode="Markdown",
            reply_markup=back_to_menu()
        )

    # ================= HISTORY =================
    elif query.data == "history":
        hist = " | ".join(session["history"][:6])
        await query.edit_message_text(
            f"📜 *Historique*\n\n{hist if hist else 'Aucun historique.'}",
            parse_mode="Markdown",
            reply_markup=back_to_menu()
        )

# =============================
# MAIN
# =============================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot lancé 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()