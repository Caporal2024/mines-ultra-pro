import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("BOT_TOKEN")  # Token ajouté dans Railway

users = {}

# =========================
# MENU PRINCIPAL
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Analyse du Jour", callback_data="analyse")],
        [InlineKeyboardButton("💰 Définir Budget", callback_data="set_budget")],
        [InlineKeyboardButton("📈 Statistiques", callback_data="stats")],
        [InlineKeyboardButton("🔄 Reset Session", callback_data="reset")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💎 BOT PARIS PRO MAX 💎\n\nChoisis une option :",
        reply_markup=reply_markup
    )

# =========================
# ANALYSE SIMPLIFIÉE
# =========================

def generate_suggestions():
    matchs = [
        "Arsenal vs Brighton",
        "Inter vs Lazio",
        "Real Madrid vs Sevilla",
        "Bayern vs Frankfurt",
        "PSG vs Lyon"
    ]

    markets = [
        "Double Chance 1X",
        "Over 1.5 buts",
        "Under 3.5 buts",
        "Draw No Bet"
    ]

    suggestions = []
    selected = random.sample(matchs, 2)

    for match in selected:
        market = random.choice(markets)
        confidence = random.randint(65, 80)
        suggestions.append(
            f"{match}\n✔ {market}\nConfiance : {confidence}%\n"
        )

    return "\n".join(suggestions)

# =========================
# CALLBACKS
# =========================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in users:
        users[user_id] = {
            "budget": 0,
            "played": 0,
            "wins": 0,
            "losses": 0
        }

    if query.data == "analyse":
        users[user_id]["played"] += 1
        suggestions = generate_suggestions()

        await query.edit_message_text(
            f"🎯 Suggestions du Jour\n\n{suggestions}\n⚠ Discipline obligatoire. Pas de garantie."
        )

    elif query.data == "set_budget":
        await query.edit_message_text(
            "💰 Envoie ton budget comme ceci :\n/budget 20000"
        )

    elif query.data == "stats":
        data = users[user_id]
        await query.edit_message_text(
            f"📈 Statistiques\n\n"
            f"Budget: {data['budget']} FCFA\n"
            f"Tickets joués: {data['played']}\n"
            f"Gains: {data['wins']}\n"
            f"Pertes: {data['losses']}"
        )

    elif query.data == "reset":
        users[user_id] = {
            "budget": 0,
            "played": 0,
            "wins": 0,
            "losses": 0
        }
        await query.edit_message_text("🔄 Session réinitialisée.")

# =========================
# BUDGET COMMAND
# =========================

async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if len(context.args) == 0:
        await update.message.reply_text("Usage: /budget 20000")
        return

    try:
        amount = int(context.args[0])
    except:
        await update.message.reply_text("Montant invalide.")
        return

    if user_id not in users:
        users[user_id] = {
            "budget": 0,
            "played": 0,
            "wins": 0,
            "losses": 0
        }

    users[user_id]["budget"] = amount

    stake = int(amount * 0.05)
    stop_loss = int(amount * 0.20)
    target = int(amount * 0.30)

    await update.message.reply_text(
        f"💰 Budget enregistré : {amount} FCFA\n\n"
        f"Mise conseillée : {stake} FCFA\n"
        f"Stop Loss : -{stop_loss} FCFA\n"
        f"Objectif : +{target} FCFA"
    )

# =========================
# MAIN
# =========================

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN non défini dans Railway.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("budget", budget))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot lancé...")
    app.run_polling()

if __name__ == "__main__":
    main()