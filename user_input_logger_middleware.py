from typing import Any, Callable, Awaitable, Dict, Optional
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update
from logger import log_user_input

class UserInputLoggerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Any], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        update: Optional[Update] = data.get('event_update') or data.get('update')
        update_id = getattr(update, 'update_id', None)
        user_id = None
        field = None
        value = None
        event_type = None
        if hasattr(event, 'from_user'):
            user_id = event.from_user.id
        if hasattr(event, 'text'):
            value = event.text
            event_type = 'message'
        if hasattr(event, 'data'):
            value = event.data
            event_type = 'callback_query'
        if hasattr(event, 'state') and event.state:
            try:
                state_str = str(await event.state.get_state())
                field = state_str.split(':')[-1]
            except Exception:
                field = None
        if user_id and value:
            log_user_input(user_id, field or '-', value, update_id=update_id, event_type=event_type)
        return await handler(event, data)
