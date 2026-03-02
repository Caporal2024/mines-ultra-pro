import os
import telebot
import random
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

users = {}

STOP_LOSS = -3000
PROFIT_TARGET = 5000

@app.route('/')
def home():
    return "Mines Ultra Pro Max Running"

# ================= MENU =================

def main_menu(user_id):
    u = users[user_id]
    text = f"""🔥 MINES 5x5 PRO MAX 🔥

💰 Capital: {u['capital']} FCFA
📈 Profit: {u['profit']} FCFA
📉 Perte: {u['loss']} FCFA
"""
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎮 Jouer", callback_data="play"),
        InlineKeyboardButton("⚙️ Paramètres", callback_data="settings")
    )
    markup.row(
        InlineKeyboardButton("📊 Stats", callback_data="stats")
    )
    return text, markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in users:
        users[user_id] = {
            "capital": 10000,
            "profit": 0,
            "loss": 0,
            "bet": 1000,
            "mines_count": 5,
            "game": None
        }
    text, markup = main_menu(user_id)
    bot.send_message(user_id, text, reply_markup=markup)

# ================= SETTINGS =================

def settings_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("💣 3 Mines", callback_data="mines_3"),
        InlineKeyboardButton("💣 5 Mines", callback_data="mines_5"),
        InlineKeyboardButton("💣 7 Mines", callback_data="mines_7")
    )
    markup.row(
        InlineKeyboardButton("💰 Mise 1000", callback_data="bet_1000"),
        InlineKeyboardButton("💰 Mise 2000", callback_data="bet_2000"),
        InlineKeyboardButton("💰 Mise 5000", callback_data="bet_5000")
    )
    markup.row(
        InlineKeyboardButton("⬅ Retour", callback_data="back")
    )
    return markup

# ================= GAME =================

def create_board(mines_count):
    return random.sample(range(25), mines_count)

def generate_grid(revealed, mines):
    markup = InlineKeyboardMarkup()
    for i in range(5):
        row = []
        for j in range(5):
            index = i*5 + j
            if index in revealed:
                text = "💣" if index in mines else "💎"
            else:
                text = "⬜"
            row.append(InlineKeyboardButton(text, callback_data=f"cell_{index}"))
        markup.row(*row)
    markup.row(InlineKeyboardButton("💰 Encaisser", callback_data="cashout"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id
    u = users[user_id]

    # STOP CONDITIONS
    if u["profit"] >= PROFIT_TARGET:
        bot.answer_callback_query(call.id, "🎯 Objectif profit atteint !", show_alert=True)
        return

    if u["profit"] - u["loss"] <= STOP_LOSS:
        bot.answer_callback_query(call.id, "🛑 Stop loss atteint !", show_alert=True)
        return

    if call.data == "play":
        if u["capital"] < u["bet"]:
            bot.answer_callback_query(call.id, "Capital insuffisant", show_alert=True)
            return

        mines = create_board(u["mines_count"])
        u["game"] = {
            "mines": mines,
            "revealed": [],
            "multiplier": 1
        }

        bot.edit_message_text(
            f"💣 Mines lancé !\nMise: {u['bet']} FCFA",
            user_id,
            call.message.message_id,
            reply_markup=generate_grid([], mines)
        )

    elif call.data.startswith("cell_"):
        if not u["game"]:
            return

        index = int(call.data.split("_")[1])
        game = u["game"]

        if index in game["revealed"]:
            return

        game["revealed"].append(index)

        if index in game["mines"]:
            u["capital"] -= u["bet"]
            u["loss"] += u["bet"]
            u["game"] = None

            bot.edit_message_text(
                f"💥 BOOM ! -{u['bet']} FCFA",
                user_id,
                call.message.message_id,
                reply_markup=generate_grid(game["revealed"], game["mines"])
            )
        else:
            game["multiplier"] += 0.4
            bot.edit_message_reply_markup(
                user_id,
                call.message.message_id,
                reply_markup=generate_grid(game["revealed"], game["mines"])
            )

    elif call.data == "cashout":
        game = u["game"]
        if game:
            gain = int(u["bet"] * game["multiplier"])
            u["capital"] += gain
            u["profit"] += gain
            u["game"] = None

            text, markup = main_menu(user_id)
            bot.edit_message_text(
                f"💰 Gain : {gain} FCFA\n\n{text}",
                user_id,
                call.message.message_id,
                reply_markup=markup
            )

    elif call.data == "settings":
        bot.edit_message_text(
            "⚙️ Paramètres",
            user_id,
            call.message.message_id,
            reply_markup=settings_menu()
        )

    elif call.data.startswith("mines_"):
        u["mines_count"] = int(call.data.split("_")[1])
        bot.answer_callback_query(call.id, f"Mines réglées à {u['mines_count']}")

    elif call.data.startswith("bet_"):
        u["bet"] = int(call.data.split("_")[1])
        bot.answer_callback_query(call.id, f"Mise réglée à {u['bet']} FCFA")

    elif call.data == "stats":
        bot.answer_callback_query(
            call.id,
            f"Capital: {u['capital']}\nProfit: {u['profit']}\nPerte: {u['loss']}",
            show_alert=True
        )

    elif call.data == "back":
        text, markup = main_menu(user_id)
        bot.edit_message_text(text, user_id, call.message.message_id, reply_markup=markup)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)