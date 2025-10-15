from matunya_bot_final.handlers.callbacks.task_handlers.task_11 import (
    all_routers as task_11_routers,
)
from matunya_bot_final.handlers.callbacks.task_handlers.task_20 import (
    task_20_handler,
)

all_task_handlers = [
    *task_11_routers,
    task_20_handler.router,
]

__all__ = [
    "all_task_handlers",
    "task_20_handler",
]
