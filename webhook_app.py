from fastapi import FastAPI, Request, HTTPException
import os
import logging
from aiogram.types import Update
from config import dp, bot

# Импорт handlers чтобы гарантировать регистрацию роутера/хэндлеров
import handlers  # noqa: F401

app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "CHANGE_ME")

logger = logging.getLogger(__name__)


@app.get("/")
async def root():
    return {"ok": True, "service": "insurance-bot webhook"}


@app.post("/webhook/{secret}")
async def telegram_webhook(secret: str, request: Request):
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        data = await request.json()
    except Exception as e:
        logger.exception("Failed to parse request JSON: %s", e)
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        update = Update(**data)
    except Exception as e:
        logger.exception("Failed to build Update object: %s", e)
        raise HTTPException(status_code=400, detail="Invalid Update payload")

    try:
        # Передаём Update в диспетчер для обработки зарегистрированными хэндлерами
        await dp.process_update(update)
    except Exception as e:
        logger.exception("Error while processing update: %s", e)
        # Не поднимаем ошибку, чтобы Telegram получил 200, но логируем
        return {"ok": False, "error": str(e)}

    return {"ok": True}
