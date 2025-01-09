from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Session
from app.db.base import Base
from app.db.session import get_db
from app.core.security import decode_token
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel
from typing import List

class QuestionSchema(BaseModel):
    question: str
    options: List[str]
    correctIndex: int
    subtopic: str

class CreateTestSchema(BaseModel):
    testName: str
    testTopic: str
    questions: List[QuestionSchema]

class QuestionResponse(BaseModel):
    id: int
    question: str
    options: List[str]
    correctIndex: int
    subtopic: str

    class Config:
        orm_mode = True

class TestResponse(BaseModel):
    id: int
    testName: str
    testTopic: str
    questions: List[QuestionResponse]

    class Config:
        orm_mode = True
