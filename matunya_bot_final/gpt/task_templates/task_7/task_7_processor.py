import random
from typing import Dict, Any, Optional
from matunya_bot_final.gpt.task_templates.task_7.task_7_verifiers import REGISTRY

async def process_generated_task(
    gpt_response: Dict[str, Any],
    subtype: str
) -> Optional[Dict[str, Any]]:
    meta = REGISTRY.get(subtype)
    if not meta or "fn" not in meta:
        print(f"[DEBUG] Нет обработчика для подтипа: {subtype}")
        return None

    verify_fn = meta["fn"]
    needs_image = bool(meta.get("needs_image", True))

    has_text = bool(gpt_response.get("text"))
    has_options = bool(gpt_response.get("options"))
    img = gpt_response.get("image_params", {}) or {}
    points_len = len(img.get("points", []) or [])
    has_image_params = bool(img)

    try:
        verified_data = verify_fn(gpt_response)
    except Exception as e:
        print(f"[ERROR] Исключение в обработчике подтипа '{subtype}': {e}")
        verified_data = None

    if needs_image:
        vd_img = (verified_data or {}).get("image_params")
        if not vd_img:
            print("[DEBUG] Брак: needs_image=True, но верификатор не вернул image_params",
                  "subtype=", subtype)
            return None

    if not verified_data:
        print("[DEBUG] process_generated_task: верификация вернула None",
              "subtype=", subtype,
              "has_text=", has_text,
              "has_options=", has_options,
              "has_image_params=", has_image_params,
              "points_len=", points_len)
        return None

    final_task = {
        "id": f"gen_{random.randint(1000, 9999)}",
        "task_type": "7",
        "subtype": subtype,
        "text": gpt_response['text'],
        "options": gpt_response['options'],
        "answer": verified_data.get('answer'),
    }
    if "image_params" in verified_data:
        final_task["image_params"] = verified_data["image_params"]

    return final_task