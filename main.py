import os
import telebot
import random
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==================================================
# 🔐 TOKEN depuis Railway (NE PAS METTRE ICI)
# ==================================================
TOKEN = os.getenv("TOKEN_MAIN")

if not TOKEN:
    raise ValueError("TOKEN_MAIN manquant dans Railway Variables.")

bot = telebot.TeleBot(TOKEN)

# ==================================================
# 📊 STOCKAGE UTILISATEURS
# ==================================================
users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 1000,
            "loss_streak": 0,
            "profit": 0
        }
    return users[user_id]

# ==================================================
# 🤖 IA INTELLIGENTE
# ==================================================
def ai_advice(user):
    if user["loss_streak"] >= 2:
        return "🛑 IA: 2 pertes consécutives. Arrête maintenant."
    if user["profit"] >= 300:
        return "💰 IA: Objectif atteint. Sécurise ton gain."
    return "✅ IA: Situation stable."

# ==================================================
# 🎨 MENU CASINO PREMIUM
# ==================================================
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🚀 LUCKY JET LIVE"))
    markup.row(KeyboardButton("💣 MINES 5x5 LIVE"))
    markup.row(KeyboardButton("📊 IA STATUT"))
    markup.row(KeyboardButton("💰 SOLDE"))

    bot.send_message(
        message.chat.id,
        "🎰 CASINO PREMIUM\nBienvenue !",
        reply_markup=markup
    )

# ==================================================
# 💰 SOLDE
# ==================================================
@bot.message_handler(func=lambda m: m.text == "💰 SOLDE")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"💰 Solde: {user['balance']} FCFA\n📈 Profit: {user['profit']} FCFA"
    )

# ==================================================
# 🚀 LUCKY JET LIVE RAPIDE
# ==================================================
@bot.message_handler(func=lambda m: m.text == "🚀 LUCKY JET LIVE")
def luckyjet(message):
    user = get_user(message.from_user.id)

    bet = 100
    if user["balance"] < bet:
        bot.send_message(message.chat.id, "❌ Solde insuffisant.")
        return

    user["balance"] -= bet

    crash = round(random.uniform(1.10, 3.00), 2)
    msg = bot.send_message(message.chat.id, "🚀 Décollage...")

    multiplier = 1.00
    while multiplier < crash:
        multiplier += 0.07  # plus rapide
        bot.edit_message_text(
            f"🚀 {round(multiplier,2)}x",
            message.chat.id,
            msg.message_id
        )
        time.sleep(0.15)

    bot.edit_message_text(
        f"💥 CRASH à {crash}x",
        message.chat.id,
        msg.message_id
    )

    # Auto cashout x1.40
    if crash >= 1.40:
        gain = int(bet * 1.40)
        profit = gain - bet
        user["balance"] += gain
        user["profit"] += profit
        user["loss_streak"] = 0
        bot.send_message(message.chat.id, f"✅ Gain: +{profit} FCFA")
    else:
        user["loss_streak"] += 1
        bot.send_message(message.chat.id, "❌ Perdu.")

# ==================================================
# 💣 MINES 5x5 LIVE INTERACTIF
# ==================================================
@bot.message_handler(func=lambda m: m.text == "💣 MINES 5x5 LIVE")
def mines(message):
    user_id = message.from_user.id
    mines_positions = random.sample(range(25), 3)

    users[user_id]["mines"] = mines_positions
    users[user_id]["safe_clicks"] = 0

    keyboard = InlineKeyboardMarkup(row_width=5)

    for i in range(25):
        keyboard.add(
            InlineKeyboardButton("⬜", callback_data=f"cell_{i}")
        )

    bot.send_message(
        message.chat.id,
        "💣 Clique une case :",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("cell_"))
def handle_click(call):
    user_id = call.from_user.id
    user = get_user(user_id)

    index = int(call.data.split("_")[1])

    if index in user.get("mines", []):
        user["loss_streak"] += 1
        bot.edit_message_text(
            "💥 BOOM ! Tu as perdu.",
            call.message.chat.id,
            call.message.message_id
        )
    else:
        user["safe_clicks"] += 1
        bot.answer_callback_query(call.id, "💎 Safe !")

        if user["safe_clicks"] >= 2:
            gain = 80
            user["balance"] += gain
            user["profit"] += gain
            user["loss_streak"] = 0
            bot.edit_message_text(
                f"💎 2 cases safe ! Gain: +{gain} FCFA",
                call.message.chat.id,
                call.message.message_id
            )

# ==================================================
# 📊 IA STATUT
# ==================================================
@bot.message_handler(func=lambda m: m.text == "📊 IA STATUT")
def ia_status(message):
    user = get_user(message.from_user.id)
    advice = ai_advice(user)
    bot.send_message(message.chat.id, advice)

# ==================================================
# ▶ LANCEMENT
# ==================================================
bot.infinity_polling()