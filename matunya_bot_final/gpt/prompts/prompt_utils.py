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

def format_history(
    dialog_history: Union[str, Sequence[Dict[str, Any]], None],
    limit: int = 16,
) -> str:
    """
    Сворачивает историю диалога в читаемый и безопасный блок для GPT.

    Канон:
    • учитываются ТОЛЬКО роли user и assistant
    • system-сообщения полностью игнорируются
    • история ограничена по длине (limit)
    • формат пригоден для анализа модели (нумерация + роли)
    """

    if not dialog_history:
        return "— (история пуста)"

    # Если история уже пришла готовой строкой — используем её
    if isinstance(dialog_history, str):
        text = dialog_history.strip()
        return text if text else "— (история пуста)"

    lines: List[str] = []

    # Берём только последние limit сообщений
    recent_messages = list(dialog_history)[-limit:]

    for i, msg in enumerate(recent_messages, 1):
        role = str(msg.get("role", "")).strip().lower()
        content = str(msg.get("content", "")).strip()

        # ❌ system и пустые сообщения не допускаются
        if role not in {"user", "assistant"} or not content:
            continue

        who = "Ученик" if role == "user" else "Матюня"
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
