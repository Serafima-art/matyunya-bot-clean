# tests/test_task7_smoke.py
import asyncio
import json
from matunya_bot_final.gpt.task_templates.task_7.task_7_processor import process_generated_task

# 1) point_to_root — у точки A интервал [4;5), ровно один корень попадает в этот интервал: √17 ≈ 4.123...
gpt_point_to_root = {
    "text": "Одно из чисел √17, √23, √28, √32 отмечено на прямой точкой A. Какое это число?",
    "options": ["√17", "√23", "√28", "√32"],
    "correct_answer_index": 0,
    "correct_answer_value": "√17"
}

# 2) fraction_in_integer_interval — дробь 190/17 ≈ 11,176..., значит между 11 и 12
gpt_fraction_in_integer_interval = {
    "text": "Между какими целыми числами заключено число 190/17?",
    "options": ["10 и 11", "11 и 12", "12 и 13", "13 и 14"],
    "correct_answer_index": 1,
    "correct_answer_value": "11 и 12"
}

# 3) root_to_point — числа (-√11; √0,2; -√3; √5).
# Отсортируем их по значению: -√11 < -√3 < √0,2 < √5
# Пусть точки расположены слева направо A < B < C < D.
gpt_root_to_point = {
    "text": "На координатной прямой точки A, B, C и D соответствуют числам -√11; √0,2; -√3; √5.\nКакой точке соответствует число -√3?",
    "options": ["A", "B", "C", "D"],
    "correct_answer_index": 1,  # ожидаем B: порядок значений -> A:-√11, B:-√3, C:√0,2, D:√5
    "correct_answer_value": "B"
}

# 4) point_to_fraction — ровное совпадение pos = p/q (17/4 = 4.25), единственная точка B
gpt_point_to_fraction = {
    "text": "На координатной прямой отмечены точки A, B, C и D. Одна из них соответствует числу 17/4. Какая это точка?",
    "options": ["точка A", "точка B", "точка C", "точка D"],
    "correct_answer_index": 1,
    "correct_answer_value": "точка B",
    "image_params": {
        "min_val": 3,
        "max_val": 6,
        "points": [
            {"label": "A", "pos": 3.9},
            {"label": "B", "pos": 4.25},  # ровное совпадение с 17/4
            {"label": "C", "pos": 4.6},
            {"label": "D", "pos": 5.1}
        ]
    }
}

CASES = [
    ("point_to_root", gpt_point_to_root),
    ("fraction_in_integer_interval", gpt_fraction_in_integer_interval),
    ("root_to_point", gpt_root_to_point),
    ("point_to_fraction", gpt_point_to_fraction),
]

async def run_case(name, payload):
    print(f"\n▶️  Тест подтипа: {name}")
    res = await process_generated_task(payload, subtype=name)
    if not res:
        print("❌ FAIL: процессор вернул None")
        return False
    print(json.dumps(res, ensure_ascii=False, indent=2))
    # Простые проверки консистентности
    assert res["task_type"] == "7"
    assert res["subtype"] == name
    assert res["text"]
    assert res["options"] and len(res["options"]) == 4
    assert res["answer"]

    # Дополнительные точечные проверки
    if name == "point_to_root":
        assert res["answer"] == payload["correct_answer_value"]
        assert "image_params" in res and "points" in res["image_params"]

    if name == "fraction_in_integer_interval":
        assert res["answer"] in payload["options"]
        assert "image_params" not in res  # для этого подтипа рисунок не нужен

    if name == "root_to_point":
        assert res["answer"] in payload["options"]  # должна быть буква точки

    if name == "point_to_fraction":
        assert res["answer"] in payload["options"]
        pts = res.get("image_params", {}).get("points", [])
        # убедимся, что есть точка с pos ~= 4.25
        ok = any(abs(p["pos"] - 4.25) <= 1e-3 for p in pts)
        assert ok, "Нет точки с координатой 4.25 ± 0.001"

    print("✅ OK")
    return True

async def main():
    ok_all = True
    for name, payload in CASES:
        try:
            ok = await run_case(name, payload)
            ok_all = ok_all and ok
        except AssertionError as e:
            ok_all = False
            print(f"❌ FAIL: {e}")
        except Exception as e:
            ok_all = False
            print(f"❌ FAIL (exception): {e}")
    print("\n----------------------------------------")
    print("📊 ИТОГ:", "Все 4 теста пройдены ✅" if ok_all else "Есть ошибки ❌")

if __name__ == "__main__":
    asyncio.run(main())