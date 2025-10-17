# -*- coding: utf-8 -*-
"""Aggregates all routers used by main_v2 entry point."""

from matunya_bot_final.handlers.start import router as start_router
from matunya_bot_final.handlers.dialogs.handler import router as dialog_router
from matunya_bot_final.handlers.callbacks.navigation.main_menu_callbacks import router as main_menu_router
from matunya_bot_final.handlers.parts_handlers import router as parts_router
from matunya_bot_final.handlers.chatter_handler import router as chatter_router
from matunya_bot_final.handlers.callbacks.dialogs.gpt_dialog_control_handler import router as gpt_dialog_control_router

from matunya_bot_final.help_core.dispatchers.task_1_5.help_handler_1_5 import router as help_router_1_5
#from matunya_bot_final.help_core.dispatchers.theory_dispatcher import theory_router

from matunya_bot_final.handlers.callbacks.task_handlers.group_1_5.task_1_5_router import router as task_1_5_router
from matunya_bot_final.handlers.callbacks.task_handlers.group_1_5.help_handler import router as group_1_5_help_router
from matunya_bot_final.handlers.message_handlers.group_1_5_answer_handler import router as universal_answer_handler
from matunya_bot_final.handlers.callbacks.task_handlers.group_1_5.theory_handler import router as theory_handler_1_5

from matunya_bot_final.handlers.callbacks.task_handlers.task_6_handler import router as task_6_router
from matunya_bot_final.handlers.callbacks.task_handlers.task_7_handler import router as task_7_router
from matunya_bot_final.handlers.callbacks.task_handlers.task_8_handler import router as task_8_router
from matunya_bot_final.handlers.callbacks.task_handlers.task_9_handler import router as task_9_router
from matunya_bot_final.handlers.callbacks.task_handlers.task_10_handler import router as task_10_router
from matunya_bot_final.handlers.callbacks.task_handlers.task_11 import task_11_router
from matunya_bot_final.handlers.message_handlers.task_11_answer_handler import router as task_11_answer_router
from matunya_bot_final.handlers.callbacks.task_handlers.task_12_handler import router as task_12_router
from matunya_bot_final.handlers.callbacks.task_handlers.task_20.task_20_handler import router as task_20_router

from matunya_bot_final.handlers._legacy.user_answer_handler import router as legacy_answer_router
from matunya_bot_final.help_core.dispatchers.help_handler import (
    solution_router as help_solution_router,
)

routers = [
    # Core navigation and menu entry points.
    start_router,
    main_menu_router,
    parts_router,

    # Help flow for tasks 1-5 (legacy architecture still in use).
    help_router_1_5,
    help_solution_router,
    #theory_router,

    # Task 1-5 callbacks and message handlers.
    task_1_5_router,
    group_1_5_help_router,
    universal_answer_handler,
    theory_handler_1_5,

    # GPT-powered conversational handlers.
    dialog_router,
    chatter_router,
    gpt_dialog_control_router,

    # Task-specific callback routers.
    task_6_router,
    task_7_router,
    task_8_router,
    task_9_router,
    task_10_router,
    task_11_router,
    task_11_answer_router,
    task_12_router,
    task_20_router,

    # Legacy fallbacks to be migrated later.
    legacy_answer_router,
]
