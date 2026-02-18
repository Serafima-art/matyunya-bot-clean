# matunya_bot_final/non_generators/task_1_5/paper/build.py
# -----------------------------------------------------------------------------
# Сборщик БД для практико-ориентированного блока "Форматы бумаги A0–A7" (задания 1–5)
#
# Источник истины: definitions/paper_sheets.txt (монолит с VARIANT START/END)
# Валидатор: PaperSheetsValidator (парсит текст, собирает контейнер variant->questions)
#
# Выход:
#   matunya_bot_final/data/tasks_1_5/paper/tasks_1_5_paper.json
#   (опционально) matunya_bot_final/data/tasks_1_5/paper/variants/<id>.json
# -----------------------------------------------------------------------------

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


# --- Пытаемся импортировать валидатор максимально "живуче" ---
def _import_validator():
    # 1) ожидаемый путь
    try:
        from matunya_bot_final.non_generators.task_1_5.paper.validators.paper_sheets_validator import (  # type: ignore
            PaperSheetsValidator,
        )
        return PaperSheetsValidator
    except Exception:
        pass

    # 2) если запускают как модуль из папки paper/
    try:
        from validators.paper_sheets_validator import PaperSheetsValidator  # type: ignore
        return PaperSheetsValidator
    except Exception as e:
        raise ImportError(
            "Не удалось импортировать PaperSheetsValidator. "
            "Проверь путь: non_generators/task_1_5/paper/validators/paper_sheets_validator.py"
        ) from e


PaperSheetsValidator = _import_validator()


# -----------------------------------------------------------------------------
# Парсер монолита definitions/paper_sheets.txt
# -----------------------------------------------------------------------------

VARIANT_START = "=== VARIANT START ==="
VARIANT_END = "=== VARIANT END ==="


@dataclass(frozen=True)
class RawVariant:
    question_text: str


def _split_variants(monolith_text: str) -> List[RawVariant]:
    """
    Режем файл на блоки между === VARIANT START === и === VARIANT END ===.
    Внутри блока валидатор сам распарсит VARIANT_CODE/IMAGE/TABLE_ORDER/Q1..Q5.
    """
    lines = monolith_text.splitlines()
    blocks: List[str] = []

    in_block = False
    buf: List[str] = []

    for line in lines:
        if line.strip() == VARIANT_START:
            in_block = True
            buf = []
            continue

        if line.strip() == VARIANT_END:
            if in_block:
                blocks.append("\n".join(buf).strip() + "\n")
            in_block = False
            buf = []
            continue

        if in_block:
            buf.append(line)

    return [RawVariant(question_text=b) for b in blocks if b.strip()]


# -----------------------------------------------------------------------------
# Нормализация / сохранение
# -----------------------------------------------------------------------------

def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _ensure_dir(path.parent)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_db(
    definitions_path: Path,
    out_dir: Path,
    write_variants: bool,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    validator = PaperSheetsValidator()

    monolith = definitions_path.read_text(encoding="utf-8")
    raw_variants = _split_variants(monolith)

    built: List[Dict[str, Any]] = []
    errors: List[str] = []

    for idx, rv in enumerate(raw_variants, start=1):
        ok, container, err_list = validator.validate({"question_text": rv.question_text})

        if not ok:
            vid = container.get("id") if isinstance(container, dict) else None
            tag = f"[#{idx}{' ' + vid if vid else ''}]"
            for e in err_list:
                errors.append(f"{tag} {e}")
            continue

        built.append(container)

        if write_variants:
            vid = container["id"]
            _write_json(out_dir / "variants" / f"{vid}.json", container)

    # один общий файл-база
    db_path = out_dir / "tasks_1_5_paper.json"
    _write_json(db_path, built)

    return built, errors


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Paper (formats A0–A7) DB for non_generators task_1_5."
    )

    default_defs = Path(__file__).resolve().parent / "definitions" / "paper_sheets.txt"
    default_out = Path(__file__).resolve().parents[3] / "data" / "tasks_1_5" / "paper"
    # ^ parents[3]:
    # build.py -> paper -> task_1_5 -> non_generators -> matunya_bot_final  (проверь структуру)

    parser.add_argument(
        "--definitions",
        type=str,
        default=str(default_defs),
        help="Path to definitions/paper_sheets.txt",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=str(default_out),
        help="Output directory (matunya_bot_final/data/tasks_1_5/paper)",
    )
    parser.add_argument(
        "--write-variants",
        action="store_true",
        help="Also write each variant into out_dir/variants/<id>.json",
    )

    args = parser.parse_args()

    defs_path = Path(args.definitions).resolve()
    out_dir = Path(args.out_dir).resolve()

    if not defs_path.exists():
        raise FileNotFoundError(f"Definitions not found: {defs_path}")

    built, errors = _build_db(
        definitions_path=defs_path,
        out_dir=out_dir,
        write_variants=bool(args.write_variants),
    )

    print("============================================================")
    print("🧱 BUILD PAPER DB (tasks 1-5)")
    print(f"📄 Definitions: {defs_path}")
    print(f"💾 Output dir : {out_dir}")
    print("------------------------------------------------------------")
    print(f"✅ Built variants : {len(built)}")
    print(f"❌ Errors        : {len(errors)}")

    if errors:
        print("------------------------------------------------------------")
        print("Ошибки:")
        for e in errors:
            print(" -", e)

    print("============================================================")
    print("Готово.")


if __name__ == "__main__":
    # Чтобы запуск работал и из Windows, и из Linux (VPS)
    os.environ.setdefault("PYTHONUTF8", "1")
    main()
