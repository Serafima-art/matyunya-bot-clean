"""
Скрипт для заполнения таблицы tasks данными из файлов questions.json
Сканирует папку data/ и загружает все найденные задачи в базу данных
"""
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импортируем наши модули
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from matunya_bot_final.utils.db_manager import setup_database, register_task, add_skill_type
from matunya_bot_final.utils.models import Task, SkillType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def scan_questions_files(data_dir: str = "data") -> List[Tuple[str, Dict]]:
    """
    Рекурсивно сканирует папку data/ и находит все файлы questions.json
    
    Args:
        data_dir: Путь к папке с данными
        
    Returns:
        list: Список кортежей (путь_к_файлу, содержимое_json)
    """
    questions_files = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        logger.error(f"Папка {data_dir} не найдена!")
        return questions_files
    
    logger.info(f"Сканирую папку {data_dir} на наличие файлов questions.json...")
    
    # Рекурсивно ищем все файлы questions.json
    for questions_file in data_path.rglob("questions.json"):
        try:
            logger.info(f"Найден файл: {questions_file}")
            
            with open(questions_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                questions_files.append((str(questions_file), content))
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка чтения JSON в файле {questions_file}: {e}")
        except Exception as e:
            logger.error(f"Ошибка при обработке файла {questions_file}: {e}")
    
    logger.info(f"Найдено {len(questions_files)} файлов questions.json")
    return questions_files


def extract_questions_from_content(file_path: str, content: Dict) -> List[Dict]:
    """
    Извлекает вопросы из содержимого JSON файла.
    ИСПРАВЛЕНО: Теперь умеет обрабатывать структуру {"q1": [...], "q2": [...]}.
    """
    questions = []
    
    try:
        if isinstance(content, list):
            # Старая логика: если корневой элемент - массив
            questions = content
        elif isinstance(content, dict):
            # --- НОВАЯ УМНАЯ ЛОГИКА ---
            # Проверяем, похож ли файл на нашу структуру {"q1": [...], "q2": [...]}
            is_q_structure = all(key.startswith('q') and isinstance(value, list) for key, value in content.items())
            
            if is_q_structure:
                # Если да, "сливаем" все списки в один большой
                for q_list in content.values():
                    questions.extend(q_list)
            # --- КОНЕЦ НОВОЙ ЛОГИКИ ---
            
            # Старая логика для других форматов (оставляем для гибкости)
            elif "questions" in content:
                questions = content["questions"]
            elif "items" in content:
                questions = content["items"]
            elif "data" in content:
                questions = content["data"]
            else:
                # Если ничего не подошло, считаем, что весь объект - это одна задача
                questions = [content]
        
        logger.info(f"Из файла {file_path} извлечено {len(questions)} вопросов")
        return questions
        
    except Exception as e:
        logger.error(f"Ошибка при извлечении вопросов из {file_path}: {e}")
        return []
        
    except Exception as e:
        logger.error(f"Ошибка при извлечении вопросов из {file_path}: {e}")
        return []


async def check_task_exists(session: AsyncSession, skill_source_id: str) -> bool:
    """
    Проверяет, существует ли задача с данным skill_source_id.
    ФИНАЛЬНАЯ ВЕРСИЯ: Использует JOIN со SkillType.
    """
    try:
        # Теперь, когда в Task есть skill_type_id, этот join будет работать.
        result = await session.execute(
            select(Task.id)
            .join(SkillType, Task.skill_type_id == SkillType.id)
            .where(SkillType.source_id == skill_source_id)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
        
    except Exception as e:
        logger.error(f"Ошибка при проверке существования задачи {skill_source_id}: {e}")
        return True

def extract_task_data(question: Dict, file_path: str) -> Dict[str, str]:
    """
    Извлекает данные задачи из объекта вопроса.
    ИСПРАВЛЕНО: Поле 'answer' теперь необязательное.
    """
    # --- НАШ ШПИОН ---
    print(f"DEBUG: Пытаюсь разобрать вопрос: {question}")
    # --------------------

    try:
        skill_source_id = question.get("id") or question.get("skill_source_id")
        text = question.get("text") or question.get("question")
        # Ответ теперь НЕОБЯЗАТЕЛЬНЫЙ. Если его нет, ставим заглушку.
        answer = question.get("answer", "dynamic") # "dynamic" означает "вычисляется на лету"
        theme = question.get("theme") or question.get("category")
        
        # Проверяем ТОЛЬКО обязательные поля
        if not skill_source_id or not text:
            logger.warning(f"Пропущен вопрос из {file_path}: отсутствуют id или text.")
            logger.debug(f"Доступные ключи: {list(question.keys())}")
            return None
        
        return {
            "skill_source_id": str(skill_source_id),
            "text": str(text),
            "answer": str(answer),
            "theme": str(theme) if theme else None
        }
        
    except Exception as e:
        logger.error(f"Ошибка при извлечении данных из вопроса в {file_path}: {e}")
        return None

async def populate_tasks(data_dir: str = "data") -> Tuple[int, int]:
    """
    Основная функция заполнения базы данных задачами
    
    Args:
        data_dir: Путь к папке с данными
        
    Returns:
        tuple: (общее_количество_найденных_задач, количество_добавленных_задач)
    """
    # Настройка базы данных
    engine, session_maker = setup_database()
    
    try:
        # Сканируем файлы
        questions_files = await scan_questions_files(data_dir)
        
        if not questions_files:
            logger.info("Файлы questions.json не найдены")
            return 0, 0
        
        total_found = 0
        total_added = 0
        
        async with session_maker() as session:
            for file_path, content in questions_files:
                logger.info(f"Обрабатываю файл: {file_path}")
                
                # Извлекаем вопросы из файла
                questions = extract_questions_from_content(file_path, content)

                # --- НАША НОВАЯ ОТЛАДКА ---
                print(f"DEBUG: Найдено вопросов в файле: {len(questions)}")
                # ---------------------------
                
                for question in questions:
                    total_found += 1
                    
                    # Извлекаем данные задачи
                    task_data = extract_task_data(question, file_path)
                    if not task_data:
                        continue
                    
                    skill_source_id = task_data["skill_source_id"]
                    
                    # Проверяем, существует ли задача
                    if await check_task_exists(session, skill_source_id=skill_source_id):
                        logger.debug(f"Задача {skill_source_id} уже существует, пропускаем")
                        continue
                    
                    # Сначала убеждаемся, что skill_type существует
                    skill_type = await add_skill_type(
                        session=session,
                        source_id=skill_source_id,
                        name=f"Навык {skill_source_id}",
                        description=f"Автоматически созданный навык для {skill_source_id}"
                    )
                    
                    if not skill_type:
                        logger.error(f"Не удалось создать skill_type для {skill_source_id}")
                        continue
                    
                    # Создаем задачу
                    task_id = await register_task(
                        session=session,
                        skill_source_id=skill_source_id,
                        text=task_data["text"],
                        answer=task_data["answer"]
                    )
                    
                    if task_id:
                        total_added += 1
                        logger.info(f"Добавлена задача {skill_source_id} (ID: {task_id})")
                        
                        # Если есть тема, обновляем её
                        if task_data["theme"]:
                            from matunya_bot_final.utils.db_manager import update_task_theme
                            await update_task_theme(session, task_id, task_data["theme"])
                    else:
                        logger.error(f"Не удалось добавить задачу {skill_source_id}")
        
        return total_found, total_added
        
    except Exception as e:
        logger.error(f"Критическая ошибка при заполнении базы: {e}")
        return 0, 0
        
    finally:
        await engine.dispose()


async def main():
    """Точка входа в скрипт"""
    logger.info("Начинаю заполнение базы данных задачами...")
    
    try:
        total_found, total_added = await populate_tasks()
        
        print("\n" + "="*50)
        print("ОТЧЕТ О ЗАПОЛНЕНИИ БАЗЫ ДАННЫХ")
        print("="*50)
        print(f"Найдено задач: {total_found}")
        print(f"Добавлено новых: {total_added}")
        print(f"Пропущено (уже существуют): {total_found - total_added}")
        print("="*50)
        
        if total_added > 0:
            logger.info("База данных успешно заполнена!")
        else:
            logger.info("Новые задачи не найдены или не добавлены")
            
    except Exception as e:
        logger.error(f"Ошибка выполнения скрипта: {e}")
        print(f"\nОШИБКА: {e}")


if __name__ == "__main__":
    asyncio.run(main())