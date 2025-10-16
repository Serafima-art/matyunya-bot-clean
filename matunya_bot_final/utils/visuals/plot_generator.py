import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import FancyArrowPatch
import matplotlib.ticker as mticker
import matplotlib
matplotlib.use("Agg")  # ✅ чтобы не требовался Tcl/Tk, только рендер в PNG
from typing import Tuple
import os

def create_graph(
    func_data: dict,
    output_filename: str = "graph.png",
    x_lim: Tuple[float, float] = (-5, 5),
    y_lim: Tuple[float, float] = (-5, 5),
) -> str:
    """
    Генератор графиков для ОГЭ. Поддерживает разрывы (гиперболы, |x|).
    Вход:
        func_data = {"func": callable, "color": str, "label": str}
        x_lim, y_lim = кортежи (min, max)
    """

    # 1) Стили (без изменений)
    sns.set_style("whitegrid")
    plt.rcParams.update({
        'grid.linewidth': 0.8,
        'axes.linewidth': 1.5,
        'figure.dpi': 300
    })

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal', adjustable='box')

    # 2) Генерация точек с обработкой разрыва (как было)
    x_full = np.linspace(x_lim[0], x_lim[1], 2000)
    func = func_data.get("func")
    if func is None and "coeffs" in func_data:
        coeffs = func_data["coeffs"]
        a = coeffs.get("a", 0)
        b = coeffs.get("b", 0)
        c = coeffs.get("c", 0)
        func = lambda x, a=a, b=b, c=c: a * x**2 + b * x + c
    if func is None:
        raise ValueError("func_data должен содержать callable func или coeffs")

    try:
        rv = func(np.array([0.001]))
        right_val = rv[0] if isinstance(rv, np.ndarray) else rv
        lv = func(np.array([-0.001]))
        left_val = lv[0] if isinstance(lv, np.ndarray) else lv
        has_discontinuity = (right_val != left_val)
    except Exception:
        has_discontinuity = True  # безопасный дефолт

    x_parts = [x_full]
    if has_discontinuity and x_lim[0] < 0 < x_lim[1]:
        split_idx = np.argmax(x_full > 0)
        x_parts = [x_full[:split_idx], x_full[split_idx:]]

    # 3) Рисуем график (как было)
    for i, x_part in enumerate(x_parts):
        vectorized_func = np.vectorize(func, otypes=[float])
        y_part = vectorized_func(x_part)
        ax.plot(
            x_part, y_part,
            color=func_data.get("color", "orange"),
            linewidth=2.5,
            zorder=5,
            label=func_data.get("label", "") if i == 0 else ""
        )

    # 4) Оси и стрелки (обновлено)
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    ax.set_aspect('equal', adjustable='box')
    ax.set_box_aspect(1)
    print(f"[DBG] limits: x={ax.get_xlim()}  y={ax.get_ylim()}  label={func_data.get('label')}")

    # скрываем стандартные спайны, чтобы стрелки не перекрывались
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)

    # стрелка оси X (вправо)
    ax.add_patch(FancyArrowPatch(
        (x_lim[0], 0), (x_lim[1] * 1.05, 0),
        transform=ax.transData,
        arrowstyle='->',
        color='black',
        linewidth=2.2,
        mutation_scale=14,
        clip_on=False, zorder=6
    ))
    # стрелка оси Y (вверх)
    ax.add_patch(FancyArrowPatch(
        (0, y_lim[0]), (0, y_lim[1] * 1.05),
        transform=ax.transData,
        arrowstyle='->',
        color='black',
        linewidth=2.2,
        mutation_scale=14,
        clip_on=False, zorder=6
    ))

    # 5) Тикеты и подписи (обновлено: убираем ±1, двигаем x/y)
    def label_format(value, pos):
        # без нуля и без ±1; оставляем только целые >= 2 по модулю
        if value == 0:
            return ''
        return str(int(value)) if abs(value) > 1 else ''

    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(label_format))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(label_format))

    # подписи осей возле стрелок
    ax.text(x_lim[1] * 1.05, 0, 'x',
            fontsize=16, fontweight='bold',
            ha='left', va='center', clip_on=False)
    ax.text(0, y_lim[1] * 1.05, 'y',
            fontsize=16, fontweight='bold',
            ha='center', va='bottom', clip_on=False)

    # точка O в центре
    ax.text(0, 0, 'O',
            fontsize=14, fontweight='bold',
            ha='center', va='center', zorder=10)

    # 6) Финал (как было)
    sns.despine(left=True, bottom=True, right=True, top=True)
    ax.tick_params(axis='both', width=2.0, length=6, colors='black', labelcolor='black')

    fig.set_size_inches(6, 6, forward=True)           # квадратный холст
    fig.subplots_adjust(left=0.12, right=0.92,        # симметричные поля
                        bottom=0.12, top=0.92)

    plt.savefig(output_filename, dpi=300, transparent=False)
    plt.close()
    print(f"[✓] Феникс-рендер: {func_data.get('label', 'graph')} -> {output_filename}")
    return output_filename  # ✅ ВОЗВРАЩАЕМ путь к PNG

