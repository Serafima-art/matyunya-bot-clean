"""
Модели базы данных для проекта "Матюня"
SQLAlchemy 2.0 модели для профессиональной аналитики
"""
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    parent_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи с другими таблицами
    answer_logs: Mapped[List["AnswerLog"]] = relationship("AnswerLog", back_populates="user")
    activity_logs: Mapped[List["ActivityLog"]] = relationship("ActivityLog", back_populates="user")
    session_logs: Mapped[List["SessionLog"]] = relationship("SessionLog", back_populates="user")
    ai_interactions: Mapped[List["AIInteractionLog"]] = relationship("AIInteractionLog", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name='{self.name}')>"


class SkillType(Base):
    """Справочник навыков — типы задач ОГЭ"""
    __tablename__ = "skill_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    task_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Связи с другими таблицами
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="skill_type")
    
    def __repr__(self) -> str:
        return f"<SkillType(id={self.id}, source_id='{self.source_id}', name='{self.name}', task_number='{self.task_number}')>"


class Task(Base):
    """Журнал сгенерированных задач"""
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("skill_types.id"), nullable=False)
    theme: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # "Шины", "Квартиры", "Печи"
    text: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи с другими таблицами
    skill_type: Mapped["SkillType"] = relationship("SkillType", back_populates="tasks")
    answer_logs: Mapped[List["AnswerLog"]] = relationship("AnswerLog", back_populates="task")
    activity_logs: Mapped[List["ActivityLog"]] = relationship("ActivityLog", back_populates="task")
    ai_interactions: Mapped[List["AIInteractionLog"]] = relationship("AIInteractionLog", back_populates="task")
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, skill_type_id={self.skill_type_id}, theme='{self.theme}', text='{self.text[:50]}...', answer='{self.answer}')>"


class AnswerLog(Base):
    """Лог ответов пользователей"""
    __tablename__ = "answer_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_answer: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # ответ пользователя
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_spent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # время в секундах
    help_used: Mapped[bool] = mapped_column(Boolean, default=False)  # использовал любую помощь
    is_timed: Mapped[bool] = mapped_column(Boolean, default=False)  # режим "На время"
    pack_session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # для группировки в паки
    generated_task_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON с полной информацией об ошибочной задаче
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи с другими таблицами
    user: Mapped["User"] = relationship("User", back_populates="answer_logs")
    task: Mapped["Task"] = relationship("Task", back_populates="answer_logs")
    
    def __repr__(self) -> str:
        return f"<AnswerLog(id={self.id}, user_id={self.user_id}, task_id={self.task_id}, is_correct={self.is_correct})>"


class ActivityLog(Base):
    """Лог активности пользователей - все действия в боте"""
    __tablename__ = "activity_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    task_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=True)  # для привязки к заданию
    activity_type: Mapped[str] = mapped_column(String, nullable=False)  
    # Типы: 'help_general', 'help_ai_chat', 'theory', 'casual_chat', 'timed_mode', 'theme_pack_start', 'exam_pack_start'
    pack_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # 'theme' или 'exam'
    pack_theme: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # для тематических паков
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи с другими таблицами
    user: Mapped["User"] = relationship("User", back_populates="activity_logs")
    task: Mapped[Optional["Task"]] = relationship("Task", back_populates="activity_logs")
    
    def __repr__(self) -> str:
        return f"<ActivityLog(id={self.id}, user_id={self.user_id}, activity_type='{self.activity_type}', pack_type='{self.pack_type}')>"


class SessionLog(Base):
    """Лог сессий работы пользователей"""
    __tablename__ = "session_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_start: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    session_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    tasks_attempted: Mapped[int] = mapped_column(Integer, default=0)  # количество попыток решения задач
    activities_count: Mapped[int] = mapped_column(Integer, default=0)  # общее количество действий
    session_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # 'study', 'casual', 'mixed'
    
    # Связи с другими таблицами
    user: Mapped["User"] = relationship("User", back_populates="session_logs")
    
    def __repr__(self) -> str:
        return f"<SessionLog(id={self.id}, user_id={self.user_id}, session_type='{self.session_type}', tasks_attempted={self.tasks_attempted})>"


class AIInteractionLog(Base):
    """Лог взаимодействий с ИИ для анализа качества помощи"""
    __tablename__ = "ai_interaction_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    task_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    # Содержание взаимодействия
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # автокатегоризация
    task_theme: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # тема задачи, по которой спросили
    
    # Косвенные индикаторы качества ИИ
    is_repeat_question: Mapped[bool] = mapped_column(Boolean, default=False)  # повторный вопрос по той же задаче
    follow_up_count: Mapped[int] = mapped_column(Integer, default=0)  # количество уточнений в диалоге
    used_theory_after: Mapped[bool] = mapped_column(Boolean, default=False)  # обратился к теории после ИИ
    solved_task_after: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # решил задачу в итоге
    time_to_solution: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # секунд от вопроса до решения
    abandoned_task: Mapped[bool] = mapped_column(Boolean, default=False)  # бросил задачу после ИИ
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи с другими таблицами
    user: Mapped["User"] = relationship("User", back_populates="ai_interactions")
    task: Mapped[Optional["Task"]] = relationship("Task", back_populates="ai_interactions")
    
    def __repr__(self) -> str:
        return f"<AIInteractionLog(id={self.id}, user_id={self.user_id}, task_id={self.task_id}, question_category='{self.question_category}')>"