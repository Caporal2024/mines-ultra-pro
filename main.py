import os
import telebot
import random
import sqlite3
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

DB_FILE = "mines.db"
STOP_LOSS = -3000
PROFIT_TARGET = 5000

# ================= DATABASE =================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            capital INTEGER,
            profit INTEGER,
            loss INTEGER,
            bet INTEGER,
            mines INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()

    if not row:
        c.execute("INSERT INTO users VALUES (?,10000,0,0,1000,5)", (user_id,))
        conn.commit()
        conn.close()
        return {"capital":10000,"profit":0,"loss":0,"bet":1000,"mines":5}

    conn.close()
    return {
        "capital":row[1],
        "profit":row[2],
        "loss":row[3],
        "bet":row[4],
        "mines":row[5]
    }

def update_user(user_id, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE users SET capital=?, profit=?, loss=?, bet=?, mines=?
        WHERE user_id=?
    """,(data["capital"],data["profit"],data["loss"],data["bet"],data["mines"],user_id))
    conn.commit()
    conn.close()

# ================= MENU =================

def main_menu_text(u):
    return f"""🔥 MINES 5x5 PRO MAX 🔥

💰 Capital: {u['capital']} FCFA
📈 Profit: {u['profit']} FCFA
📉 Perte: {u['loss']} FCFA
"""

def main_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎮 Jouer", callback_data="play"),
        InlineKeyboardButton("⚙️ Paramètres", callback_data="settings")
    )
    markup.row(
        InlineKeyboardButton("📊 Stats", callback_data="stats")
    )
    return markup

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
    markup.row(InlineKeyboardButton("⬅ Retour", callback_data="back"))
    return markup

# ================= GAME MEMORY =================

games = {}

def create_board(mines_count):
    return random.sample(range(25), mines_count)

def calculate_multiplier(mines, opened):
    total_cells = 25
    safe_cells = total_cells - mines
    return round((safe_cells / (safe_cells - opened)), 2)

def generate_grid(revealed, mines):
    markup = InlineKeyboardMarkup()
    for i in range(5):
        row = []
        for j in range(5):
            index = i*5+j
            if index in revealed:
                text = "💣" if index in mines else "💎"
            else:
                text = "⬜"
            row.append(InlineKeyboardButton(text, callback_data=f"cell_{index}"))
        markup.row(*row)
    markup.row(InlineKeyboardButton("💰 Encaisser", callback_data="cashout"))
    return markup

# ================= HANDLERS =================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    u = get_user(user_id)
    bot.send_message(user_id, main_menu_text(u), reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id
    u = get_user(user_id)

    if call.data == "play":
        if u["capital"] < u["bet"]:
            bot.answer_callback_query(call.id, "Capital insuffisant", show_alert=True)
            return

        mines_positions = create_board(u["mines"])
        games[user_id] = {
            "mines": mines_positions,
            "revealed": []
        }

        bot.edit_message_text(
            f"""💰 Capital: {u['capital']} FCFA
💣 Mines: {u['mines']}
🎯 Mise: {u['bet']} FCFA
📈 Multiplicateur: x1.0""",
            user_id,
            call.message.message_id,
            reply_markup=generate_grid([], mines_positions)
        )

    elif call.data.startswith("cell_"):
        if user_id not in games:
            return

        index = int(call.data.split("_")[1])
        game = games[user_id]

        if index in game["revealed"]:
            return

        game["revealed"].append(index)

        if index in game["mines"]:
            u["capital"] -= u["bet"]
            u["loss"] += u["bet"]
            update_user(user_id, u)

            bot.edit_message_text(
                f"💥 BOOM ! -{u['bet']} FCFA",
                user_id,
                call.message.message_id,
                reply_markup=generate_grid(game["revealed"], game["mines"])
            )
            del games[user_id]
        else:
            multiplier = calculate_multiplier(u["mines"], len(game["revealed"]))
            bot.edit_message_text(
                f"""💰 Capital: {u['capital']} FCFA
💣 Mines: {u['mines']}
🎯 Mise: {u['bet']} FCFA
📈 Multiplicateur: x{multiplier}""",
                user_id,
                call.message.message_id,
                reply_markup=generate_grid(game["revealed"], game["mines"])
            )

    elif call.data == "cashout":
        if user_id not in games:
            return

        game = games[user_id]
        multiplier = calculate_multiplier(u["mines"], len(game["revealed"]))
        gain = int(u["bet"] * multiplier)

        u["capital"] += gain
        u["profit"] += gain
        update_user(user_id, u)

        del games[user_id]

        bot.edit_message_text(
            f"💰 Gain : {gain} FCFA\n\n"+main_menu_text(u),
            user_id,
            call.message.message_id,
            reply_markup=main_menu_markup()
        )

    elif call.data == "settings":
        bot.edit_message_text("⚙️ Paramètres", user_id, call.message.message_id, reply_markup=settings_menu())

    elif call.data.startswith("mines_"):
        u["mines"] = int(call.data.split("_")[1])
        update_user(user_id, u)
        bot.answer_callback_query(call.id, "Mines mises à jour")

    elif call.data.startswith("bet_"):
        u["bet"] = int(call.data.split("_")[1])
        update_user(user_id, u)
        bot.answer_callback_query(call.id, "Mise mise à jour")

    elif call.data == "stats":
        bot.answer_callback_query(
            call.id,
            f"Capital: {u['capital']}\nProfit: {u['profit']}\nPerte: {u['loss']}",
            show_alert=True
        )

    elif call.data == "back":
        bot.edit_message_text(main_menu_text(u), user_id, call.message.message_id, reply_markup=main_menu_markup())

# ================= RUN =================

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    init_db()
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)