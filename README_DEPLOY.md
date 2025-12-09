# Deploy to Render (webhook mode)

This document contains minimal steps to deploy this bot to Render.com using webhooks.

1) Files added
- `webhook_app.py` — FastAPI app that receives Telegram updates and forwards them to aiogram `Dispatcher`.
- `Procfile` — start command for Render.
- `.gitignore` — (see repo) to avoid committing secrets.

2) Environment variables to set on Render
- `BOT_TOKEN` — your Telegram bot token
- `USE_WEBHOOK` — set to `1` (informational; not required by `webhook_app`)
- `WEBHOOK_SECRET` — a long random string used in webhook path
- `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `CHANNEL_ID` — if you use email/channel features

3) Render settings
- Service type: Web Service
- Branch: your branch (e.g. `main`)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn webhook_app:app --host 0.0.0.0 --port $PORT`

4) Setting Telegram webhook
- Webhook URL: `https://<your-service>.onrender.com/webhook/<WEBHOOK_SECRET>`
- Use the following API call (replace placeholders):
```
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<RENDER_HOST>/webhook/<WEBHOOK_SECRET>
```

5) Notes
- Do NOT commit `.env` containing `BOT_TOKEN` to the repo.
- If you experience timeouts or blocking behavior when sending email, consider making `send_email` non-blocking or using a background worker.
