from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from database import get_user, update_balance

ADMIN_ID = 8094967191

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    message = (
        f"🎰 Bienvenue au Casino Premium\n\n"
        f"💰 Solde: {user['balance']} FCFA\n"
        f"🎮 Parties jouées: {user['games_played']}\n"
        f"🏆 Victoires: {user['wins']}\n"
        f"❌ Défaites: {user['losses']}"
    )

    await update.message.reply_text(message)


# ===== PROFIL =====
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    message = (
        f"📊 Ton Profil\n\n"
        f"💰 Solde: {user['balance']} FCFA\n"
        f"🎮 Parties: {user['games_played']}\n"
        f"🏆 Victoires: {user['wins']}\n"
        f"❌ Défaites: {user['losses']}"
    )

    await update.message.reply_text(message)


# ===== ADMIN PANEL =====
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Accès refusé.")
        return

    await update.message.reply_text("👑 Panneau Admin activé.")


# ===== MAIN =====
def main():
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("admin", admin))

    print("Bot lancé...")
    app.run_polling()


if __name__ == "__main__":
    main()