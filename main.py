import telebot
from telebot import types
import sqlite3
import random
from config import TOKEN, START_BALANCE, DEFAULT_BET

# ==============================
# INITIALISATION BOT
# ==============================

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# ==============================
# CRÉATION TABLE UTILISATEURS
# ==============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER,
    total_wins INTEGER DEFAULT 0,
    total_losses INTEGER DEFAULT 0
)
""")
conn.commit()

# Stockage parties en cours
games = {}

# ==============================
# FONCTION UTILISATEUR
# ==============================

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, balance) VALUES (?, ?)",
            (user_id, START_BALANCE)
        )
        conn.commit()
        return (user_id, START_BALANCE, 0, 0)

    return user

# ==============================
# MENU START
# ==============================

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎯 Jouer")
    markup.add("💰 Balance", "📊 Stats")

    bot.send_message(
        message.chat.id,
        f"🎰 MINES TITAN PRO\n\n💰 Solde: {user[1]} FCFA",
        reply_markup=markup
    )

# ==============================
# BALANCE
# ==============================

@bot.message_handler(func=lambda m: m.text == "💰 Balance")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 Ton solde: {user[1]} FCFA")

# ==============================
# STATS
# ==============================

@bot.message_handler(func=lambda m: m.text == "📊 Stats")
def stats(message):
    user = get_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"📊 STATISTIQUES\n\n"
        f"🏆 Victoires: {user[2]}\n"
        f"💥 Défaites: {user[3]}"
    )

# ==============================
# JOUER
# ==============================

@bot.message_handler(func=lambda m: m.text == "🎯 Jouer")
def play(message):
    user = get_user(message.from_user.id)

    if user[1] < DEFAULT_BET:
        bot.send_message(message.chat.id, "❌ Solde insuffisant.")
        return

    # Retirer mise
    cursor.execute(
        "UPDATE users SET balance = balance - ? WHERE user_id=?",
        (DEFAULT_BET, user[0])
    )
    conn.commit()

    # Générer cases safe (3 mines)
    safe_positions = random.sample(range(25), 22)

    games[user[0]] = {
        "safe": safe_positions,
        "bet": DEFAULT_BET
    }

    markup = types.InlineKeyboardMarkup()
    buttons = []

    for i in range(25):
        buttons.append(
            types.InlineKeyboardButton("⬜", callback_data=str(i))
        )

    for i in range(0, 25, 5):
        markup.row(*buttons[i:i+5])

    bot.send_message(
        message.chat.id,
        f"🎰 Partie lancée\nMise: {DEFAULT_BET} FCFA\nClique une case",
        reply_markup=markup
    )

# ==============================
# CLICK HANDLER
# ==============================

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    game = games.get(user_id)

    if not game:
        return

    position = int(call.data)

    # Si mine
    if position not in game["safe"]:
        cursor.execute(
            "UPDATE users SET total_losses = total_losses + 1 WHERE user_id=?",
            (user_id,)
        )
        conn.commit()

        reveal_board(call, False)
        return

    # Si safe → gain x2
    gain = game["bet"] * 2

    cursor.execute(
        "UPDATE users SET balance = balance + ?, total_wins = total_wins + 1 WHERE user_id=?",
        (gain, user_id)
    )
    conn.commit()

    reveal_board(call, True, gain)

# ==============================
# RÉVÉLER GRILLE
# ==============================

def reveal_board(call, win, gain=0):
    user_id = call.from_user.id
    game = games.get(user_id)

    markup = types.InlineKeyboardMarkup()
    buttons = []

    for i in range(25):
        if i in game["safe"]:
            text = "💎"
        else:
            text = "💣"

        buttons.append(types.InlineKeyboardButton(text, callback_data="x"))

    for i in range(0, 25, 5):
        markup.row(*buttons[i:i+5])

    if win:
        text = f"🏆 GAGNÉ +{gain} FCFA"
    else:
        text = "💥 PERDU"

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# ==============================
# LANCEMENT
# ==============================

bot.infinity_polling()