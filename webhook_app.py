from fastapi import FastAPI, Request, HTTPException, Header
import os
import logging
from aiogram.types import Update
from config import dp, bot

# Импорт handlers чтобы гарантировать регистрацию роутера/хэндлеров
import handlers  # noqa: F401

app = FastAPI()

# Basic logging configuration for the webhook app
logging.basicConfig(level=logging.INFO)

# Accept WEBHOOK_SECRET from either WEBHOOK_SECRET or legacy NEW_SECRET env var
WEBHOOK_SECRET = (os.getenv("WEBHOOK_SECRET") or os.getenv("NEW_SECRET") or "").strip()

logger = logging.getLogger(__name__)


@app.get("/")
async def root():
    return {"ok": True, "service": "insurance-bot webhook"}


@app.post("/webhook/{secret}")
async def telegram_webhook(
    secret: str,
    request: Request,
    tg_secret: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    expected = WEBHOOK_SECRET
    if not expected:
        raise HTTPException(status_code=500, detail="WEBHOOK_SECRET not set")

    # Accept either URL secret or Telegram header secret_token
    if secret.strip() != expected and (tg_secret or "").strip() != expected:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        data = await request.json()
    except Exception as e:
        logger.exception("Failed to parse request JSON: %s", e)
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        # Для aiogram v3 корректно валидировать Update через Pydantic model
        # и передать контекст с ботом, чтобы внутри Update были методы бота.
        update = Update.model_validate(data, context={"bot": bot})
    except Exception as e:
        logger.exception("Failed to build Update object: %s", e)
        raise HTTPException(status_code=400, detail="Invalid Update payload")

    try:
        # Передаём Update в диспетчер для обработки зарегистрированными хэндлерами.
        # В aiogram 3.18 корректный вызов для вебхуков — feed_update(bot, update)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.exception("Error while processing update: %s", e)
        # Не поднимаем ошибку, чтобы Telegram получил 200, но логируем
        return {"ok": False, "error": str(e)}

    return {"ok": True}
