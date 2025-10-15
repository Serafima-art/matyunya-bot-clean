"""
Analytics Core для проекта "Матюня"
Ядро аналитических расчетов - чистые функции для сбора и обработки данных
Возвращает только числа, факты и сырые данные без форматирования
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import select, func, and_, desc, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    User, SkillType, Task, AnswerLog, 
    ActivityLog, SessionLog, AIInteractionLog
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы для анализа
DEFAULT_ANALYSIS_DAYS = 7
MIN_ATTEMPTS_FOR_STATS = 3


# ====================================================================
# БАЗОВЫЕ ФУНКЦИИ СБОРА ДАННЫХ
# ====================================================================

async def get_user_performance_by_skills(
    session: AsyncSession,
    user_id: int,
    days_back: int = DEFAULT_ANALYSIS_DAYS
) -> Dict[str, Dict[str, Any]]:
    """
    Получает статистику по навыкам (номера заданий ОГЭ) для пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        days_back: Количество дней назад для анализа
        
    Returns:
        dict: {skill_name: {"correct": int, "total": int, "success_rate": float, "task_number": str}}
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        result = await session.execute(
            select(
                SkillType.name,
                SkillType.task_number,
                func.count(AnswerLog.id).label('total_attempts'),
                func.sum(func.cast(AnswerLog.is_correct, func.Integer)).label('correct_attempts')
            )
            .join(Task, AnswerLog.task_id == Task.id)
            .join(SkillType, Task.skill_type_id == SkillType.id)
            .where(and_(
                AnswerLog.user_id == user_id,
                AnswerLog.timestamp >= cutoff_date
            ))
            .group_by(SkillType.id, SkillType.name, SkillType.task_number)
        )
        
        performance = {}
        for row in result:
            skill_name = row.name or f"Задание {row.task_number}"
            total = row.total_attempts or 0
            correct = row.correct_attempts or 0
            success_rate = correct / total if total > 0 else 0
            
            performance[skill_name] = {
                "correct": correct,
                "total": total,
                "success_rate": round(success_rate, 3),
                "task_number": row.task_number
            }
        
        logger.debug(f"Получена статистика по навыкам для user_id={user_id}: {len(performance)} навыков")
        return performance
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики по навыкам user_id={user_id}: {e}")
        return {}


async def get_user_performance_by_themes(
    session: AsyncSession,
    user_id: int,
    days_back: int = DEFAULT_ANALYSIS_DAYS
) -> Dict[str, Dict[str, Any]]:
    """
    Получает статистику по темам (Шины, Квартиры и т.д.) для пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        days_back: Количество дней назад для анализа
        
    Returns:
        dict: {theme: {"correct": int, "total": int, "success_rate": float, "last_attempt": datetime}}
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        result = await session.execute(
            select(
                Task.theme,
                func.count(AnswerLog.id).label('total_attempts'),
                func.sum(func.cast(AnswerLog.is_correct, func.Integer)).label('correct_attempts'),
                func.max(AnswerLog.timestamp).label('last_attempt')
            )
            .join(Task, AnswerLog.task_id == Task.id)
            .where(and_(
                AnswerLog.user_id == user_id,
                AnswerLog.timestamp >= cutoff_date,
                Task.theme.isnot(None)
            ))
            .group_by(Task.theme)
        )
        
        performance = {}
        for row in result:
            if row.theme:
                total = row.total_attempts or 0
                correct = row.correct_attempts or 0
                success_rate = correct / total if total > 0 else 0
                
                performance[row.theme] = {
                    "correct": correct,
                    "total": total,
                    "success_rate": round(success_rate, 3),
                    "last_attempt": row.last_attempt
                }
        
        logger.debug(f"Получена статистика по темам для user_id={user_id}: {len(performance)} тем")
        return performance
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики по темам user_id={user_id}: {e}")
        return {}


async def get_weekly_activity_counts(
    session: AsyncSession,
    user_id: int,
    days_back: int = DEFAULT_ANALYSIS_DAYS
) -> Dict[str, int]:
    """
    Подсчитывает активность пользователя по типам за период.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        days_back: Количество дней назад для анализа
        
    Returns:
        dict: {activity_type: count}
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        result = await session.execute(
            select(
                ActivityLog.activity_type,
                func.count(ActivityLog.id).label('activity_count')
            )
            .where(and_(
                ActivityLog.user_id == user_id,
                ActivityLog.timestamp >= cutoff_date
            ))
            .group_by(ActivityLog.activity_type)
        )
        
        activity_counts = {}
        for row in result:
            activity_counts[row.activity_type] = row.activity_count or 0
        
        logger.debug(f"Получена активность для user_id={user_id}: {len(activity_counts)} типов")
        return activity_counts
        
    except Exception as e:
        logger.error(f"Ошибка при получении активности user_id={user_id}: {e}")
        return {}


