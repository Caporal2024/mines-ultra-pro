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

@app.route('/')
def home():
    return "Mines Ultra Pro Running"

# ================= MENU =================

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎮 Jouer Mines", callback_data="play"),
        InlineKeyboardButton("💰 Capital", callback_data="capital")
    )
    markup.row(
        InlineKeyboardButton("📊 Stats", callback_data="stats")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in users:
        users[user_id] = {
            "capital": 10000,
            "profit": 0,
            "loss": 0,
            "game": None
        }
    bot.send_message(user_id, "🔥 MINES ULTRA PRO 🔥", reply_markup=main_menu())

# ================= MINES GAME =================

def create_board():
    mines = random.sample(range(25), 5)
    return mines

def generate_grid(revealed=[], mines=[]):
    markup = InlineKeyboardMarkup()
    for i in range(5):
        row = []
        for j in range(5):
            index = i*5 + j
            if index in revealed:
                if index in mines:
                    text = "💣"
                else:
                    text = "💎"
            else:
                text = "⬜"
            row.append(InlineKeyboardButton(text, callback_data=f"cell_{index}"))
        markup.row(*row)
    markup.row(InlineKeyboardButton("💰 Encaisser", callback_data="cashout"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id

    if call.data == "play":
        mines = create_board()
        users[user_id]["game"] = {
            "mines": mines,
            "revealed": [],
            "multiplier": 1
        }
        bot.edit_message_text("💣 Mines lancé !",
                              user_id,
                              call.message.message_id,
                              reply_markup=generate_grid([], mines))

    elif call.data.startswith("cell_"):
        index = int(call.data.split("_")[1])
        game = users[user_id]["game"]

        if not game:
            return

        if index in game["revealed"]:
            return

        game["revealed"].append(index)

        if index in game["mines"]:
            users[user_id]["capital"] -= 1000
            users[user_id]["loss"] += 1000
            users[user_id]["game"] = None
            bot.edit_message_text("💥 BOOM ! -1000 FCFA",
                                  user_id,
                                  call.message.message_id,
                                  reply_markup=generate_grid(game["revealed"], game["mines"]))
        else:
            game["multiplier"] += 0.5
            bot.edit_message_reply_markup(user_id,
                                          call.message.message_id,
                                          reply_markup=generate_grid(game["revealed"], game["mines"]))

    elif call.data == "cashout":
        game = users[user_id]["game"]
        if game:
            gain = int(1000 * game["multiplier"])
            users[user_id]["capital"] += gain
            users[user_id]["profit"] += gain
            users[user_id]["game"] = None
            bot.edit_message_text(f"💰 Gain : {gain} FCFA",
                                  user_id,
                                  call.message.message_id,
                                  reply_markup=main_menu())

    elif call.data == "capital":
        capital = users[user_id]["capital"]
        bot.answer_callback_query(call.id, f"Capital: {capital} FCFA", show_alert=True)

    elif call.data == "stats":
        profit = users[user_id]["profit"]
        loss = users[user_id]["loss"]
        bot.answer_callback_query(call.id,
                                  f"Profit: {profit} FCFA\nPerte: {loss} FCFA",
                                  show_alert=True)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)