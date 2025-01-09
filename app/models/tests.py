from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Session
from app.db.base import Base
from app.db.session import get_db
from app.core.security import decode_token
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.types import TypeDecorator, String
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
import json


class JSONType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, nullable=False)
    test_topic = Column(String, nullable=False)
    teacher_id = Column(String, ForeignKey("users.id"), nullable=False)

    teacher = relationship("User", back_populates="tests")
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    options = Column(JSONType, nullable=False)  # Use the custom JSONType
    correct_index = Column(Integer, nullable=False)
    subtopic = Column(String, nullable=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)

    test = relationship("Test", back_populates="questions")
