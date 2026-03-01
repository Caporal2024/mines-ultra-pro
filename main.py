import telebot
import random
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import *
from config import *

TOKEN = ""  # ← Mets ton token ici
bot = telebot.TeleBot(TOKEN)

mines_games = {}
jet_games = {}

# ================= MENU =================

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    house = get_house()

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💣 MINES PRO", callback_data="mines"),
        InlineKeyboardButton("✈️ LUCKY JET", callback_data="jet")
    )
    markup.add(
        InlineKeyboardButton("📊 STATS", callback_data="stats"),
        InlineKeyboardButton("🏦 CAPITAL", callback_data="capital")
    )

    bot.send_message(
        message.chat.id,
        f"🎰 ULTRA CASINO\n\n"
        f"💰 Solde : {user['balance']}\n"
        f"🏦 Capital : {house}",
        reply_markup=markup
    )

# ================= LUCKY JET =================

@bot.callback_query_handler(func=lambda call: call.data == "jet")
def start_jet(call):
    user_id = call.from_user.id
    user = get_user(user_id)

    if user["balance"] < BET_AMOUNT:
        bot.answer_callback_query(call.id, "Solde insuffisant")
        return

    user["balance"] -= BET_AMOUNT
    update_user(user_id, user)
    update_house(BET_AMOUNT)

    crash = round(random.uniform(JET_MIN, JET_MAX), 2)

    jet_games[user_id] = {
        "crash": crash,
        "current": 1.0,
        "cashed": False
    }

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💰 CASHOUT", callback_data="jet_cashout"))

    msg = bot.send_message(
        call.message.chat.id,
        "✈️ LUCKY JET\n🚀 x1.00",
        reply_markup=markup
    )

    jet_games[user_id]["message_id"] = msg.message_id

    while user_id in jet_games:
        game = jet_games[user_id]

        if game["cashed"]:
            break

        time.sleep(JET_SPEED)
        game["current"] += JET_STEP

        if game["current"] >= game["crash"]:
            bot.edit_message_text(
                f"💥 CRASH à x{game['crash']}",
                call.message.chat.id,
                game["message_id"]
            )
            user["losses"] += 1
            update_user(user_id, user)
            del jet_games[user_id]
            return

        try:
            bot.edit_message_text(
                f"✈️ LUCKY JET\n🚀 x{game['current']:.2f}",
                call.message.chat.id,
                game["message_id"],
                reply_markup=markup
            )
        except:
            break

@bot.callback_query_handler(func=lambda call: call.data == "jet_cashout")
def jet_cashout(call):
    user_id = call.from_user.id
    user = get_user(user_id)

    if user_id not in jet_games:
        return

    game = jet_games[user_id]
    game["cashed"] = True

    win = int(BET_AMOUNT * game["current"])

    user["balance"] += win
    user["wins"] += 1
    update_user(user_id, user)
    update_house(-win)

    bot.edit_message_text(
        f"🏆 CASHOUT à x{game['current']:.2f}\n💰 Gain : {win}",
        call.message.chat.id,
        game["message_id"]
    )

    del jet_games[user_id]

# ================= MINES =================

@bot.callback_query_handler(func=lambda call: call.data == "mines")
def start_mines(call):
    user_id = call.from_user.id
    user = get_user(user_id)

    if user["balance"] < BET_AMOUNT:
        bot.answer_callback_query(call.id, "Solde insuffisant")
        return

    user["balance"] -= BET_AMOUNT
    update_user(user_id, user)
    update_house(BET_AMOUNT)

    bombs = random.sample(range(25), MINES_BOMBS)

    mines_games[user_id] = {
        "bombs": bombs,
        "revealed": [],
        "multiplier": 1.0
    }

    send_mines_grid(call.message.chat.id, user_id)

def send_mines_grid(chat_id, user_id, message_id=None):
    game = mines_games[user_id]
    markup = InlineKeyboardMarkup()

    for row in range(5):
        buttons = []
        for col in range(5):
            index = row * 5 + col
            text = "💎" if index in game["revealed"] else "⬜"
            buttons.append(
                InlineKeyboardButton(text, callback_data=f"mine_{index}")
            )
        markup.row(*buttons)

    markup.row(
        InlineKeyboardButton("💰 CASHOUT", callback_data="cashout")
    )

    text = f"💣 MINES\n📈 Multiplier : x{game['multiplier']:.2f}"

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else:
        msg = bot.send_message(chat_id, text, reply_markup=markup)
        game["message_id"] = msg.message_id

@bot.callback_query_handler(func=lambda call: call.data.startswith("mine_"))
def mine_click(call):
    user_id = call.from_user.id
    user = get_user(user_id)

    if user_id not in mines_games:
        return

    game = mines_games[user_id]
    index = int(call.data.split("_")[1])

    if index in game["bombs"]:
        user["losses"] += 1
        update_user(user_id, user)
        reveal_mines(call.message.chat.id, user_id)
        del mines_games[user_id]
    else:
        game["revealed"].append(index)
        game["multiplier"] += 0.3
        send_mines_grid(call.message.chat.id, user_id, game["message_id"])

def reveal_mines(chat_id, user_id):
    game = mines_games[user_id]

    for bomb in game["bombs"]:
        game["revealed"].append(bomb)
        send_mines_grid(chat_id, user_id, game["message_id"])
        time.sleep(0.3)

    bot.edit_message_text("💥 GAME OVER", chat_id, game["message_id"])

@bot.callback_query_handler(func=lambda call: call.data == "cashout")
def cashout(call):
    user_id = call.from_user.id
    user = get_user(user_id)

    if user_id not in mines_games:
        return

    game = mines_games[user_id]
    win = int(BET_AMOUNT * game["multiplier"])

    user["balance"] += win
    user["wins"] += 1
    update_user(user_id, user)
    update_house(-win)

    bot.edit_message_text(
        f"🏆 CASHOUT\n💰 Gain : {win}",
        call.message.chat.id,
        game["message_id"]
    )

    del mines_games[user_id]

# ================= STATS =================

@bot.callback_query_handler(func=lambda call: call.data == "stats")
def stats(call):
    user = get_user(call.from_user.id)
    bot.send_message(
        call.message.chat.id,
        f"📊 STATS\n\n"
        f"💰 Balance : {user['balance']}\n"
        f"🏆 Wins : {user['wins']}\n"
        f"💥 Losses : {user['losses']}"
    )

# ================= CAPITAL =================

@bot.callback_query_handler(func=lambda call: call.data == "capital")
def capital(call):
    house = get_house()
    bot.send_message(call.message.chat.id, f"🏦 Capital Casino : {house}")

bot.infinity_polling()