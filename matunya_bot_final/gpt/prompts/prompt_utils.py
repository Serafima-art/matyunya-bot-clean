from typing import Any, Dict, List, Sequence, Union

# =================================================================
# ЭТО НАША НОВАЯ, ЦЕНТРАЛЬНАЯ БИБЛИОТЕКА УТИЛИТ ДЛЯ ПРОМПТОВ
# =================================================================

def gender_words(gender: str) -> Dict[str, str]:
    """
    Подбирает формы слов с учётом пола ученика.
    """
    g = (gender or "").strip().lower()
    if g in {"f", "female", "жен", "ж", "girl", "woman", "девочка"}:
        return {"ready": "готова", "sure": "уверена", "dear": "дорогая"}
    # По умолчанию (male или None)
    return {"ready": "готов", "sure": "уверен", "dear": "дорогой"}

def format_history(dialog_history: Union[str, Sequence[Dict[str, Any]], None], limit: int = 16) -> str:
    """
    Сворачивает историю диалога в красивый, читаемый блок для GPT.
    """
    if not dialog_history:
        return "— (история пуста)"
    if isinstance(dialog_history, str):
        return dialog_history.strip() or "— (история пуста)"

    lines: List[str] = []
    for i, msg in enumerate(list(dialog_history)[-limit:], 1):
        role = str(msg.get("role", "")).strip().lower()
        content = str(msg.get("content", "")).strip()
        if not content:
            continue
        
        who = {"user": "Ученик", "assistant": "Матюня", "system": "System"}.get(role, role)
        lines.append(f"{i}. [{who}]: {content}")
        
    return "\n".join(lines) if lines else "— (история пуста)"

def safe_text(obj: Any) -> str:
    """
    Аккуратно превращает любой Python-объект (dict, list) в текстовый блок.
    Критически важен для режима "Помощь".
    """
    if obj is None: return "— (нет данных)"
    if isinstance(obj, (str, int, float)): return str(obj)
    try:
        import pprint
        return pprint.pformat(obj, width=88, compact=True)
    except Exception:
        return str(obj)