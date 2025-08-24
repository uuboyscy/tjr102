from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    text,
)

from .base import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {"schema": "ops"}

    id = Column(Integer, primary_key=True)
    table_name = Column(Text, nullable=False)
    task_type = Column(String(20), nullable=False)
    task_status = Column(Integer, nullable=False, default=0)
    task_args = Column(Text, nullable=False, default="")
    file_count = Column(Integer, nullable=False, default=0)
    file_names = Column(Text, nullable=False, default="")
    file_checksum = Column(String(32), nullable=False, default="")
    wc_count = Column(Integer, nullable=False, default=0)
    db_count = Column(Integer, nullable=False, default=0)
    error_type = Column(Integer, nullable=False, default=0)
    load_start = Column(DateTime)
    load_end = Column(DateTime)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"))
