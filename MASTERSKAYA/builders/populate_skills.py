# -*- coding: utf-8 -*-
"""
ОДНОРАЗОВЫЙ СКРИПТ-НАПОЛНИТЕЛЬ ("СИДЕР")
=========================================

НАЗНАЧЕНИЕ:
Этот скрипт предназначен для первоначального наполнения таблицы 'skill_types'
в основной базе данных (`matunya.db`).

ПРОБЛЕМА, КОТОРУЮ ОН РЕШАЕТ:
Система регистрации задач (`register_task`) требует, чтобы в таблице 'skill_types'
уже существовала запись о "навыке" (например, 'tires_q1_01'), прежде чем
регистрировать конкретный экземпляр этой задачи. Если таблица пуста,
регистрация невозможна.

КАК ОН РАБОТАЕТ:
1. Подключается к основной базе данных.
2. Проверяет, какие 'source_id' уже существуют в таблице 'skill_types'.
3. Добавляет только те 'source_id' из списка TIRES_SKILLS, которых еще нет в базе.

КОГДА ЕГО ЗАПУСКАТЬ:
- Один раз при первоначальной настройке базы данных.
- Каждый раз, когда в проект добавляются НОВЫЕ подтипы задач (например,
  когда мы добавим "Печи", нам нужно будет добавить их 'source_id' сюда и
  запустить скрипт снова).

КАК ЗАПУСКАТЬ (из корневой папки 'matunya' с активным .venv):
python -m MASTERSKAYA.builders.populate_skills
"""

import asyncio
from sqlalchemy.future import select

# --- ВАЖНО: Правильные абсолютные импорты ---
import matunya_bot_final.utils.db_manager as db_manager
from matunya_bot_final.utils.models import SkillType

# --- СПИСОК ВСЕХ НАВЫКОВ ДЛЯ "ШИН" ---
# (Сгенерирован на основе анализа questions.json)
TIRES_SKILLS = [
    # Q1
    "tires_q1_01", "tires_q1_02", "tires_q1_03", "tires_q1_04", "tires_q1_05",
    # Q2
    "tires_q2_01", "tires_q2_02", "tires_q2_03", "tires_q2_04", "tires_q2_05",
    # Q3
    "tires_q3_01", "tires_q3_02", "tires_q3_03", "tires_q3_04", "tires_q3_05",
    # Q4
    "tires_q4_01", "tires_q4_02", "tires_q4_03", "tires_q4_04",
    # Q5
    "tires_q5_01", "tires_q5_02", "tires_q5_03", "tires_q5_04",
    # Q6
    "tires_q6_01", "tires_q6_02", "tires_q6_03", "tires_q6_04", "tires_q6_05",
]

PAPER_SKILLS = [
    "paper_q1",
    "paper_q2",
    "paper_q3",
    "paper_q4",
    "paper_q5",
]

STOVES_SKILLS = [
    "stoves_q1",
    "stoves_q2",
    "stoves_q3",
    "stoves_q4",
    "stoves_q5",
]

async def main():
    print("🚀 Запуск наполнения таблицы 'skill_types'...")

    # --- ШАГ 1: Настраиваем БД ---
    # Эта функция создаст engine и session_maker
    await db_manager.setup_database()

    # Проверяем, что session_maker был создан
    if not db_manager.session_maker:
        print("❌ ОШИБКА: Не удалось создать фабрику сессий.")
        return

    # --- ШАГ 2: Работаем с сессией ---
    # Теперь мы можем создать сессию с помощью session_maker
    async with db_manager.session_maker() as session:
        # Получаем все уже существующие ID, чтобы не создавать дубликаты
        result = await session.execute(select(SkillType.source_id))
        existing_ids = {row[0] for row in result.all()}
        print(f"ℹ️  В базе уже существует {len(existing_ids)} навыков.")

        new_skills_added = 0
        ALL_SKILLS = TIRES_SKILLS + PAPER_SKILLS + STOVES_SKILLS

        for skill_id in ALL_SKILLS:

            if skill_id not in existing_ids:

                if skill_id.startswith("paper_"):
                    name_prefix = "Бумага"
                    description_prefix = "Навык для задания Бумага"
                elif skill_id.startswith("stoves_"):
                    name_prefix = "Печи"
                    description_prefix = "Навык для задания Печи"
                elif skill_id.startswith("tires_"):
                    name_prefix = "Шины"
                    description_prefix = "Навык для задания Шины"
                else:
                    name_prefix = "1-5"
                    description_prefix = "Навык для задания 1-5"

                new_skill = SkillType(
                    source_id=skill_id,
                    name=f"{name_prefix}: {skill_id}",
                    task_number="1-5",
                    description=f"{description_prefix}: {skill_id}"
                )

                session.add(new_skill)
                new_skills_added += 1
                print(f"  + Добавляем новый навык: {skill_id}")

        await session.commit()
        print(f"✅ Готово! Добавлено новых навыков: {new_skills_added}")


if __name__ == "__main__":
    asyncio.run(main())
