from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("users.id"), nullable=False)
    testName = Column(String, nullable=False)  # Match frontend naming
    testTopic = Column(String, nullable=False)  # Match frontend naming
    totalQuestions = Column(Integer, nullable=False)  # Match frontend naming
    rightAnswersCount = Column(Integer, nullable=False)  # Match frontend naming
    wrongAnswersCount = Column(Integer, nullable=False)  # Match frontend naming
    subTopics = Column(JSON, nullable=False)  # Match frontend naming (JSON for a list of strings)

    student = relationship("User", back_populates="test_results")
