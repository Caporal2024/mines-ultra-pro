import telebot
from telebot import types
import sqlite3

# ---------------- CONFIG ----------------

TOKEN = ""  # mets ton token ici
ADMIN_ID = 0  # mets ton ID Telegram ici

bot = telebot.TeleBot(TOKEN)

# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        player_id TEXT,
        active INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- MENU ----------------

def main_menu():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    login = types.KeyboardButton("🔑 Login")
    game = types.KeyboardButton("🎮 Open Game")
    signal = types.KeyboardButton("⏳ Next Signal")

    markup.add(login)
    markup.add(game)
    markup.add(signal)

    return markup

# ---------------- START ----------------

@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "🤖 Welcome\n\nChoose option:",
        reply_markup=main_menu()
    )

# ---------------- LOGIN ----------------

@bot.message_handler(func=lambda m: m.text == "🔑 Login")
def login(message):

    msg = bot.send_message(message.chat.id, "Send Player ID")

    bot.register_next_step_handler(msg, save_player)

def save_player(message):

    user_id = message.from_user.id
    player_id = message.text

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id,player_id,active) VALUES (?,?,0)",
        (user_id, player_id)
    )

    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, "✅ Player ID saved")

# ---------------- CHECK ACCESS ----------------

def check_access(user_id):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT active FROM users WHERE user_id=?", (user_id,))

    result = cursor.fetchone()

    conn.close()

    if result and result[0] == 1:
        return True

    return False

# ---------------- SIGNAL ----------------

@bot.message_handler(func=lambda m: m.text == "⏳ Next Signal")
def signal(message):

    if not check_access(message.from_user.id):

        bot.send_message(message.chat.id, "❌ Ton accès n'est pas activé.")
        return

    bot.send_message(
        message.chat.id,
        "🚀 AVIATOR SIGNAL\n\nBet: 100\nCashout: 2.00x"
    )

# ---------------- OPEN GAME ----------------

@bot.message_handler(func=lambda m: m.text == "🎮 Open Game")
def open_game(message):

    if not check_access(message.from_user.id):

        bot.send_message(message.chat.id, "❌ Ton accès n'est pas activé.")
        return

    bot.send_message(
        message.chat.id,
        "🎮 Open Game\n\nhttps://1win.com"
    )

# ---------------- ADMIN ACTIVATE ----------------

@bot.message_handler(commands=['activate'])
def activate(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        user_id = int(message.text.split()[1])

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET active=1 WHERE user_id=?",
            (user_id,)
        )

        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, "✅ User activated")

    except:

        bot.send_message(message.chat.id, "Usage:\n/activate USER_ID")

# ---------------- USERS LIST ----------------

@bot.message_handler(commands=['users'])
def users(message):

    if message.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id,player_id,active FROM users")

    data = cursor.fetchall()

    conn.close()

    text = "👥 USERS LIST\n\n"

    for u in data:

        status = "ACTIVE" if u[2] == 1 else "WAIT"

        text += f"ID: {u[0]} | Player: {u[1]} | {status}\n"

    bot.send_message(message.chat.id, text)

# ---------------- RUN ----------------

print("Bot started...")

bot.infinity_polling()