from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class QuestionRead(BaseModel):
    id: UUID
    company_id: UUID
    content: str
    order_index: int
    origin: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerCreate(BaseModel):
    company_id: UUID
    question_id: UUID
    content: str


class AnswerRead(BaseModel):
    id: UUID
    company_id: UUID
    question_id: UUID
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
