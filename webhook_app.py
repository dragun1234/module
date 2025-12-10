from fastapi import FastAPI, Request, HTTPException, Header
import os
import logging
import asyncio
from aiogram.types import Update
from config import dp, bot

# Импорт handlers чтобы гарантировать регистрацию роутера/хэндлеров
import handlers  # noqa: F401

# IMPORTANT: attach handlers router to dispatcher for webhook runtime
# In `bot.py` you include the router for polling. When running under the
# FastAPI webhook app we must also attach the same router to `dp`, otherwise
# `dp` will have no handlers registered and updates will be "not handled".
try:
    dp.include_router(handlers.router)
except Exception:
    # If router already included or dp is different, ignore the error
    pass

app = FastAPI()

# Basic logging configuration for the webhook app
logging.basicConfig(level=logging.INFO)

# Accept WEBHOOK_SECRET from either WEBHOOK_SECRET or legacy NEW_SECRET env var
WEBHOOK_SECRET = (os.getenv("WEBHOOK_SECRET") or os.getenv("NEW_SECRET") or "").strip()

logger = logging.getLogger(__name__)

# Queue for incoming updates to process asynchronously so webhook returns fast
update_queue: asyncio.Queue = asyncio.Queue(maxsize=200)


async def _worker() -> None:
    """Background worker that processes updates from the queue using the Dispatcher."""
    while True:
        update = await update_queue.get()
        try:
            await dp.feed_update(bot, update)
        except Exception:
            logger.exception("Worker error while processing update")
        finally:
            try:
                update_queue.task_done()
            except Exception:
                pass


@app.on_event("startup")
async def _on_startup() -> None:
    # Start background worker(s)
    asyncio.create_task(_worker())


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
        # Попробуем поставить Update в очередь для фоновой обработки —
        # это позволяет быстро вернуть 200 Telegram и не блокировать webhook.
        update_queue.put_nowait(update)
        return {"ok": True}
    except asyncio.QueueFull:
        # Если очередь переполнена (очень высокая нагрузка), логируем и
        # выполняем обработку синхронно как запасной вариант.
        logger.warning("Update queue is full, processing update synchronously")
        try:
            await dp.feed_update(bot, update)
        except Exception:
            logger.exception("Error while processing update synchronously")
            # Всё равно возвращаем 200, чтобы Telegram не повторял часто.
        return {"ok": True}
