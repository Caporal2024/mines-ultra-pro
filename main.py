import os
import logging
import random
import string
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def generate_coupon_code():
    prefix = "CPN"
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}-{random_part}"

def analyse_coupon(mise, cotes):
    cote_totale = 1
    for cote in cotes:
        cote_totale *= cote

    gain = mise * cote_totale
    proba_implicite = 1 / cote_totale
    proba_reelle = proba_implicite * 1.15  # ajustement interne
    ev = (proba_reelle * gain) - ((1 - proba_reelle) * mise)

    return cote_totale, gain, proba_implicite, ev

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🎟 Générer Code Coupon"],
        ["📊 Analyse Coupon"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🤖 COUPON AI PRO\n\nChoisissez une option :",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎟 Générer Code Coupon":
        code = generate_coupon_code()

        equipes = [
            {"nom": "Real Madrid", "cote": 1.80},
            {"nom": "Manchester City", "cote": 1.65},
            {"nom": "Bayern Munich", "cote": 1.75},
        ]

        cote_totale = 1
        message = f"🎟 CODE COUPON : {code}\n\n"

        for equipe in equipes:
            message += f"✅ {equipe['nom']} ({equipe['cote']})\n"
            cote_totale *= equipe["cote"]

        message += f"\n📈 Cote totale : {round(cote_totale,2)}"

        await update.message.reply_text(message)

    elif text == "📊 Analyse Coupon":
        mise = 2000
        cotes = [1.80, 1.65, 1.75]

        cote_totale, gain, proba_implicite, ev = analyse_coupon(mise, cotes)

        message = (
            f"📊 Analyse Coupon\n\n"
            f"Mise : {mise} FCFA\n"
            f"Cote totale : {round(cote_totale,2)}\n"
            f"Gain potentiel : {round(gain,2)} FCFA\n"
            f"Probabilité implicite : {round(proba_implicite*100,2)}%\n"
            f"EV estimé : {round(ev,2)} FCFA\n"
        )

        if ev > 0:
            message += "\n✅ Coupon validé"
        else:
            message += "\n⚠️ Risque élevé"

        await update.message.reply_text(message)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()