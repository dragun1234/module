import os
from datetime import datetime
from typing import Any, Optional

LOGS_DIR = "logs"
USER_LOG = os.path.join(LOGS_DIR, "user_inputs.log")
ERROR_LOG = os.path.join(LOGS_DIR, "errors.log")

os.makedirs(LOGS_DIR, exist_ok=True)

def log_user_input(
    user_id: int,
    field: str,
    value: Any,
    update_id: Optional[int] = None,
    event_type: Optional[str] = None
) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_part = f" update_id={update_id}" if update_id is not None else ""
    event_part = f" event={event_type}" if event_type else ""
    with open(USER_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}]{update_part} user_id={user_id}{event_part} field={field} value={value}\n")

def log_error(
    user_id: int,
    field: str,
    error: Any,
    update_id: Optional[int] = None
) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_part = f" update_id={update_id}" if update_id is not None else ""
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}]{update_part} user_id={user_id} field={field} error={error}\n")

def log_entry(utm_code: str, price: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_log_path = os.path.join(LOGS_DIR, "entry_log.txt")
    with open(entry_log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] UTM={utm_code} Price={price}\n")
