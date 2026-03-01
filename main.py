import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from database import get_user

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 8094967191


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    message = (
        f"🎰 Bienvenue au Casino Premium\n\n"
        f"💰 Solde : {user['balance']} FCFA\n"
        f"🎮 Parties jouées : {user['games_played']}\n"
        f"🏆 Victoires : {user['wins']}\n"
        f"❌ Défaites : {user['losses']}"
    )

    await update.message.reply_text(message)


# ===== PROFIL =====
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    message = (
        f"📊 Ton Profil\n\n"
        f"💰 Solde : {user['balance']} FCFA\n"
        f"🎮 Parties : {user['games_played']}\n"
        f"🏆 Victoires : {user['wins']}\n"
        f"❌ Défaites : {user['losses']}"
    )

    await update.message.reply_text(message)


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN not found in environment variables")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))

    print("Bot en ligne...")
    app.run_polling()


if __name__ == "__main__":
    main()