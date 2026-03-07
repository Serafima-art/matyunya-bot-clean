from typing import Dict, Any, List
from matunya_bot_final.utils.display.display import format_number


def build_stoves_q5(task: Dict[str, Any]) -> List[Dict[str, Any]]:

    input_data = task.get("input_data", {})

    a = input_data.get("a")
    b = input_data.get("b")

    # форматирование чисел
    a = format_number(a)
    b = format_number(b)

    text = (
        f"Хозяин выбрал дровяную печь с кожухом вокруг дверцы топки. "
        f"Верхняя часть кожуха выполнена в виде арки, приваренной к передней "
        f"стенке печи по дуге окружности с центром в середине нижней части кожуха.\n\n"
        f"Высота a кожуха равна {a} см., а его ширина b — {b} см.\n\n"
        f"Найди радиус R дуги окружности, образующей арку кожуха.\n"
        f"Ответ дай в сантиметрах."
    )

    return [
        {
            "type": "text",
            "content": text,
        }
    ]
