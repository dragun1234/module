from typing import Any, Callable, Awaitable, Dict, Optional
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from logger import log_error

class ErrorLoggerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Any], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            user_id: Optional[int] = None
            from_user = getattr(event, 'from_user', None)
            if from_user and hasattr(from_user, 'id'):
                user_id = from_user.id
            else:
                user_id = None
            event_update = data.get('event_update')
            update_id = getattr(event_update, 'update_id', None) if event_update else None
            log_error(user_id or -1, '-', f'{type(e).__name__}: {e}', update_id=update_id)
            raise
