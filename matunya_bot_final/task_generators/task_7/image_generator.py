from PIL import Image, ImageDraw, ImageFont
import io

def create_number_line_image(image_params: dict):
    """
    Создает изображение числовой прямой на основе словаря с параметрами.

    :param image_params: Словарь с параметрами, например:
        {
            "min_val": 0,
            "max_val": 5,
            "points": [
                {"label": "a", "pos": 3.3},
                {"label": "B", "pos": 4.1}
            ]
        }
    :return: Изображение в виде байтов для отправки в Telegram
    """
    # --- Извлекаем параметры ---
    min_val = image_params['min_val']
    max_val = image_params['max_val']
    points = image_params['points']

    # --- Настройки изображения ---
    width, height = 550, 100
    bg_color = "white"
    line_color = "black"
    point_color = "orange"
    font_color = "black"

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    try:
        font_size = 15
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font_size = 15 # Для стандартного шрифта размер может потребоваться другой
        font = ImageFont.load_default()

    # --- Рисуем числовую прямую ---
    y_line = height // 2
    padding = 50

    draw.line([(padding, y_line), (width - padding + 5, y_line)], fill=line_color, width=2)
    draw.line([(width - padding - 5, y_line - 5), (width - padding + 5, y_line)], fill=line_color, width=2)
    draw.line([(width - padding - 5, y_line + 5), (width - padding + 5, y_line)], fill=line_color, width=2)

    # --- Рисуем деления и подписи ---
    total_range = max_val - min_val
    # Предотвращаем деление на ноль, если диапазон некорректен
    if total_range == 0:
        total_range = 1
        
    px_per_unit = (width - 2 * padding) / total_range

    # Определяем, какие целые числа попадают в наш диапазон
    start_tick = int(min_val) if min_val % 1 == 0 else int(min_val) + 1
    end_tick = int(max_val) + 1

    for num in range(start_tick, end_tick):
        # Проверяем, видимо ли это деление на оси
        if min_val <= num <= max_val:
            x_pos = padding + (num - min_val) * px_per_unit
            draw.line([(x_pos, y_line - 5), (x_pos, y_line + 5)], fill=line_color, width=2)
            
            text = str(num)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            draw.text((x_pos - text_width / 2, y_line + 10), text, fill=font_color, font=font)

    # --- Рисуем все точки из списка ---
    for point in points:
        label = point['label']
        pos = point['pos']

        point_x = padding + (pos - min_val) * px_per_unit
        point_radius = 4

        draw.ellipse(
            [(point_x - point_radius, y_line - point_radius), (point_x + point_radius, y_line + point_radius)],
            fill=point_color, outline=point_color
        )
        
        # Рисуем метку, только если она не пустая
        if label:
            label_bbox = draw.textbbox((0, 0), label, font=font)
            label_width = label_bbox[2] - label_bbox[0]
            draw.text((point_x - label_width / 2, y_line - 30), label, fill=point_color, font=font)

    # --- Сохраняем картинку в память ---
    image_buffer = io.BytesIO()
    image.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    return image_buffer