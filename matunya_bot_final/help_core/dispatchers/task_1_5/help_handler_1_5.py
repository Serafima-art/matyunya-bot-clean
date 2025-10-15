"""Dispatcher metadata for task group 1–5 help flows.

Legacy router is kept minimal; actual handlers live in
``handlers.callbacks.task_handlers.group_1_5.help_handler``.
"""

from __future__ import annotations

import logging
from aiogram import Router

from matunya_bot_final.help_core.solvers.task_1_5.tires import (
    tires_q1_solver,
    tires_q2_solver,
    tires_q3_solver,
    tires_q4_solver,
    tires_q5_solver,
    tires_q6_solver,
)

logger = logging.getLogger(__name__)

router = Router(name="help_handler_1_5")

SOLVER_DISPATCHER = {
    1: tires_q1_solver.solve,
    2: tires_q2_solver.solve,
    3: tires_q3_solver.solve,
    4: tires_q4_solver.solve,
    5: tires_q5_solver.solve,
    6: tires_q6_solver.solve,
}


__all__ = [
    "router",
    "SOLVER_DISPATCHER",
]
