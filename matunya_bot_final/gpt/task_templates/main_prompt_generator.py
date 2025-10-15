# 🔧 Склейка блоков в единый MAIN_PROMPT для задания

from base_prompt_blocks import (
    ROLE_BLOCK,
    COPYRIGHT_BLOCK,
    FORMAT_STRUCTURE_BLOCK,
    FORMAT_RULES_BLOCK,
    FINAL_BLOCK
)

def generate_prompt(*blocks: str) -> str:
    """
    Склеивает переданные текстовые блоки в один промпт.
    Пример использования:
    MAIN_PROMPT = generate_prompt(ROLE_BLOCK, COPYRIGHT_BLOCK, TASK_7_BLOCK, FORMAT_STRUCTURE_BLOCK, FORMAT_RULES_BLOCK, FINAL_BLOCK)
    """
    return "".join(blocks)

# Пример заготовки — можно удалить или заменить
if __name__ == "__main__":
    example_prompt = generate_prompt(
        ROLE_BLOCK,
        COPYRIGHT_BLOCK,
        "\nТвоя задача — составить ОДНО задание №7 по следующим темам...\n",  # Здесь вставляется блок подтипов
        FORMAT_STRUCTURE_BLOCK,
        FORMAT_RULES_BLOCK,
        FINAL_BLOCK
    )
    print(example_prompt)
