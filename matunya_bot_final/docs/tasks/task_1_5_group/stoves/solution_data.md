Да, поняла: пишу идеальную структуру solution_data (facts-only) для всех 4 narrative Q3, чтобы:

валидатор = источник истины (считает всё)

solver ничего не вычисляет

humanizer берёт только из variables/solution_data

и потом не ловим KeyError’ы и расхождения

Ниже — канон полей. Названия фиксируем сейчас и дальше не меняем.

Q3.PATTERN: stoves_purchase_cost
1) find_price_difference

Смысл: насколько дешевле дровяная (подходящая по объёму) по сравнению с электрической (подходящей по объёму) с учётом установки.

{
  "selected": {
    "wood_stove_no": 2,
    "electric_stove_no": 1
  },
  "prices": {
    "wood_cost": 30500,
    "electric_cost": 16700,
    "electric_install_cost": 10200,
    "electric_total_cost": 26900
  },
  "difference_rub": 3600,
  "answer": 3600
}

Важно: electric_total_cost уже посчитан валидатором.

2) find_wood_stove_total_cost

Смысл: стоимость покупки дровяной (подходящей по объёму) с доставкой.

{
  "selected": {
    "wood_stove_no": 3
  },
  "prices": {
    "wood_cost": 34500,
    "delivery_cost": 2800,
    "wood_total_cost": 37300
  },
  "answer": 37300
}
3) find_electric_stove_total_cost

Смысл: стоимость покупки электрической (подходящей по объёму) с установкой и доставкой.

{
  "selected": {
    "electric_stove_no": 1
  },
  "prices": {
    "electric_cost": 16700,
    "electric_install_cost": 10200,
    "delivery_cost": 2800,
    "electric_total_cost": 39700
  },
  "answer": 39700
}
4) find_operating_cost_difference

Смысл: на сколько рублей эксплуатация дровяной подходящей дешевле электрической за год.

{
  "selected": {
    "wood_stove_no": 2,
    "electric_stove_no": 1
  },
  "operating": {
    "electric_kwh_per_year": 3100,
    "electric_price_per_kwh": 4,
    "electric_total": 12400,

    "wood_m3_per_year": 3,
    "wood_price_per_m3": 1500,
    "wood_total": 4500
  },
  "difference_rub": 7900,
  "answer": 7900
}
Общий контракт для Q3-вопроса в questions[]

У каждого вопроса Q3 (какой бы narrative ни был) в итоговом JSON задачи будет так:

{
  "q_number": 3,
  "pattern": "stoves_purchase_cost",
  "narrative": "find_price_difference",
  "question_text": "…",
  "input_data": { },
  "solution_data": { "...как выше..." },
  "answer": "3600",
  "skill_source_id": "stoves_q3"
}
