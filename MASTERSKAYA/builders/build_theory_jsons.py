#!/usr/bin/env python3
"""Builder script that converts theory cards from Google Sheets into JSON files."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import gspread
from gspread.exceptions import WorksheetNotFound
from dotenv import load_dotenv

# Автоматически подтягиваем переменные окружения из .env в корне проекта.
load_dotenv()

SERVICE_ACCOUNT_ENV = "GOOGLE_SERVICE_ACCOUNT"
WORKSHEET_NAME = "theory_all"
SCHEMA_NAME = "theory@v1"
REQUIRED_COLUMNS: Tuple[str, ...] = (
    "task_type",
    "subtype",
    "id",
    "style",
    "theory",
    "example",
    "mistakes",
)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )


def sanitize_text(value: Any) -> str:
    """Return a cleaned up text value suitable for JSON export."""
    if value is None:
        return ""
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    normalized = "\n".join(lines)
    while "\n\n\n" in normalized:
        normalized = normalized.replace("\n\n\n", "\n\n")
    return normalized.strip()


def load_client() -> gspread.Client:
    credentials_raw = os.getenv(SERVICE_ACCOUNT_ENV)
    if not credentials_raw:
        raise RuntimeError(
            "Переменная GOOGLE_SERVICE_ACCOUNT не найдена. "
            "Добавьте её в .env или задайте в окружении перед запуском."
        )
    try:
        credentials_dict = json.loads(credentials_raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Environment variable {SERVICE_ACCOUNT_ENV} does not contain valid JSON."
        ) from exc
    return gspread.service_account_from_dict(credentials_dict)


def fetch_records(client: gspread.Client, sheet_url: str) -> List[Dict[str, Any]]:
    logging.info("Открываю таблицу: %s", sheet_url)
    spreadsheet = client.open_by_url(sheet_url)
    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except WorksheetNotFound as exc:
        raise RuntimeError(
            f"Worksheet '{WORKSHEET_NAME}' was not found in the spreadsheet."
        ) from exc

    header = [cell.strip() for cell in worksheet.row_values(1)]
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing_columns:
        raise RuntimeError(
            "The worksheet is missing required columns: "
            + ", ".join(missing_columns)
        )

    records = worksheet.get_all_records(default_blank="")
    logging.info("Прочитано строк с данными: %d", len(records))
    return records


def validate_record(
    record: Dict[str, Any],
    row_number: int,
    seen_ids: Dict[str, int],
) -> Tuple[Dict[str, str], List[str]]:
    issues: List[str] = []
    sanitized: Dict[str, str] = {}

    for column in REQUIRED_COLUMNS:
        if column not in record:
            issues.append(f"нет колонки '{column}'")
            continue
        value = sanitize_text(record.get(column, ""))
        if not value:
            issues.append(f"пустое значение в колонке '{column}'")
        sanitized[column] = value

    card_id = sanitized.get("id", "")
    if card_id:
        if card_id in seen_ids:
            issues.append(f"дублирующий id '{card_id}' (строка {seen_ids[card_id]})")
    else:
        issues.append("не удалось определить id карточки")

    mistakes_text = sanitized.get("mistakes", "")
    if "<tg-spoiler" in mistakes_text.lower():
        issues.append("поле mistakes уже содержит тег <tg-spoiler>")

    if issues:
        return sanitized, issues

    if card_id:
        seen_ids[card_id] = row_number

    return sanitized, []


def wrap_cards(records: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    cards: List[Dict[str, str]] = []
    for record in records:
        payload = {
            "id": record["id"],
            "subtype": record["subtype"],
            "style": record["style"],
            "theory": record["theory"],
            "example": record["example"],
            "mistakes": f"<tg-spoiler>{record['mistakes']}</tg-spoiler>",
        }
        cards.append(payload)
    return cards


def save_json(
    repo_root: Path,
    task_type: str,
    cards: List[Dict[str, str]],
    sheet_url: str,
) -> Path:
    theory_root = repo_root / "matunya_bot_final" / "data" / "theory" / task_type
    theory_root.mkdir(parents=True, exist_ok=True)
    output_path = theory_root / f"theory_{task_type}.json"

    build_info = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": sheet_url,
        "worksheet": WORKSHEET_NAME,
        "card_count": len(cards),
    }

    payload = {
        "schema": SCHEMA_NAME,
        "task_type": task_type,
        "build": build_info,
        "cards": cards,
    }

    with output_path.open("w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, ensure_ascii=False, indent=2)

    return output_path


def process_records(
    records: List[Dict[str, Any]],
    sheet_url: str,
) -> None:
    seen_ids: Dict[str, int] = {}
    valid_records_by_task: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    invalid_entries: List[Tuple[int, str, List[str]]] = []

    for index, record in enumerate(records, start=2):
        sanitized, issues = validate_record(record, index, seen_ids)
        if issues:
            human_id = sanitized.get("id") or str(record.get("id") or "")
            identifier = human_id or f"строка {index}"
            invalid_entries.append((index, identifier, issues))
            continue

        task_type = sanitized["task_type"]
        valid_records_by_task[task_type].append(sanitized)

    total_valid = sum(len(items) for items in valid_records_by_task.values())
    logging.info("Создано валидных карточек: %d", total_valid)
    logging.info("Пропущено карточек из-за ошибок: %d", len(invalid_entries))

    if invalid_entries:
        logging.info("Список проблемных карточек:")
        for row_number, identifier, issues in invalid_entries:
            joined = "; ".join(issues)
            logging.info("  - строка %d (id=%s): %s", row_number, identifier, joined)

    if not valid_records_by_task:
        logging.error("Не найдено валидных карточек. Завершаю работу без генерации файлов.")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parents[2]
    for task_type, items in sorted(valid_records_by_task.items(), key=lambda pair: pair[0]):
        cards = wrap_cards(items)
        output_path = save_json(
            repo_root=repo_root,
            task_type=task_type,
            cards=cards,
            sheet_url=sheet_url,
        )
        logging.info(
            "Сохранен файл: %s (карточек: %d)",
            output_path,
            len(cards),
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Собрать теоретические карточки в JSON из Google Таблицы."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Полный URL Google Таблицы с листом theory_all.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()

    try:
        client = load_client()
    except Exception as exc:  # pragma: no cover
        logging.error("Не удалось инициализировать сервисный аккаунт: %s", exc)
        sys.exit(1)

    try:
        records = fetch_records(client, args.url)
    except Exception as exc:  # pragma: no cover
        logging.error("Не удалось прочитать таблицу: %s", exc)
        sys.exit(1)

    logging.info("Начинаю обработку...")
    process_records(records, args.url)
    logging.info("Готово.")


if __name__ == "__main__":
    main()
