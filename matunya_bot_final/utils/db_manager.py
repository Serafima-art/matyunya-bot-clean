"""
Database Manager для проекта "Матюня"
Профессиональная асинхронная архитектура на SQLAlchemy
CRUD операции и базовое логирование данных
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import IntegrityError

from .models import (
    Base, User, SkillType, Task, AnswerLog, 
    ActivityLog, SessionLog, AIInteractionLog
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Конфигурация базы данных
DATABASE_URL = "sqlite+aiosqlite:///matunya.db"

# Глобальные переменные для движка и фабрики сессий
engine: Optional[AsyncEngine] = None
session_maker: Optional[async_sessionmaker[AsyncSession]] = None


# ====================================================================
# ИНИЦИАЛИЗАЦИЯ И НАСТРОЙКА БД
# ====================================================================

def setup_database() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """
    Настраивает компоненты базы данных.
    
    Returns:
        tuple: (engine, session_maker)
    """
    global engine, session_maker
    
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Установите True для отладки SQL-запросов
        future=True,
        pool_pre_ping=True  # Проверка соединения перед использованием
    )
    
    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logger.info("Компоненты базы данных настроены")
    return engine, session_maker


async def init_db(engine: AsyncEngine) -> None:
    """
    Инициализация базы данных.
    Создает все таблицы на основе моделей SQLAlchemy.
    
    Args:
        engine: Асинхронный движок SQLAlchemy
    """
    try:
        logger.info("Начинаем инициализацию базы данных...")
        
        async with engine.begin() as conn:
            # Создаем все таблицы, описанные в моделях
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Инициализация базы данных завершена успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise


async def close_database(engine: AsyncEngine) -> None:
    """
    Закрывает подключение к базе данных.
    
    Args:
        engine: Асинхронный движок SQLAlchemy
    """
    try:
        await engine.dispose()
        logger.info("Подключение к базе данных закрыто")
    except Exception as e:
        logger.error(f"Ошибка при закрытии базы данных: {e}")


# ====================================================================
# УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
# ====================================================================

async def add_or_update_user(
    session: AsyncSession, 
    telegram_id: int, 
    name: Optional[str] = None,
    gender: Optional[str] = None,
    parent_telegram_id: Optional[int] = None
) -> Optional[User]:
    """
    Находит пользователя по telegram_id или создает нового. 
    Обновляет переданные поля.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        telegram_id: Telegram ID пользователя
        name: Имя пользователя
        gender: Пол пользователя
        parent_telegram_id: Telegram ID родителя
        
    Returns:
        User: Объект пользователя (новый или обновленный)
        None: Если произошла ошибка
    """
    try:
        # Проверяем, существует ли пользователь
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Обновляем существующего пользователя
            updated = False
            if name is not None and user.name != name:
                user.name = name
                updated = True
            if gender is not None and user.gender != gender:
                user.gender = gender
                updated = True
            if parent_telegram_id is not None and user.parent_telegram_id != parent_telegram_id:
                user.parent_telegram_id = parent_telegram_id
                updated = True
                
            if updated:
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info(f"Обновлен пользователь: {user}")
            else:
                logger.debug(f"Пользователь не требует обновления: {user}")
        else:
            # Создаем нового пользователя
            user = User(
                telegram_id=telegram_id,
                name=name or "Чемпион",
                gender=gender,
                parent_telegram_id=parent_telegram_id
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"Создан новый пользователь: {user}")
        
        return user
        
    except IntegrityError as e:
        await session.rollback()
        logger.warning(f"Конфликт при создании пользователя telegram_id={telegram_id}: {e}")
        # Пытаемся найти существующего пользователя после ошибки
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при работе с пользователем telegram_id={telegram_id}: {e}")
        return None


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """
    Получает пользователя по его Telegram ID.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        telegram_id: Telegram ID пользователя
        
    Returns:
        User: Объект пользователя или None, если не найден
    """
    try:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            logger.debug(f"Найден пользователь: {user}")
        else:
            logger.debug(f"Пользователь с telegram_id={telegram_id} не найден")
            
        return user
        
    except Exception as e:
        logger.error(f"Ошибка при поиске пользователя telegram_id={telegram_id}: {e}")
        return None


async def get_user_id_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[int]:
    """
    Получает внутренний ID пользователя по Telegram ID.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        telegram_id: Telegram ID пользователя
        
    Returns:
        int: Внутренний ID пользователя или None, если не найден
    """
    try:
        result = await session.execute(
            select(User.id).where(User.telegram_id == telegram_id)
        )
        user_id = result.scalar_one_or_none()
        
        if user_id:
            logger.debug(f"Найден пользователь: telegram_id={telegram_id} -> user_id={user_id}")
        else:
            logger.warning(f"Пользователь с telegram_id={telegram_id} не найден")
            
        return user_id
        
    except Exception as e:
        logger.error(f"Ошибка при поиске пользователя telegram_id={telegram_id}: {e}")
        return None


# ====================================================================
# УПРАВЛЕНИЕ НАВЫКАМИ И ЗАДАЧАМИ
# ====================================================================

async def add_skill_type(
    session: AsyncSession, 
    source_id: str, 
    name: Optional[str] = None,
    task_number: Optional[str] = None, 
    description: Optional[str] = None
) -> Optional[SkillType]:
    """
    Добавляет новый тип навыка в справочник.
    Если тип навыка уже существует (по source_id), возвращает существующий.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        source_id: Уникальный идентификатор навыка
        name: Название навыка
        task_number: Номер задания ОГЭ
        description: Описание навыка
        
    Returns:
        SkillType: Объект типа навыка (новый или существующий)
        None: Если произошла ошибка
    """
    try:
        # Проверяем, существует ли уже такой skill_type
        result = await session.execute(
            select(SkillType).where(SkillType.source_id == source_id)
        )
        existing_skill = result.scalar_one_or_none()
        
        if existing_skill:
            logger.debug(f"Тип навыка с source_id={source_id} уже существует")
            return existing_skill
        
        # Создаем новый тип навыка
        new_skill = SkillType(
            source_id=source_id,
            name=name,
            task_number=task_number,
            description=description
        )
        
        session.add(new_skill)
        await session.commit()
        await session.refresh(new_skill)
        
        logger.info(f"Создан новый тип навыка: {new_skill}")
        return new_skill
        
    except IntegrityError as e:
        await session.rollback()
        logger.warning(f"Попытка создать дублирующий тип навыка source_id={source_id}: {e}")
        # Пытаемся найти существующий после ошибки
        result = await session.execute(
            select(SkillType).where(SkillType.source_id == source_id)
        )
        return result.scalar_one_or_none()
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при добавлении типа навыка source_id={source_id}: {e}")
        return None


async def register_task(
    session: AsyncSession, 
    skill_source_id: str, 
    text: str, 
    answer: str,
    theme: Optional[str] = None
) -> Optional[int]:
    """
    Регистрирует новую задачу в базе данных.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        skill_source_id: ID навыка из таблицы skill_types
        text: Текст задачи
        answer: Ответ на задачу
        theme: Тема задачи (Шины, Квартиры, Печи)
        
    Returns:
        Optional[int]: ID созданной задачи, если регистрация успешна; None, если навык не найден или произошла ошибка
    """
    try:
        # Ищем навык по source_id
        result = await session.execute(
            select(SkillType).where(SkillType.source_id == skill_source_id)
        )
        skill_type = result.scalar_one_or_none()
        
        if not skill_type:
            logger.warning(f"Навык с source_id={skill_source_id} не найден в базе")
            return None
        
        # Создаем новую задачу
        new_task = Task(
            skill_type_id=skill_type.id,
            text=text,
            answer=str(answer),
            theme=theme
        )
        
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        
        logger.info(f"Зарегистрирована новая задача: ID={new_task.id}, skill={skill_source_id}, theme={theme}")
        return new_task.id
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при регистрации задачи для skill_source_id={skill_source_id}: {e}")
        return None


async def get_task_by_id(session: AsyncSession, task_id: int) -> Optional[Task]:
    """
    Получает задачу по её ID.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        task_id: ID задачи
        
    Returns:
        Task: Объект задачи или None, если не найдена
    """
    try:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if task:
            logger.debug(f"Найдена задача: {task}")
        else:
            logger.warning(f"Задача с ID={task_id} не найдена")
            
        return task
        
    except Exception as e:
        logger.error(f"Ошибка при поиске задачи ID={task_id}: {e}")
        return None


async def update_task_theme(
    session: AsyncSession,
    task_id: int,
    theme: str
) -> bool:
    """
    Обновляет тему существующей задачи.
    Полезно для миграции данных.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        task_id: ID задачи
        theme: Новая тема задачи
        
    Returns:
        bool: True если обновление успешно
    """
    try:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            logger.warning(f"Задача с ID={task_id} не найдена")
            return False
        
        task.theme = theme
        session.add(task)
        await session.commit()
        
        logger.info(f"Обновлена тема задачи ID={task_id}: {theme}")
        return True
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при обновлении темы задачи ID={task_id}: {e}")
        return False


# ====================================================================
# ЛОГИРОВАНИЕ АКТИВНОСТИ
# ====================================================================

async def log_answer(
    session: AsyncSession, 
    user_id: int, 
    task_id: int, 
    is_correct: bool,
    user_answer: Optional[str] = None,
    time_spent: Optional[int] = None,
    help_used: bool = False,
    is_timed: bool = False,
    pack_session_id: Optional[str] = None,
    generated_task_details: Optional[str] = None
) -> Optional[AnswerLog]:
    """
    Записывает попытку ответа ученика в базу данных.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя из таблицы users
        task_id: ID задачи из таблицы tasks
        is_correct: Правильность ответа
        user_answer: Ответ пользователя
        time_spent: Время решения в секундах
        help_used: Использовал ли любую помощь
        is_timed: Режим "На время"
        pack_session_id: ID сессии пака для группировки
        generated_task_details: JSON с полными данными ошибочной задачи (только если is_correct=False)
        
    Returns:
        AnswerLog: Объект лога ответа
        None: Если произошла ошибка
    """
    try:
        new_log = AnswerLog(
            user_id=user_id,
            task_id=task_id,
            is_correct=is_correct,
            user_answer=user_answer,
            time_spent=time_spent,
            help_used=help_used,
            is_timed=is_timed,
            pack_session_id=pack_session_id,
            generated_task_details=generated_task_details
        )
        
        session.add(new_log)
        await session.commit()
        await session.refresh(new_log)
        
        # Логируем с указанием, сохранены ли детали задачи
        details_saved = " (с деталями задачи)" if generated_task_details else ""
        logger.info(f"Создан лог ответа: user_id={user_id}, task_id={task_id}, correct={is_correct}, timed={is_timed}{details_saved}")
        return new_log
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при создании лога ответа: user_id={user_id}, task_id={task_id}: {e}")
        return None


async def log_activity(
    session: AsyncSession,
    user_id: int,
    activity_type: str,
    task_id: Optional[int] = None,
    pack_type: Optional[str] = None,
    pack_theme: Optional[str] = None
) -> Optional[ActivityLog]:
    """
    Записывает активность пользователя в базу данных.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        activity_type: Тип активности ('help_general', 'help_ai_chat', 'theory', 'casual_chat', 
                      'timed_mode', 'theme_pack_start', 'exam_pack_start')
        task_id: ID задачи (опционально)
        pack_type: Тип пака ('theme' или 'exam')
        pack_theme: Тема пака для тематических паков
        
    Returns:
        ActivityLog: Объект лога активности
        None: Если произошла ошибка
    """
    try:
        new_activity = ActivityLog(
            user_id=user_id,
            task_id=task_id,
            activity_type=activity_type,
            pack_type=pack_type,
            pack_theme=pack_theme
        )
        
        session.add(new_activity)
        await session.commit()
        await session.refresh(new_activity)
        
        logger.info(f"Записана активность: user_id={user_id}, type={activity_type}, pack={pack_type}")
        return new_activity
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при записи активности: user_id={user_id}, type={activity_type}: {e}")
        return None


async def start_session(
    session: AsyncSession,
    user_id: int
) -> Optional[SessionLog]:
    """
    Начинает новую сессию пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        
    Returns:
        SessionLog: Объект сессии
        None: Если произошла ошибка
    """
    try:
        new_session = SessionLog(
            user_id=user_id,
            session_start=datetime.utcnow()
        )
        
        session.add(new_session)
        await session.commit()
        await session.refresh(new_session)
        
        logger.info(f"Начата новая сессия: user_id={user_id}, session_id={new_session.id}")
        return new_session
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при начале сессии: user_id={user_id}: {e}")
        return None


async def end_session(
    session: AsyncSession,
    session_id: int,
    tasks_attempted: int = 0,
    activities_count: int = 0,
    session_type: Optional[str] = None
) -> Optional[SessionLog]:
    """
    Завершает сессию пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        session_id: ID сессии для завершения
        tasks_attempted: Количество попыток решения задач
        activities_count: Общее количество действий
        session_type: Тип сессии ('study', 'casual', 'mixed')
        
    Returns:
        SessionLog: Обновленный объект сессии
        None: Если произошла ошибка
    """
    try:
        result = await session.execute(
            select(SessionLog).where(SessionLog.id == session_id)
        )
        session_log = result.scalar_one_or_none()
        
        if not session_log:
            logger.warning(f"Сессия с ID={session_id} не найдена")
            return None
        
        session_log.session_end = datetime.utcnow()
        session_log.tasks_attempted = tasks_attempted
        session_log.activities_count = activities_count
        session_log.session_type = session_type
        
        session.add(session_log)
        await session.commit()
        await session.refresh(session_log)
        
        logger.info(f"Завершена сессия: session_id={session_id}, type={session_type}, tasks={tasks_attempted}")
        return session_log
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при завершении сессии: session_id={session_id}: {e}")
        return None


async def get_session_by_user(
    session: AsyncSession,
    user_id: int,
    active_only: bool = True
) -> Optional[SessionLog]:
    """
    Получает активную (или последнюю) сессию пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        active_only: Искать только активные сессии (без session_end)
        
    Returns:
        SessionLog: Объект сессии или None
    """
    try:
        query = select(SessionLog).where(SessionLog.user_id == user_id)
        
        if active_only:
            query = query.where(SessionLog.session_end.is_(None))
        
        query = query.order_by(desc(SessionLog.session_start))
        
        result = await session.execute(query)
        session_log = result.first()
        
        return session_log[0] if session_log else None
        
    except Exception as e:
        logger.error(f"Ошибка при поиске сессии пользователя user_id={user_id}: {e}")
        return None


async def log_ai_interaction(
    session: AsyncSession,
    user_id: int,
    question_text: str,
    task_id: Optional[int] = None,
    question_category: Optional[str] = None,
    task_theme: Optional[str] = None,
    is_repeat_question: bool = False,
    follow_up_count: int = 0,
    used_theory_after: bool = False,
    solved_task_after: Optional[bool] = None,
    time_to_solution: Optional[int] = None,
    abandoned_task: bool = False
) -> Optional[AIInteractionLog]:
    """
    Записывает взаимодействие с ИИ для анализа качества помощи.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        question_text: Текст вопроса к ИИ
        task_id: ID задачи (если вопрос по конкретной задаче)
        question_category: Категория вопроса (автоматическая категоризация)
        task_theme: Тема задачи
        is_repeat_question: Повторный вопрос по той же задаче
        follow_up_count: Количество уточнений в диалоге
        used_theory_after: Обратился к теории после ИИ
        solved_task_after: Решил задачу в итоге
        time_to_solution: Время от вопроса до решения в секундах
        abandoned_task: Бросил задачу после ИИ
        
    Returns:
        AIInteractionLog: Объект лога взаимодействия с ИИ
        None: Если произошла ошибка
    """
    try:
        new_interaction = AIInteractionLog(
            user_id=user_id,
            task_id=task_id,
            question_text=question_text,
            question_category=question_category,
            task_theme=task_theme,
            is_repeat_question=is_repeat_question,
            follow_up_count=follow_up_count,
            used_theory_after=used_theory_after,
            solved_task_after=solved_task_after,
            time_to_solution=time_to_solution,
            abandoned_task=abandoned_task
        )
        
        session.add(new_interaction)
        await session.commit()
        await session.refresh(new_interaction)
        
        logger.info(f"Записано взаимодействие с ИИ: user_id={user_id}, task_id={task_id}, category={question_category}")
        return new_interaction
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при записи взаимодействия с ИИ: user_id={user_id}: {e}")
        return None