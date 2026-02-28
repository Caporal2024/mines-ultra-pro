import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from database import get_db, init_db
from config import BOT_TOKEN, LEVELS, ADMIN_ID
from games_mines import calculate_multiplier, safe_probability
from games_luckyjet import generate_crash

# Initialisation base de données
init_db()


# -------------------------
# Mise à jour automatique du niveau
# -------------------------
def update_level(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT xp FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if not result:
        return

    xp = result["xp"]

    level = "Bronze 🥉"
    for threshold in sorted(LEVELS.keys()):
        if xp >= threshold:
            level = LEVELS[threshold]

    cursor.execute(
        "UPDATE users SET level=? WHERE user_id=?",
        (level, user_id)
    )
    conn.commit()


# -------------------------
# COMMANDES
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

    await update.message.reply_text(
        "👑 Bienvenue sur EMPIRE PLATFORM\n\n"
        "Commandes disponibles :\n"
        "/profile\n"
        "/mines\n"
        "/luckyjet\n"
        "/rank"
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        await update.message.reply_text("❌ Profil introuvable.")
        return

    await update.message.reply_text(
        f"👤 PROFIL\n\n"
        f"💎 Coins : {user['coins']}\n"
        f"⭐ XP : {user['xp']}\n"
        f"🏅 Niveau : {user['level']}"
    )


async def mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    multiplier = calculate_multiplier(1)
    probability = safe_probability(1)

    await update.message.reply_text(
        f"💣 MINES MODE\n\n"
        f"Multiplicateur potentiel : x{multiplier}\n"
        f"Probabilité safe : {probability}"
    )


async def luckyjet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seed = str(random.random())
    crash = generate_crash(seed)

    await update.message.reply_text(
        f"🚀 LUCKY JET\n\n"
        f"Seed : {seed}\n"
        f"Crash prévu : x{crash}"
    )


async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, xp FROM users ORDER BY xp DESC LIMIT 5"
    )
    top = cursor.fetchall()

    msg = "🏆 CLASSEMENT XP\n\n"

    for i, user in enumerate(top, 1):
        msg += f"{i}. ID {user['user_id']} - {user['xp']} XP\n"

    await update.message.reply_text(msg)


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Accès refusé.")
        return

    await update.message.reply_text("🔐 Accès Admin validé.")


# -------------------------
# LANCEMENT DU BOT
# -------------------------

app = ApplicationBuilder().token(BOT_TOKEN).build()

8765706088:AAHEQvqlxuQhl2WHgsJ3g0cd6UdXaNwiqt0