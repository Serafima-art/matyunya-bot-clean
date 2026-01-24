from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import List, Optional

import gspread
from cachetools import TTLCache

logger = logging.getLogger(__name__)

_GOLDEN_SET_CACHE: TTLCache[str, List[str]] = TTLCache(maxsize=128, ttl=3600)

SERVICE_ACCOUNT_ENV = "GOOGLE_SERVICE_ACCOUNT"
SHEET_URL_ENV = "GOOGLE_SHEET_URL"


def _load_sheet() -> Optional[gspread.Worksheet]:
    credentials_json = os.getenv(SERVICE_ACCOUNT_ENV)
    if not credentials_json:
        logger.info(
            "[GoldenSet] GOOGLE_SERVICE_ACCOUNT не задан — golden set отключён"
        )
        return None

    sheet_url = os.getenv(SHEET_URL_ENV)
    if not sheet_url:
        logger.info(
            "[GoldenSet] GOOGLE_SHEET_URL не задан — golden set отключён"
        )
        return None

    try:
        creds_info = json.loads(credentials_json)
        client = gspread.service_account_from_dict(creds_info)
        spreadsheet = client.open_by_url(sheet_url)
        return spreadsheet.sheet1

    except Exception as e:
        logger.warning(
            f"[GoldenSet] Недоступен (работаем без него): {e.__class__.__name__}"
        )
        return None


def _fetch_golden_set_sync(subtype: str, task_type: Optional[int]) -> List[str]:
    worksheet = _load_sheet()
    if worksheet is None:
        return []

    records = worksheet.get_all_records()
    results: List[str] = []
    for row in records:
        row_subtype = str(row.get("subtype", "")).strip()
        row_task_type = row.get("task_type")

        if subtype and row_subtype != subtype:
            continue
        if task_type is not None and str(row_task_type).strip() != str(task_type):
            continue

        phrase = row.get("style_phrase")
        if phrase:
            results.append(str(phrase).strip())

    return results


def _cache_key(subtype: str, task_type: Optional[int]) -> str:
    return f"{task_type or 'any'}::{subtype or ''}"


async def get_golden_set(subtype: str, task_type: Optional[int] = None) -> List[str]:
    """Fetch golden set phrases for a given subtype (and optional task type)."""
    key = _cache_key(subtype, task_type)
    if key in _GOLDEN_SET_CACHE:
        return _GOLDEN_SET_CACHE[key]

    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, _fetch_golden_set_sync, subtype, task_type)
    except Exception as exc:  # pragma: no cover
        logger.exception("Golden set fetch failed", exc_info=exc)
        result = []

    _GOLDEN_SET_CACHE[key] = result
    return result
