# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, Any


def build_q4_text(task: Dict[str, Any]) -> str:
    """
    Формирует текст вопроса Q4 (скидки).
    Данные берутся из solution_data.
    """

    narrative = task.get("narrative")
    data = task.get("solution_data", {})

    if narrative == "find_past_price":
        return _build_find_past_price(data)

    if narrative == "find_discounted_price":
        return _build_find_discounted_price(data)

    if narrative == "conditional_discount":
        return _build_conditional_discount(data)

    if narrative == "discount_and_setup":
        return _build_discount_and_setup(data)

    raise ValueError(f"Неизвестный narrative Q4: {narrative}")


# ---------------------------------------------------------
# 1️⃣ find_past_price
# ---------------------------------------------------------

def _build_find_past_price(data: Dict[str, Any]) -> str:

    stove = data["stove_no"]

    d1 = data["discount_stove_1"]
    d2 = data["discount_stove_2"]
    d3 = data["discount_stove_3"]

    return (
        "До начала сезонной распродажи цены на банные печи были выше. "
        f"В рамках акции стоимость модели №1 снизили на {d1}%, "
        f"модели №2 — на {d2}%, "
        f"а модели №3 — на {d3}%. "
        f"Вычисли, по какой цене (в рублях) продавалась печь №{stove} "
        "до объявления этих скидок?"
    )


# ---------------------------------------------------------
# 2️⃣ find_discounted_price
# ---------------------------------------------------------

def _build_find_discounted_price(data: Dict[str, Any]) -> str:

    stove = data["stove_no"]
    discount = data["discount_percent"]

    return (
        f"Магазин предоставляет покупателям специальную скидку {discount}% "
        f"на печь №{stove}. "
        "Определи итоговую стоимость этой печи (в рублях) "
        "с учётом заявленной скидки."
    )


# ---------------------------------------------------------
# 3️⃣ conditional_discount
# ---------------------------------------------------------

def _build_conditional_discount(data: Dict[str, Any]) -> str:

    stove = data["stove_no"]

    delivery_cost = data["delivery_cost"]
    threshold = data["threshold"]

    stove_discount = data["stove_discount_percent"]
    delivery_discount = data["delivery_discount_percent"]

    return (
        f"Услуга по доставке приобретённой печи до дачи обходится "
        f"в {delivery_cost} рублей. "
        "Однако магазин проводит акцию: "
        f"если стоимость выбранной печи превышает {threshold} рублей, "
        f"покупатель получает скидку {stove_discount}% на саму печь, "
        f"а цена доставки снижается на {delivery_discount}%. "
        f"Рассчитай общую сумму (в рублях), которую придётся заплатить "
        f"за приобретение печи №{stove} вместе с её доставкой "
        "на этих условиях."
    )

# ---------------------------------------------------------
# 4️⃣ discount_and_setup
# ---------------------------------------------------------

def _build_discount_and_setup(data: Dict[str, Any]) -> str:

    stove = data["stove_no"]
    delivery_cost = data["delivery_cost"]
    discount = data["discount_percent"]

    return (
        f"На покупку электрической печи действует разовая скидка "
        f"в размере {discount}%. "
        "Рассчитай, в какую общую сумму (в рублях) обойдётся "
        "приобретение этой печи вместе с её транспортировкой "
        "и полным монтажом (включая покупку специального кабеля), "
        f"если за доставку до участка транспортная компания "
        f"просит {delivery_cost} рублей."
    )