async def get_session_patterns(
    session: AsyncSession,
    user_id: int,
    days_back: int = DEFAULT_ANALYSIS_DAYS
) -> Dict[str, Any]:
    """
    Анализирует паттерны сессий пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        days_back: Количество дней назад для анализа
        
    Returns:
        dict: Статистика сессий
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Получаем завершенные сессии
        result = await session.execute(
            select(
                func.count(SessionLog.id).label('total_sessions'),
                func.sum(SessionLog.tasks_attempted).label('total_tasks'),
                func.sum(SessionLog.activities_count).label('total_activities'),
                func.avg(
                    func.cast(
                        (func.julianday(SessionLog.session_end) - func.julianday(SessionLog.session_start)) * 24 * 60,
                        func.Float
                    )
                ).label('avg_session_minutes')
            )
            .where(and_(
                SessionLog.user_id == user_id,
                SessionLog.session_start >= cutoff_date,
                SessionLog.session_end.isnot(None)
            ))
        )
        
        row = result.first()
        
        patterns = {
            "total_sessions": row.total_sessions or 0,
            "total_tasks": row.total_tasks or 0,
            "total_activities": row.total_activities or 0,
            "avg_session_minutes": round(row.avg_session_minutes or 0, 1),
            "avg_tasks_per_session": 0,
            "sessions_per_day": 0
        }
        
        # Дополнительные расчеты
        if patterns["total_sessions"] > 0:
            patterns["avg_tasks_per_session"] = round(patterns["total_tasks"] / patterns["total_sessions"], 1)
            patterns["sessions_per_day"] = round(patterns["total_sessions"] / days_back, 1)
        
        logger.debug(f"Получены паттерны сессий для user_id={user_id}: {patterns['total_sessions']} сессий")
        return patterns
        
    except Exception as e:
        logger.error(f"Ошибка при анализе паттернов сессий user_id={user_id}: {e}")
        return {}


async def get_help_usage_stats(
    session: AsyncSession,
    user_id: int,
    days_back: int = DEFAULT_ANALYSIS_DAYS
) -> Dict[str, Any]:
    """
    Анализирует использование помощи пользователем.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        days_back: Количество дней назад для анализа
        
    Returns:
        dict: Статистика использования помощи
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Общая статистика по ответам
        answer_stats = await session.execute(
            select(
                func.count(AnswerLog.id).label('total_answers'),
                func.sum(func.cast(AnswerLog.help_used, func.Integer)).label('answers_with_help'),
                func.sum(func.cast(AnswerLog.is_timed, func.Integer)).label('timed_answers')
            )
            .where(and_(
                AnswerLog.user_id == user_id,
                AnswerLog.timestamp >= cutoff_date
            ))
        )
        
        answer_row = answer_stats.first()
        total_answers = answer_row.total_answers or 0
        answers_with_help = answer_row.answers_with_help or 0
        timed_answers = answer_row.timed_answers or 0
        
        # Статистика по типам помощи из активности
        activity_stats = await get_weekly_activity_counts(session, user_id, days_back)
        
        help_stats = {
            "total_answers": total_answers,
            "answers_with_help": answers_with_help,
            "help_usage_rate": round(answers_with_help / total_answers, 3) if total_answers > 0 else 0,
            "timed_answers": timed_answers,
            "timed_usage_rate": round(timed_answers / total_answers, 3) if total_answers > 0 else 0,
            "help_general_count": activity_stats.get("help_general", 0),
            "help_ai_chat_count": activity_stats.get("help_ai_chat", 0),
            "theory_usage_count": activity_stats.get("theory", 0)
        }
        
        logger.debug(f"Получена статистика помощи для user_id={user_id}: {help_stats['help_usage_rate']:.2%} использования")
        return help_stats
        
    except Exception as e:
        logger.error(f"Ошибка при анализе использования помощи user_id={user_id}: {e}")
        return {}


# ====================================================================
# АНАЛИЗ КАЧЕСТВА ИИ
# ====================================================================

