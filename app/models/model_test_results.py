from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class ModelTestResult(Base):
    __tablename__ = "model_test_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("users.id"), nullable=False)
    question = Column(String, nullable=False)
    user_answer = Column(String, nullable=False)
    similarity_score = Column(Float, nullable=False)

    student = relationship("User", back_populates="model_test_results")
