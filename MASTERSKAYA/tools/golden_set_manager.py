# -*- coding: utf-8 -*-
"""Utility to manage Golden Set data in Google Sheets."""

from __future__ import annotations

import argparse
import json
import os
from typing import Iterable

import gspread
import gspread_dataframe as gd
import pandas as pd

from golden_sets_source import GOLDEN_SETS

SERVICE_ACCOUNT_ENV = "GOOGLE_SERVICE_ACCOUNT"
COLUMNS = ["task_type", "subtype", "style_phrase", "tags"]
SHEET_RANGE = "A:D"


def _get_client() -> gspread.Client:
    credentials_json = os.getenv(SERVICE_ACCOUNT_ENV)
    if not credentials_json:
        raise RuntimeError(
            f"Environment variable {SERVICE_ACCOUNT_ENV} is not set."
        )
    creds_info = json.loads(credentials_json)
    return gspread.service_account_from_dict(creds_info)


def _load_sheet(sheet_url: str):
    client = _get_client()
    spreadsheet = client.open_by_url(sheet_url)
    return spreadsheet.sheet1


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[COLUMNS]


def _read_existing(sheet) -> pd.DataFrame:
    values = sheet.get_all_records()
    if not values:
        return pd.DataFrame(columns=COLUMNS)
    existing = pd.DataFrame(values)
    return _ensure_columns(existing)


def _to_dataframe(data: Iterable[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(list(data))
    return _ensure_columns(frame)


def replace_data(sheet, df: pd.DataFrame) -> None:
    sheet.clear()
    gd.set_with_dataframe(sheet, df[COLUMNS], include_index=False, include_column_header=True)


def append_data(sheet, df: pd.DataFrame) -> None:
    existing = _read_existing(sheet)
    if existing.empty:
        replace_data(sheet, df)
        return
    merged = pd.concat([existing, df], ignore_index=True)
    merged = merged.drop_duplicates(subset=COLUMNS, keep="first")
    sheet.clear()
    gd.set_with_dataframe(sheet, merged[COLUMNS], include_index=False, include_column_header=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Golden Set manager for Google Sheets")
    parser.add_argument("--sheet-url", required=True, help="URL of the Google Sheet")
    parser.add_argument(
        "--mode",
        choices=("replace", "append"),
        default="replace",
        help="replace: overwrite sheet; append: merge new entries",
    )
    args = parser.parse_args()

    df = _to_dataframe(GOLDEN_SETS)
    sheet = _load_sheet(args.sheet_url)

    if args.mode == "replace":
        replace_data(sheet, df)
    else:
        append_data(sheet, df)


if __name__ == "__main__":
    main()