async def get_ai_interaction_metrics(
    session: AsyncSession,
    days_back: int = DEFAULT_ANALYSIS_DAYS,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Анализирует метрики качества ИИ-взаимодействий.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        days_back: Количество дней назад для анализа
        user_id: ID конкретного пользователя (опционально)
        
    Returns:
        dict: Метрики качества ИИ
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Базовый фильтр
        base_filter = [AIInteractionLog.timestamp >= cutoff_date]
        if user_id:
            base_filter.append(AIInteractionLog.user_id == user_id)
        
        # Общие метрики
        overall_stats = await session.execute(
            select(
                func.count(AIInteractionLog.id).label('total_interactions'),
                func.avg(func.cast(AIInteractionLog.solved_task_after, func.Float)).label('success_rate'),
                func.avg(func.cast(AIInteractionLog.follow_up_count, func.Float)).label('avg_follow_ups'),
                func.sum(func.cast(AIInteractionLog.is_repeat_question, func.Integer)).label('repeat_questions'),
                func.sum(func.cast(AIInteractionLog.used_theory_after, func.Integer)).label('theory_fallbacks'),
                func.sum(func.cast(AIInteractionLog.abandoned_task, func.Integer)).label('task_abandonments')
            )
            .where(and_(*base_filter))
        )
        
        row = overall_stats.first()
        total_interactions = row.total_interactions or 0
        
        if total_interactions == 0:
            return {"total_interactions": 0, "message": "Недостаточно данных для анализа"}
        
        metrics = {
            "total_interactions": total_interactions,
            "success_rate": round(row.success_rate or 0, 3),
            "avg_follow_ups": round(row.avg_follow_ups or 0, 2),
            "repeat_question_rate": round((row.repeat_questions or 0) / total_interactions, 3),
            "theory_fallback_rate": round((row.theory_fallbacks or 0) / total_interactions, 3),
            "abandonment_rate": round((row.task_abandonments or 0) / total_interactions, 3)
        }
        
        logger.debug(f"Получены метрики ИИ: {total_interactions} взаимодействий, {metrics['success_rate']:.2%} успех")
        return metrics
        
    except Exception as e:
        logger.error(f"Ошибка при анализе метрик ИИ: {e}")
        return {}


async def get_ai_performance_by_themes(
    session: AsyncSession,
    days_back: int = DEFAULT_ANALYSIS_DAYS,
    min_interactions: int = MIN_ATTEMPTS_FOR_STATS
) -> Dict[str, Dict[str, Any]]:
    """
    Анализирует эффективность ИИ по темам задач.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        days_back: Количество дней назад для анализа
        min_interactions: Минимальное количество взаимодействий для включения в статистику
        
    Returns:
        dict: {theme: {"interactions": int, "success_rate": float, "avg_follow_ups": float}}
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        result = await session.execute(
            select(
                AIInteractionLog.task_theme,
                func.count(AIInteractionLog.id).label('interactions'),
                func.avg(func.cast(AIInteractionLog.solved_task_after, func.Float)).label('success_rate'),
                func.avg(func.cast(AIInteractionLog.follow_up_count, func.Float)).label('avg_follow_ups')
            )
            .where(and_(
                AIInteractionLog.timestamp >= cutoff_date,
                AIInteractionLog.task_theme.isnot(None)
            ))
            .group_by(AIInteractionLog.task_theme)
            .having(func.count(AIInteractionLog.id) >= min_interactions)
        )
        
        theme_performance = {}
        for row in result:
            theme_performance[row.task_theme] = {
                "interactions": row.interactions,
                "success_rate": round(row.success_rate or 0, 3),
                "avg_follow_ups": round(row.avg_follow_ups or 0, 2)
            }
        
        logger.debug(f"Получена производительность ИИ по темам: {len(theme_performance)} тем")
        return theme_performance
        
    except Exception as e:
        logger.error(f"Ошибка при анализе производительности ИИ по темам: {e}")
        return {}


# ====================================================================
# ФУНКЦИИ АНАЛИЗА И РЕКОМЕНДАЦИЙ
# ====================================================================

async def identify_weak_areas(
    session: AsyncSession,
    user_id: int,
    success_threshold: float = 0.7,
    min_attempts: int = MIN_ATTEMPTS_FOR_STATS,
    days_back: int = DEFAULT_ANALYSIS_DAYS
) -> Dict[str, List[str]]:
    """
    Определяет слабые области пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        success_threshold: Порог успешности (ниже = слабая область)
        min_attempts: Минимальное количество попыток для анализа
        days_back: Количество дней назад для анализа
        
    Returns:
        dict: {"weak_skills": [...], "weak_themes": [...], "neglected_themes": [...]}
    """
    try:
        # Анализируем навыки
        skills_performance = await get_user_performance_by_skills(session, user_id, days_back)
        weak_skills = [
            skill for skill, stats in skills_performance.items()
            if stats["total"] >= min_attempts and stats["success_rate"] < success_threshold
        ]
        
        # Анализируем темы
        themes_performance = await get_user_performance_by_themes(session, user_id, days_back)
        weak_themes = [
            theme for theme, stats in themes_performance.items()
            if stats["total"] >= min_attempts and stats["success_rate"] < success_threshold
        ]
        
        # Находим заброшенные темы (давно не решались)
        neglect_threshold = datetime.utcnow() - timedelta(days=3)
        neglected_themes = [
            theme for theme, stats in themes_performance.items()
            if stats["last_attempt"] and stats["last_attempt"] < neglect_threshold
        ]
        
        # Также находим темы, которые вообще не затрагивались за период
        all_themes_result = await session.execute(
            select(Task.theme)
            .where(Task.theme.isnot(None))
            .distinct()
        )
        all_themes = {row.theme for row in all_themes_result}
        attempted_themes = set(themes_performance.keys())
        never_attempted = list(all_themes - attempted_themes)
        
        analysis = {
            "weak_skills": weak_skills,
            "weak_themes": weak_themes,
            "neglected_themes": neglected_themes,
            "never_attempted_themes": never_attempted
        }
        
        logger.debug(f"Анализ слабых областей user_id={user_id}: {len(weak_skills)} навыков, {len(weak_themes)} тем")
        return analysis
        
    except Exception as e:
        logger.error(f"Ошибка при анализе слабых областей user_id={user_id}: {e}")
        return {"weak_skills": [], "weak_themes": [], "neglected_themes": [], "never_attempted_themes": []}


async def calculate_consistency_score(
    session: AsyncSession,
    user_id: int,
    days_back: int = DEFAULT_ANALYSIS_DAYS
) -> float:
    """
    Рассчитывает оценку постоянства занятий пользователя.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        days_back: Количество дней назад для анализа
        
    Returns:
        float: Оценка от 0.0 до 1.0 (1.0 = максимальная регулярность)
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Получаем дни с активностью
        result = await session.execute(
            select(
                func.date(AnswerLog.timestamp).label('activity_date'),
                func.count(AnswerLog.id).label('daily_attempts')
            )
            .where(and_(
                AnswerLog.user_id == user_id,
                AnswerLog.timestamp >= cutoff_date
            ))
            .group_by(func.date(AnswerLog.timestamp))
        )
        
        active_days = result.fetchall()
        days_with_activity = len(active_days)
        
        # Простая формула консистентности
        consistency = days_with_activity / days_back if days_back > 0 else 0
        
        # Бонус за равномерность (штраф за большие перерывы)
        if days_with_activity > 1:
            # Дополнительная логика для анализа равномерности может быть добавлена здесь
            pass
        
        consistency_score = round(min(consistency, 1.0), 3)
        
        logger.debug(f"Рассчитан показатель постоянства user_id={user_id}: {consistency_score}")
        return consistency_score
        
    except Exception as e:
        logger.error(f"Ошибка при расчете постоянства user_id={user_id}: {e}")
        return 0.0


async def get_pack_usage_stats(
    session: AsyncSession,
    user_id: int,
    days_back: int = DEFAULT_ANALYSIS_DAYS
) -> Dict[str, Any]:
    """
    Анализирует использование паков заданий пользователем.
    
    Args:
        session: Асинхронная сессия SQLAlчemy
        user_id: ID пользователя
        days_back: Количество дней назад для анализа
        
    Returns:
        dict: Статистика использования паков
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Статистика по пакам из активности
        pack_activity = await session.execute(
            select(
                ActivityLog.pack_type,
                ActivityLog.pack_theme,
                func.count(ActivityLog.id).label('pack_starts')
            )
            .where(and_(
                ActivityLog.user_id == user_id,
                ActivityLog.timestamp >= cutoff_date,
                ActivityLog.activity_type.in_(['theme_pack_start', 'exam_pack_start'])
            ))
            .group_by(ActivityLog.pack_type, ActivityLog.pack_theme)
        )
        
        pack_stats = {
            "theme_packs": {},
            "exam_pack_attempts": 0,
            "total_pack_sessions": 0
        }
        
        for row in pack_activity:
            pack_stats["total_pack_sessions"] += row.pack_starts
            
            if row.pack_type == "theme":
                theme = row.pack_theme or "Unknown"
                pack_stats["theme_packs"][theme] = row.pack_starts
            elif row.pack_type == "exam":
                pack_stats["exam_pack_attempts"] += row.pack_starts
        
        logger.debug(f"Получена статистика паков user_id={user_id}: {pack_stats['total_pack_sessions']} сессий")
        return pack_stats
        
    except Exception as e:
        logger.error(f"Ошибка при анализе использования паков user_id={user_id}: {e}")
        return {"theme_packs": {}, "exam_pack_attempts": 0, "total_pack_sessions": 0}