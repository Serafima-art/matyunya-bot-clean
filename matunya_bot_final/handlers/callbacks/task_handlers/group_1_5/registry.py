from .subtypes.paper.loader import load_paper_variant
from .subtypes.paper.overview import send_overview_block_paper
from .subtypes.paper.focused import send_focused_task_block_paper

from .subtypes.stoves.loader import load_stoves_variant
from .subtypes.stoves.overview import send_overview_block_stoves
from .subtypes.stoves.focused import send_focused_task_block_stoves

from .subtypes.apartments.loader import load_apartments_variant
from .subtypes.apartments.overview import send_overview_block_apartments
from .subtypes.apartments.focused import send_focused_task_block_apartments


TASK_1_5_REGISTRY = {
    "paper": {
        "loader": load_paper_variant,
        "overview": send_overview_block_paper,
        "focused": send_focused_task_block_paper,
    },
    "stoves": {
        "loader": load_stoves_variant,
        "overview": send_overview_block_stoves,
        "focused": send_focused_task_block_stoves,
    },
    "apartments": {
        "loader": load_apartments_variant,
        "overview": send_overview_block_apartments,
        "focused": send_focused_task_block_apartments,
    }
}
