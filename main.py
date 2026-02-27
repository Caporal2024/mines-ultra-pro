import telebot
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "TON_TOKEN_ICI"
ADMIN_ID = 8094967191

bot = telebot.TeleBot(TOKEN)

users = {}

# ==============================
# INITIALISATION UTILISATEUR
# ==============================

def init_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 10000.0,
            "bet": 120.0,
            "mines": 3,
            "grid": ["⬛"] * 25,
            "mines_positions": [],
            "opened": 0,
            "multiplier": 1.00
        }

# ==============================
# MULTIPLICATEUR INTELLIGENT
# ==============================

def calculate_multiplier(opened, mines):
    base = 1 + (opened * (0.15 + mines * 0.02))
    return round(base, 2)

# ==============================
# MENU PRINCIPAL
# ==============================

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("💣 Mines", callback_data="mines"),
        InlineKeyboardButton("⚽ Penalty", callback_data="penalty")
    )
    return markup

# ==============================
# MENU BOMBS
# ==============================

def bombs_menu(selected):
    markup = InlineKeyboardMarkup()
    row = []
    for n in [2,3,5,7]:
        text = f"⭐ {n}" if n == selected else str(n)
        row.append(InlineKeyboardButton(text, callback_data=f"bomb_{n}"))
    markup.row(*row)
    return markup

# ==============================
# BOUTONS MISE
# ==============================

def bet_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("➖", callback_data="bet_minus"),
        InlineKeyboardButton("➕", callback_data="bet_plus")
    )
    return markup

# ==============================
# CRÉER GRILLE
# ==============================

def create_mines(user_id):
    users[user_id]["grid"] = ["⬛"] * 25
    users[user_id]["opened"] = 0
    users[user_id]["multiplier"] = 1.00
    users[user_id]["mines_positions"] = random.sample(
        range(25),
        users[user_id]["mines"]
    )

def mines_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=5)
    for i in range(25):
        markup.insert(
            InlineKeyboardButton(
                users[user_id]["grid"][i],
                callback_data=f"cell_{i}"
            )
        )
    return markup

# ==============================
# START
# ==============================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    init_user(user_id)

    bot.send_message(
        message.chat.id,
        f"👑 PRO MAX\n"
        f"🆔 ID: {user_id}\n"
        f"💰 Bourse: {users[user_id]['balance']:.2f} F\n"
        f"💵 Mise: {users[user_id]['bet']:.2f} F",
        reply_markup=main_menu()
    )

# ==============================
# CALLBACK
# ==============================

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    init_user(user_id)
    data = call.data

    # ---- MINES ----
    if data == "mines":
        bot.edit_message_text(
            f"💣 MINES\n"
            f"💰 Bourse: {users[user_id]['balance']:.2f} F\n"
            f"💵 Mise: {users[user_id]['bet']:.2f} F\n\n"
            f"Choisis bombes :",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=bombs_menu(users[user_id]["mines"])
        )

    elif data.startswith("bomb_"):
        mines_number = int(data.split("_")[1])
        users[user_id]["mines"] = mines_number
        create_mines(user_id)

        bot.edit_message_text(
            f"💣 Mines: {mines_number}\n"
            f"💰 {users[user_id]['balance']:.2f} F\n"
            f"💵 Mise: {users[user_id]['bet']:.2f} F",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=mines_keyboard(user_id)
        )

    elif data.startswith("cell_"):
        index = int(data.split("_")[1])

        if index in users[user_id]["mines_positions"]:
            users[user_id]["grid"][index] = "💣"
            users[user_id]["balance"] -= users[user_id]["bet"]

            bot.edit_message_text(
                f"💥 BOOM\n"
                f"💰 Bourse: {users[user_id]['balance']:.2f} F",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=main_menu()
            )
        else:
            users[user_id]["grid"][index] = "🟦"
            users[user_id]["opened"] += 1
            users[user_id]["multiplier"] = calculate_multiplier(
                users[user_id]["opened"],
                users[user_id]["mines"]
            )

            gain = users[user_id]["bet"] * users[user_id]["multiplier"]
            users[user_id]["balance"] += gain * 0.1

            bot.edit_message_text(
                f"🟦 SAFE\n"
                f"📈 Multiplicateur: x{users[user_id]['multiplier']}\n"
                f"💰 Bourse: {users[user_id]['balance']:.2f} F",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=mines_keyboard(user_id)
            )

    # ---- MODIFIER MISE ----
    elif data == "bet_plus":
        users[user_id]["bet"] += 20

    elif data == "bet_minus":
        if users[user_id]["bet"] > 20:
            users[user_id]["bet"] -= 20

    # ---- PENALTY ----
    elif data == "penalty":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("⬅️", callback_data="shot_left"),
            InlineKeyboardButton("⬆️", callback_data="shot_center"),
            InlineKeyboardButton("➡️", callback_data="shot_right")
        )

        bot.edit_message_text(
            f"⚽ PENALTY\n"
            f"💰 Bourse: {users[user_id]['balance']:.2f} F\n"
            f"💵 Mise: {users[user_id]['bet']:.2f} F",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    elif data.startswith("shot_"):
        directions = ["left","center","right"]
        bot_choice = random.choice(directions)
        player = data.split("_")[1]

        if player == bot_choice:
            users[user_id]["balance"] -= users[user_id]["bet"]
            result = "❌ Arrêt"
        else:
            users[user_id]["balance"] += users[user_id]["bet"]
            result = "⚽ BUT"

        bot.edit_message_text(
            f"{result}\n"
            f"💰 Bourse: {users[user_id]['balance']:.2f} F",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )

print("PRO MAX BOT LANCÉ")
bot.infinity_polling()