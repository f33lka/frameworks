# backend/app/models.py
from datetime import datetime
from enum import Enum

import bcrypt
from sqlalchemy import (Boolean, Column, DateTime, Enum as SaEnum, ForeignKey,
                        Integer, LargeBinary, Numeric, String, Table, Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ---------------------------------------------------------------------------
# Перечисления
# ---------------------------------------------------------------------------
class RoleEnum(str, Enum):
    ENGINEER = "engineer"
    MANAGER = "manager"
    OBSERVER = "observer"


class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StatusEnum(str, Enum):
    NEW = "new"
    IN_WORK = "in_work"
    ON_CHECK = "on_check"
    CLOSED = "closed"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Пользователи и роли
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    role = Column(SaEnum(RoleEnum), nullable=False, default=RoleEnum.ENGINEER)
    _password_hash = Column("password_hash", LargeBinary(60), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # связи
    created_defects = relationship("Defect", back_populates="creator", foreign_keys="Defect.created_by")
    assigned_defects = relationship("Defect", back_populates="assignee", foreign_keys="Defect.assigned_to")
    comments = relationship("Comment", back_populates="author")
    history_records = relationship("History", back_populates="user")

    # --------- пароль через bcrypt ----------
    @property
    def password(self):
        raise AttributeError("password is write-only")

    @password.setter
    def password(self, raw_password: str) -> None:
        self._password_hash = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())

    def verify_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(raw_password.encode("utf-8"), self._password_hash)


# ---------------------------------------------------------------------------
# Проекты (строительные объекты)
# ---------------------------------------------------------------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    stages = relationship("Stage", back_populates="project", cascade="all, delete-orphan")
    defects = relationship("Defect", back_populates="project")


# ---------------------------------------------------------------------------
# Этапы строительства (внутри проекта)
# ---------------------------------------------------------------------------
class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="stages")
    defects = relationship("Defect", back_populates="stage")


# ---------------------------------------------------------------------------
# Дефекты
# ---------------------------------------------------------------------------
class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(SaEnum(PriorityEnum), default=PriorityEnum.MEDIUM)
    status = Column(SaEnum(StatusEnum), default=StatusEnum.NEW)

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id", ondelete="SET NULL"), nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # связи
    project = relationship("Project", back_populates="defects")
    stage = relationship("Stage", back_populates="defects")
    creator = relationship("User", back_populates="created_defects", foreign_keys=[created_by])
    assignee = relationship("User", back_populates="assigned_defects", foreign_keys=[assigned_to])
    comments = relationship("Comment", back_populates="defect", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="defect", cascade="all, delete-orphan")
    history = relationship("History", back_populates="defect", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Комментарии к дефекту
# ---------------------------------------------------------------------------
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    defect_id = Column(Integer, ForeignKey("defects.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    defect = relationship("Defect", back_populates="comments")
    author = relationship("User", back_populates="comments")


# ---------------------------------------------------------------------------
# Вложения (фото, документы)
# ---------------------------------------------------------------------------
class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)
    defect_id = Column(Integer, ForeignKey("defects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)          # оригинальное имя
    stored_path = Column(String(500), nullable=False)       # путь на диске
    file_size = Column(Integer)                             # байты
    mime_type = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    defect = relationship("Defect", back_populates="attachments")


# ---------------------------------------------------------------------------
# История изменений дефекта
# ---------------------------------------------------------------------------
class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    defect_id = Column(Integer, ForeignKey("defects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    field_name = Column(String(50), nullable=False)   # какое поле изменили
    old_value = Column(Text)
    new_value = Column(Text)
    changed_at = Column(DateTime, default=datetime.utcnow)

    defect = relationship("Defect", back_populates="history")
    user = relationship("User", back_populates="history_records")