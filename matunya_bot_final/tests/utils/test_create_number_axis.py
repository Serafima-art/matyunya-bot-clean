from matunya_bot_final.utils.visuals.plot_generator import create_number_axis
import os

def test_create_number_axis_preview():
    axis_data = {
        "points": [
            {"value_num": -2.0, "value_text": "-2", "type": "solid"},
            {"value_num": 0.0, "value_text": "0", "type": "hollow"},
            {"value_num": 3.0, "value_text": "3", "type": "solid"},
        ],
        "intervals": [
            {"range": [-5, -2], "sign": "+"},
            {"range": [-2, 0], "sign": "-"},
            {"range": [0, 3], "sign": "+"},
            {"range": [3, 5], "sign": "-"},
        ],
        "shading_ranges": [
            [-5, -2],
            [0, 3]
        ]
    }

    output = "axis_test.png"  # имя, без полного пути
    result = create_number_axis(axis_data, output)

    assert os.path.exists(result)
    print(f"✅ Тестовая ось успешно создана: {result}")
