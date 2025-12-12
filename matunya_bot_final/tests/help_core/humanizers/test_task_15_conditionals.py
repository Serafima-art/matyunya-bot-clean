from matunya_bot_final.help_core.humanizers.template_humanizers.task_15_humanizer import (
    _apply_conditionals,
)


def test_if_true_block_shown():
    template = "{if flag}AAA{endif}"
    assert _apply_conditionals(template, {"flag": True}) == "AAA"


def test_if_false_block_hidden():
    template = "{if flag}AAA{endif}"
    assert _apply_conditionals(template, {"flag": False}) == ""


def test_if_not_false_block_shown():
    template = "{if not flag}BBB{endif}"
    assert _apply_conditionals(template, {"flag": False}) == "BBB"


def test_if_and_if_not_coexist():
    template = "{if flag}AAA{endif}{if not flag}BBB{endif}"
    assert _apply_conditionals(template, {"flag": True}) == "AAA"
    assert _apply_conditionals(template, {"flag": False}) == "BBB"


def test_regression_step_three_not_empty_when_small_requested():
    template = (
        "Step 3.\n"
        "{if is_find_big}"
        "BIG"
        "{endif}"
        "{if not is_find_big}"
        "Area {target_area_name} uses {target_base_parts} parts. "
        "{target_area_name} = {one_part_val} * {target_base_parts} = {other_small_area_val}"
        "{endif}"
    )
    context = {
        "is_find_big": False,
        "target_area_name": "S(BCD)",
        "target_base_parts": "5",
        "one_part_val": "5",
        "other_small_area_val": "25",
    }
    processed = _apply_conditionals(template, context)
    rendered = processed.format(**context)
    assert "Area S(BCD) uses 5 parts." in rendered
    assert "25" in rendered
