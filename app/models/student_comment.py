from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class StudentComment(Base):
    __tablename__ = "student_comments"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("users.id"), nullable=False)
    student_id = Column(String, ForeignKey("users.id"), nullable=False)
    comment = Column(String, nullable=False)

    teacher = relationship("User", foreign_keys=[teacher_id])
    student = relationship("User", foreign_keys=[student_id])