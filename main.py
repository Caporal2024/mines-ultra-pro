import telebot
from telebot import types
import sqlite3

TOKEN = "PUT_YOUR_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

# DATABASE
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    player_id TEXT
)
""")
conn.commit()


# START
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🔑 Login")
    btn2 = types.KeyboardButton("🎮 Open Game")

    markup.add(btn1)
    markup.add(btn2)

    bot.send_message(
        message.chat.id,
        "Welcome to Aviator Predictor 🚀\n\nChoose option:",
        reply_markup=markup
    )


# LOGIN BUTTON
@bot.message_handler(func=lambda message: message.text == "🔑 Login")
def login(message):

    msg = bot.send_message(
        message.chat.id,
        "Send Player ID"
    )

    bot.register_next_step_handler(msg, save_player_id)


# SAVE PLAYER ID
def save_player_id(message):

    player_id = message.text
    user_id = message.from_user.id

    cursor.execute(
        "INSERT INTO users (user_id, player_id) VALUES (?,?)",
        (user_id, player_id)
    )
    conn.commit()

    bot.send_message(
        message.chat.id,
        "✅ Player ID saved"
    )


# OPEN GAME BUTTON
@bot.message_handler(func=lambda message: message.text == "🎮 Open Game")
def open_game(message):

    markup = types.InlineKeyboardMarkup()

    btn = types.InlineKeyboardButton(
        "🚀 Open Aviator",
        url="https://1xbet.com"
    )

    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "Click to open the game",
        reply_markup=markup
    )


print("Bot is running...")
bot.infinity_polling()