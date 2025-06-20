# bot.py
import asyncio
import logging
from config import bot, dp
import handlers

logging.basicConfig(level=logging.INFO)

# Регистрируем роутер из handlers
dp.include_router(handlers.router)

async def main():
    logging.info("Бот запущен.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
