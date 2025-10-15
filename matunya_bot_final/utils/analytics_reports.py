"""
Analytics Reports для проекта "Матюня"
Генерация отчетов и дайджестов на основе данных из analytics_core
Превращает числа в человеческий текст, соблюдая принципы "честного помощника"
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import User
from .analytics_core import (
    get_user_performance_by_skills,
    get_user_performance_by_themes,
    get_weekly_activity_counts,
    get_session_patterns,
    get_help_usage_stats,
    get_ai_interaction_metrics,
    get_ai_performance_by_themes,
    identify_weak_areas,
    calculate_consistency_score,
    get_pack_usage_stats
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы для отчетов
DEFAULT_ANALYSIS_DAYS = 7
SUCCESS_THRESHOLD = 0.7
MIN_ATTEMPTS_FOR_RECOMMENDATION = 3


# ====================================================================
# ОТЧЕТЫ ДЛЯ УЧЕНИКОВ (ЧЕСТНАЯ СТАТИСТИКА)
# ====================================================================

async def get_student_stats(session: AsyncSession, user_id: int) -> Dict[str, Any]:
    """
    Рассчитывает статистику для ученика (честные цифры).
    Анализирует данные за последнюю неделю.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        
    Returns:
        dict: Полная статистика ученика
    """
    try:
        logger.info(f"Начинаем расчет статистики для ученика user_id={user_id}")
        
        # Собираем все данные из analytics_core
        skill_performance = await get_user_performance_by_skills(session, user_id)
        theme_performance = await get_user_performance_by_themes(session, user_id)
        weekly_activity = await get_weekly_activity_counts(session, user_id)
        session_patterns = await get_session_patterns(session, user_id)
        help_usage = await get_help_usage_stats(session, user_id)
        weak_areas = await identify_weak_areas(session, user_id)
        consistency_score = await calculate_consistency_score(session, user_id)
        pack_stats = await get_pack_usage_stats(session, user_id)
        
        # Формируем структурированный отчет
        student_stats = {
            # Производительность по навыкам (задания ОГЭ)
            "skill_performance": skill_performance,
            
            # Производительность по темам (Шины, Квартиры и т.д.)
            "theme_performance": theme_performance,
            
            # Еженедельная активность
            "weekly_activity": {
                "total_answers": help_usage.get("total_answers", 0),
                "study_sessions": session_patterns.get("total_sessions", 0),
                "total_time_minutes": round(session_patterns.get("total_sessions", 0) * session_patterns.get("avg_session_minutes", 0), 1),
                "help_usage": {
                    "general_help": weekly_activity.get("help_general", 0),
                    "ai_chat": weekly_activity.get("help_ai_chat", 0),
                    "theory_usage": weekly_activity.get("theory", 0),
                    "casual_chat": weekly_activity.get("casual_chat", 0)
                },
                "pack_usage": {
                    "theme_packs": pack_stats.get("theme_packs", {}),
                    "exam_attempts": pack_stats.get("exam_pack_attempts", 0)
                }
            },
            
            # Паттерны поведения
            "behavior_patterns": {
                "avg_session_minutes": session_patterns.get("avg_session_minutes", 0),
                "avg_tasks_per_session": session_patterns.get("avg_tasks_per_session", 0),
                "sessions_per_day": session_patterns.get("sessions_per_day", 0),
                "consistency_score": consistency_score,
                "help_dependency": help_usage.get("help_usage_rate", 0),
                "timed_mode_usage": help_usage.get("timed_usage_rate", 0)
            },
            
            # Анализ и рекомендации
            "analysis": {
                "weak_skills": weak_areas.get("weak_skills", []),
                "weak_themes": weak_areas.get("weak_themes", []),
                "neglected_themes": weak_areas.get("neglected_themes", []),
                "never_attempted_themes": weak_areas.get("never_attempted_themes", []),
                "recommendations": await _generate_student_recommendations(
                    skill_performance, theme_performance, weekly_activity, 
                    session_patterns, help_usage, weak_areas, consistency_score
                )
            }
        }
        
        logger.info(f"Статистика для ученика user_id={user_id} успешно рассчитана")
        return student_stats
        
    except Exception as e:
        logger.error(f"Ошибка при расчете статистики ученика user_id={user_id}: {e}")
        return {}


async def _generate_student_recommendations(
    skill_performance: Dict,
    theme_performance: Dict,
    weekly_activity: Dict,
    session_patterns: Dict,
    help_usage: Dict,
    weak_areas: Dict,
    consistency_score: float
) -> List[str]:
    """
    Генерирует конкретные рекомендации для ученика на основе анализа данных.
    
    Returns:
        list: Список конкретных рекомендаций
    """
    recommendations = []
    
    # Рекомендации по слабым областям
    weak_skills = weak_areas.get("weak_skills", [])
    weak_themes = weak_areas.get("weak_themes", [])
    
    if weak_skills:
        recommendations.append(f"Стоит дополнительно проработать: {', '.join(weak_skills[:2])}")
    
    if weak_themes:
        recommendations.append(f"Нужно подтянуть темы: {', '.join(weak_themes[:2])}")
    
    # Рекомендации по заброшенным темам
    neglected = weak_areas.get("neglected_themes", [])
    never_attempted = weak_areas.get("never_attempted_themes", [])
    
    if neglected:
        recommendations.append(f"Давно не решал задачи по темам: {', '.join(neglected[:2])}")
    
    if never_attempted and len(never_attempted) <= 3:
        recommendations.append(f"Попробуй новые темы: {', '.join(never_attempted[:2])}")
    
    # Рекомендации по паттернам обучения
    if consistency_score < 0.4:
        recommendations.append("Попробуй заниматься более регулярно, даже по 10-15 минут в день")
    
    avg_session = session_patterns.get("avg_session_minutes", 0)
    if avg_session > 60:
        recommendations.append("Лучше заниматься короче, но чаще - это эффективнее")
    elif avg_session > 0 and avg_session < 10:
        recommendations.append("Можно увеличить время занятий до 15-20 минут")
    
    # Рекомендации по использованию помощи
    theory_usage = weekly_activity.get("theory", 0)
    total_answers = help_usage.get("total_answers", 0)
    
    if theory_usage < 3 and total_answers > 10:
        recommendations.append("Чаще обращайся к разделу 'Теория' - это поможет лучше понимать задачи")
    
    help_rate = help_usage.get("help_usage_rate", 0)
    if help_rate > 0.8:
        recommendations.append("Попробуй сначала решить задачу самостоятельно, а потом обращаться за помощью")
    elif help_rate < 0.2 and total_answers > 15:
        recommendations.append("Не стесняйся обращаться за помощью, когда что-то непонятно")
    
    # Рекомендации по режиму "На время"
    timed_rate = help_usage.get("timed_usage_rate", 0)
    if timed_rate < 0.1 and total_answers > 20:
        recommendations.append("Попробуй режим 'На время' - это поможет подготовиться к настоящему экзамену")
    
    return recommendations[:5]  # Максимум 5 рекомендаций


# ====================================================================
# ДАЙДЖЕСТЫ ДЛЯ РОДИТЕЛЕЙ (МЯГКАЯ ИНТЕРПРЕТАЦИЯ)
# ====================================================================

async def get_parent_digest(session: AsyncSession, user_id: int) -> str:
    """
    Генерирует дайджест для родителя (мягкая интерпретация).
    Превращает статистику в понятный человеческий текст.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        user_id: ID пользователя
        
    Returns:
        str: Текстовый дайджест для родителя
    """
    try:
        logger.info(f"Генерируем дайджест для родителя user_id={user_id}")
        
        # Получаем имя ученика
        user_result = await session.execute(
            select(User.name).where(User.id == user_id)
        )
        user_name = user_result.scalar_one_or_none() or "Ваш ребёнок"
        
        # Получаем данные из analytics_core
        skill_performance = await get_user_performance_by_skills(session, user_id)
        theme_performance = await get_user_performance_by_themes(session, user_id)
        session_patterns = await get_session_patterns(session, user_id)
        weekly_activity = await get_weekly_activity_counts(session, user_id)
        help_usage = await get_help_usage_stats(session, user_id)
        consistency_score = await calculate_consistency_score(session, user_id)
        weak_areas = await identify_weak_areas(session, user_id)
        
        # Формируем дайджест
        digest_parts = []
        
        # Заголовок
        digest_parts.append(f"📊 Еженедельный отчет: {user_name}")
        digest_parts.append("")
        
        # Общая активность
        sessions_count = session_patterns.get("total_sessions", 0)
        total_tasks = session_patterns.get("total_tasks", 0)
        avg_session = session_patterns.get("avg_session_minutes", 0)
        
        if sessions_count == 0:
            digest_parts.append("📅 На этой неделе занятий не было")
            digest_parts.append("")
            digest_parts.append("💡 Рекомендация: Попробуйте установить регулярное время для занятий")
            return "\n".join(digest_parts)
        
        # Активность
        digest_parts.extend([
            f"📅 Занимался {sessions_count} раз на этой неделе",
            f"📝 Решил {total_tasks} задач"
        ])
        
        if avg_session > 0:
            digest_parts.append(f"⏰ Средняя продолжительность занятий: {avg_session:.0f} минут")
        
        digest_parts.append("")
        
        # Оценка регулярности
        digest_parts.append(_format_consistency_message(consistency_score, sessions_count))
        digest_parts.append("")
        
        # Успехи и прогресс
        success_message = _format_achievements_message(skill_performance, theme_performance)
        if success_message:
            digest_parts.append(success_message)
            digest_parts.append("")
        
        # Области для внимания
        attention_message = _format_attention_areas(weak_areas, skill_performance, theme_performance)
        if attention_message:
            digest_parts.append(attention_message)
            digest_parts.append("")
        
        # Самостоятельность и использование помощи
        independence_message = _format_independence_message(help_usage, weekly_activity, total_tasks)
        if independence_message:
            digest_parts.append(independence_message)
            digest_parts.append("")
        
        # Рекомендации для родителей
        parent_recommendations = _generate_parent_recommendations(
            sessions_count, avg_session, consistency_score, 
            help_usage, weak_areas, weekly_activity
        )
        if parent_recommendations:
            digest_parts.append("💡 Рекомендации:")
            digest_parts.extend(parent_recommendations)
        
        result = "\n".join(digest_parts)
        logger.info(f"Дайджест для родителя user_id={user_id} успешно сгенерирован")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при генерации дайджеста для родителя user_id={user_id}: {e}")
        return "Произошла ошибка при формировании отчета."


def _format_consistency_message(consistency_score: float, sessions_count: int) -> str:
    """Форматирует сообщение о регулярности занятий."""
    if consistency_score >= 0.8:
        return "🎯 Отличная регулярность занятий!"
    elif consistency_score >= 0.6:
        return "📈 Хорошая регулярность занятий"
    elif consistency_score >= 0.3:
        return "📊 Занимается периодически"
    else:
        return "⏰ Занятия нерегулярные"


def _format_achievements_message(skill_performance: Dict, theme_performance: Dict) -> str:
    """Форматирует сообщение об успехах и достижениях."""
    achievements = []
    
    # Находим сильные навыки
    strong_skills = [
        name for name, stats in skill_performance.items()
        if stats["total"] >= MIN_ATTEMPTS_FOR_RECOMMENDATION and stats["success_rate"] >= 0.8
    ]
    
    # Находим сильные темы  
    strong_themes = [
        theme for theme, stats in theme_performance.items()
        if stats["total"] >= MIN_ATTEMPTS_FOR_RECOMMENDATION and stats["success_rate"] >= 0.8
    ]
    
    if strong_skills:
        achievements.append(f"✅ Отлично справляется: {', '.join(strong_skills[:2])}")
    
    if strong_themes:
        achievements.append(f"🏆 Сильные темы: {', '.join(strong_themes[:2])}")
    
    # Находим улучшающиеся области
    improving_skills = [
        name for name, stats in skill_performance.items()
        if stats["total"] >= MIN_ATTEMPTS_FOR_RECOMMENDATION and 0.5 <= stats["success_rate"] < 0.8
    ]
    
    if improving_skills:
        achievements.append(f"📈 Показывает прогресс: {', '.join(improving_skills[:2])}")
    
    return "\n".join(achievements) if achievements else ""


def _format_attention_areas(weak_areas: Dict, skill_performance: Dict, theme_performance: Dict) -> str:
    """Форматирует сообщение об областях, требующих внимания."""
    attention_parts = []
    
    weak_skills = weak_areas.get("weak_skills", [])
    weak_themes = weak_areas.get("weak_themes", [])
    neglected_themes = weak_areas.get("neglected_themes", [])
    
    if weak_skills or weak_themes:
        attention_parts.append("⚠️ Стоит обратить внимание:")
        
        if weak_themes:
            attention_parts.append(f"Темы для дополнительной проработки: {', '.join(weak_themes[:2])}")
        
        if weak_skills:
            attention_parts.append(f"Задания, требующие практики: {', '.join(weak_skills[:2])}")
    
    if neglected_themes:
        if not attention_parts:
            attention_parts.append("📅 Рекомендуется повторить:")
        attention_parts.append(f"Давно не решались темы: {', '.join(neglected_themes[:2])}")
    
    return "\n".join(attention_parts)


def _format_independence_message(help_usage: Dict, weekly_activity: Dict, total_tasks: int) -> str:
    """Форматирует сообщение о самостоятельности."""
    if total_tasks == 0:
        return ""
    
    help_rate = help_usage.get("help_usage_rate", 0)
    theory_usage = weekly_activity.get("theory", 0)
    ai_usage = weekly_activity.get("help_ai_chat", 0)
    
    independence_parts = ["🤝 Самостоятельность:"]
    
    if help_rate <= 0.3:
        independence_parts.append("Хорошо справляется самостоятельно")
    elif help_rate <= 0.6:
        independence_parts.append("Умеренно использует помощь - это нормально")
    else:
        independence_parts.append("Часто обращается за помощью - это естественно на этапе изучения")
    
    if theory_usage >= 3:
        independence_parts.append("Активно изучает теоретические материалы")
    
    if ai_usage >= 5:
        independence_parts.append("Использует ИИ-помощника для разбора сложных вопросов")
    
    return "\n".join(independence_parts)


def _generate_parent_recommendations(
    sessions_count: int,
    avg_session: float,
    consistency_score: float,
    help_usage: Dict,
    weak_areas: Dict,
    weekly_activity: Dict
) -> List[str]:
    """Генерирует рекомендации для родителей."""
    recommendations = []
    
    # Рекомендации по регулярности
    if sessions_count >= 5:
        recommendations.append("Отличная регулярность! Поддерживайте ребёнка в таком темпе")
    elif sessions_count >= 3:
        recommendations.append("Хорошая регулярность. Можно попробовать заниматься чуть чаще")
    else:
        recommendations.append("Рекомендуется установить более регулярный график занятий")
    
    # Рекомендации по продолжительности
    if avg_session > 60:
        recommendations.append("Попробуйте сократить время занятий до 30-45 минут, но заниматься чаще")
    elif avg_session > 0 and avg_session < 15:
        recommendations.append("Можно увеличить продолжительность занятий до 20-30 минут")
    
    # Рекомендации по слабым областям
    weak_themes = weak_areas.get("weak_themes", [])
    if weak_themes:
        recommendations.append(f"Стоит уделить больше внимания темам: {', '.join(weak_themes[:2])}")
    
    # Рекомендации по мотивации
    if consistency_score < 0.4:
        recommendations.append("Попробуйте создать систему поощрений за регулярные занятия")
    
    # Рекомендации по балансу
    casual_chat = weekly_activity.get("casual_chat", 0)
    if casual_chat > 15:
        recommendations.append("Ребёнок активно общается с ботом - это хороший знак вовлечённости")
    
    return recommendations


# ====================================================================
# ОТЧЕТЫ ПО КАЧЕСТВУ ИИ (ДЛЯ РАЗРАБОТЧИКОВ)
# ====================================================================

async def get_ai_quality_report(session: AsyncSession, days_back: int = DEFAULT_ANALYSIS_DAYS) -> Dict[str, Any]:
    """
    Генерирует отчет о качестве ИИ-помощника для разработчиков.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        days_back: Количество дней для анализа
        
    Returns:
        dict: Подробный отчет о качестве ИИ
    """
    try:
        logger.info(f"Генерируем отчет качества ИИ за {days_back} дней")
        
        # Получаем метрики из analytics_core
        overall_metrics = await get_ai_interaction_metrics(session, days_back)
        theme_performance = await get_ai_performance_by_themes(session, days_back)
        
        if overall_metrics.get("total_interactions", 0) == 0:
            return {"status": "insufficient_data", "message": "Недостаточно данных для анализа"}
        
        # Анализируем проблемные области
        problematic_themes = [
            theme for theme, stats in theme_performance.items()
            if stats["success_rate"] < 0.6 or stats["avg_follow_ups"] > 2.0
        ]
        
        # Формируем отчет
        report = {
            "period_days": days_back,
            "overall_metrics": overall_metrics,
            "theme_performance": theme_performance,
            "analysis": {
                "problematic_themes": problematic_themes,
                "recommendations": _generate_ai_improvement_recommendations(overall_metrics, theme_performance)
            },
            "summary": _format_ai_summary(overall_metrics, problematic_themes)
        }
        
        logger.info(f"Отчет качества ИИ успешно сгенерирован: {overall_metrics['total_interactions']} взаимодействий")
        return report
        
    except Exception as e:
        logger.error(f"Ошибка при генерации отчета качества ИИ: {e}")
        return {"status": "error", "message": str(e)}


def _generate_ai_improvement_recommendations(overall_metrics: Dict, theme_performance: Dict) -> List[str]:
    """Генерирует рекомендации по улучшению ИИ."""
    recommendations = []
    
    success_rate = overall_metrics.get("success_rate", 0)
    avg_follow_ups = overall_metrics.get("avg_follow_ups", 0)
    abandonment_rate = overall_metrics.get("abandonment_rate", 0)
    
    if success_rate < 0.7:
        recommendations.append("Низкая общая эффективность - нужно улучшить промпты")
    
    if avg_follow_ups > 2.0:
        recommendations.append("Слишком много уточняющих вопросов - ответы должны быть более полными")
    
    if abandonment_rate > 0.1:
        recommendations.append("Высокий процент отказов от задач после помощи ИИ - проверить качество объяснений")
    
    # Рекомендации по темам
    weak_themes = [
        theme for theme, stats in theme_performance.items()
        if stats["success_rate"] < 0.6
    ]
    
    if weak_themes:
        recommendations.append(f"Улучшить объяснения по темам: {', '.join(weak_themes[:3])}")
    
    return recommendations


def _format_ai_summary(overall_metrics: Dict, problematic_themes: List[str]) -> str:
    """Форматирует краткое резюме качества ИИ."""
    success_rate = overall_metrics.get("success_rate", 0)
    total_interactions = overall_metrics.get("total_interactions", 0)
    
    if success_rate >= 0.8:
        quality_level = "Отличное"
    elif success_rate >= 0.7:
        quality_level = "Хорошее"
    elif success_rate >= 0.6:
        quality_level = "Удовлетворительное"
    else:
        quality_level = "Требует улучшения"
    
    summary = f"Качество ИИ-помощника: {quality_level} ({success_rate:.1%} успех из {total_interactions} взаимодействий)"
    
    if problematic_themes:
        summary += f"\nПроблемные темы: {', '.join(problematic_themes[:3])}"
    
    return summary