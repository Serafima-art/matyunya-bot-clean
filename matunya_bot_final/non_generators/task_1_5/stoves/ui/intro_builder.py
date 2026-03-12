from typing import Dict, Any, List
from matunya_bot_final.utils.display.display import format_number


def build_stoves_intro(variant: Dict[str, Any]) -> List[Dict[str, Any]]:

    room = variant.get("room_context", {})

    length = room.get("length")
    width = room.get("width")
    height = room.get("height")
    door_width = room.get("door_width_cm")
    door_height = room.get("door_height_m")

    cable_cost = room.get("electric_install_cost")

    # форматирование чисел
    length = format_number(length)
    width = format_number(width)
    height = format_number(height)
    door_width = format_number(door_width)
    door_height = format_number(door_height)
    cable_cost = format_number(cable_cost)

    text = (
        f"Владелец загородного дома оборудует баню с парным отделением.\n\n"
        f"Размеры парной: <i>длина</i> <b>{length} м</b>, <i>ширина</i> <b>{width} м</b>, <i>высота</i> <b>{height} м</b>. "
        f"Окна в помещении отсутствуют, вход осуществляется через дверной проём "
        f"<i>шириной</i> <b>{door_width} см</b> и <i>высотой</i> <b>{door_height} м</b>.\n\n"
        f"Для обогрева можно выбрать электрическую или дровяную печь. "
        f"В таблице приведены характеристики трёх моделей: <b>тип печи, "
        f"объём помещения, на который она рассчитана, масса и стоимость</b>.\n\n"
        f"Установка дровяной печи дополнительных затрат не потребует. "
        f"Для подключения электрической печи необходимо провести специальный кабель. "
        f"Стоимость работ составит <b>{cable_cost} рублей</b>."
    )

    return [
        {
            "type": "text",
            "content": text,
        }
    ]