def create_number_axis(axis_data: dict, output_filename: str) -> str:
    """
    Рисует числовую ось для решения неравенств (задание 20).

    Вход:
        axis_data: {
            "points": [{"value_num": float, "value_text": str, "type": "solid|hollow"}],
            "intervals": [{"range": [float, float], "sign": "+"|"-"}],
            "shading_ranges": [[float, float], ...]
        }
        output_filename: путь для сохранения PNG
    """

    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Rectangle

    # --- 1. Настройка холста ---
    plt.rcParams.update({
        'axes.linewidth': 1.2,
        'figure.dpi': 300
    })
    fig, ax = plt.subplots(figsize=(7, 2))
    ax.set_ylim(-1.5, 1.5)
    ax.get_yaxis().set_visible(False)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)

    # --- 2. Определяем диапазон оси X ---
    all_values = [p["value_num"] for p in axis_data.get("points", []) if isinstance(p["value_num"], (int, float))]
    for r in axis_data.get("shading_ranges", []):
        all_values.extend([r[0], r[1]])
    if not all_values:
        all_values = [-5, 5]
    x_min, x_max = min(all_values) - 1, max(all_values) + 1
    ax.set_xlim(x_min, x_max)

    # --- 3. Ось X со стрелкой ---
    ax.axhline(y=0, color="black", linewidth=1.5)
    ax.add_patch(FancyArrowPatch(
        (x_max - 0.3, 0), (x_max + 0.2, 0),
        arrowstyle='->', mutation_scale=12,
        color='black', linewidth=1.5, zorder=5
    ))
    ax.text(x_max + 0.3, 0, 'x', fontsize=14, va='center', ha='left', fontweight='bold')

    # --- 4. Заштриховка решений ---
    for r in axis_data.get("shading_ranges", []):
        x0, x1 = r
        if x0 is None or x1 is None:
            continue
        rect = Rectangle(
            (x0, -0.12), x1 - x0, 0.24,
            color='gold', alpha=0.4, zorder=1
        )
        ax.add_patch(rect)

    # --- 5. Отрисовка точек ---
    for point in axis_data.get("points", []):
        x = point.get("value_num", 0)
        t = point.get("type", "solid")
        style = dict(facecolor="white", edgecolor="black", linewidth=1.5)
        if t == "solid":
            style["facecolor"] = "black"
        circle = plt.Circle((x, 0), 0.08, **style, zorder=3)
        ax.add_patch(circle)
        ax.text(x, -0.35, point.get("value_text", str(x)),
                fontsize=10, ha='center', va='top')

    # --- 6. Знаки на интервалах ---
    for interval in axis_data.get("intervals", []):
        x0, x1 = interval.get("range", [None, None])
        if x0 is None or x1 is None:
            continue
        x_mid = (x0 + x1) / 2
        sign = interval.get("sign", "")
        ax.text(x_mid, 0.25, sign,
                fontsize=12, ha='center', va='bottom', fontweight='bold', color='darkblue')

    # --- 7. Финал ---
    # создаём базовую папку temp/task_20
    base_dir = os.path.join("matunya_bot_final", "temp", "task_20")
    os.makedirs(base_dir, exist_ok=True)

    # сохраняем только имя файла (без поддиректорий)
    filename = os.path.basename(output_filename)
    final_path = os.path.join(base_dir, filename)

    plt.tight_layout()
    plt.savefig(final_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[✓] Числовая ось сохранена: {final_path}")
    return final_path
