from matunya_bot_final.handlers.callbacks.task_handlers.group_1_5.task_1_5_router import (
    router as task_1_5_router,
)
from matunya_bot_final.handlers.callbacks.task_handlers.group_1_5.theory_handler import (
    router as theory_handler_1_5,
)
from matunya_bot_final.handlers.callbacks.task_handlers.group_1_5.help_handler import (
    router as group_1_5_help_router,
)

__all__ = [
    "task_1_5_router",
    "theory_handler_1_5",
    "group_1_5_help_router",
    "all_routers",
]

all_routers = [
    task_1_5_router,
    theory_handler_1_5,
    group_1_5_help_router,
]
