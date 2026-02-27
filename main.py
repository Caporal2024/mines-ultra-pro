import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = "TON_TOKEN_ICI"

async def main():
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())