from . import task_20_handler

__all__ = [
    "task_20_handler",
    "task_20_router",
    "all_routers",
]

task_20_router = task_20_handler.router

all_routers = [
    task_20_router,
]
