import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    order_index = Column(Integer, nullable=False)  # 1,2,3...
    content = Column(Text, nullable=False)
    origin = Column(String(20), nullable=False, default="system")  # system | ai

    created_at = Column(DateTime, default=datetime.utcnow)

    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="answers")
