import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "TON_TOKEN_ICI"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

GRID_SIZE = 5
MINES = 3

def generate_board():
    board = ["💎"] * 25
    mines_positions = random.sample(range(25), MINES)
    for pos in mines_positions:
        board[pos] = "💣"
    return board

def create_keyboard(board):
    keyboard = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(25):
        buttons.append(InlineKeyboardButton(board[i], callback_data="none"))
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(commands=["start"])
async def start_game(message: types.Message):
    board = generate_board()
    keyboard = create_keyboard(board)
    await message.answer("🎯 Mines 5x5 - Mode 3-5-7 LIVE", reply_markup=keyboard)

if __name__ == "__main__":
    executor.start_polling(dp)