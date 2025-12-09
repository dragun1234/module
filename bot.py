# bot.py
import asyncio
import logging
from config import bot, dp
import handlers
from logger import log_error
from user_input_logger_middleware import UserInputLoggerMiddleware
from error_logger_middleware import ErrorLoggerMiddleware

logging.basicConfig(level=logging.INFO)

# Регистрируем роутер из handlers
dp.include_router(handlers.router)

dp.message.middleware(UserInputLoggerMiddleware())
dp.callback_query.middleware(UserInputLoggerMiddleware())
dp.message.middleware(ErrorLoggerMiddleware())
dp.callback_query.middleware(ErrorLoggerMiddleware())

async def on_error(update, exception):
    user_id = None
    try:
        if hasattr(update, 'message') and update.message:
            user_id = update.message.from_user.id
        elif hasattr(update, 'callback_query') and update.callback_query:
            user_id = update.callback_query.from_user.id
    except Exception:
        user_id = 'unknown'
    log_error(user_id, 'global', f'{type(exception).__name__}: {exception}')
    return True  # чтобы не падал бот

async def main():
    logging.info("Бот запущен.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
