# utils/svg_convert/rsvg_convert.py

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Union


def svg_to_png(
    svg_input: Union[str, Path],
    png_output: Union[str, Path],
    width: int,
    height: int,
    background: str = "#FFFFFF",
) -> None:
    """
    Конвертирует SVG → PNG утилитой `rsvg-convert` (librsvg).

    Args:
        svg_input: путь к SVG (str | Path)
        png_output: путь к PNG (str | Path)
        width: ширина результата в пикселях
        height: высота результата в пикселях
        background: цвет фона (например, "#FFFFFF")

    Raises:
        FileNotFoundError: если входного SVG нет
        RuntimeError: если rsvg-convert отсутствует или завершился с ошибкой
    """
    svg_path = Path(svg_input)
    png_path = Path(png_output)

    if not svg_path.exists():
        raise FileNotFoundError(f"SVG not found: {svg_path}")

    # Собираем команду rsvg-convert
    # В Windows рsvg-convert попадает в PATH после установки msys2/mingw.
    cmd = [
        "rsvg-convert",
        "--format", "png",
        "--width", str(int(width)),
        "--height", str(int(height)),
        "--background-color", str(background),
        "--output", str(png_path),
        str(svg_path),
    ]

    try:
        res = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as e:
        # rsvg-convert не найден в PATH
        raise RuntimeError(
            "Не найден `rsvg-convert`. "
            "Убедись, что установлен MSYS2 и пакет mingw-w64-x86_64-librsvg, "
            "а также что `C:\\msys64\\mingw64\\bin` добавлен в PATH."
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"rsvg-convert завершился с ошибкой ({e.returncode}).\n"
            f"STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        ) from e