from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class TeacherStudents(Base):
    __tablename__ = "teacher_students"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("users.id"))
    student_id = Column(String, ForeignKey("users.id"))

    teacher = relationship("User", foreign_keys=[teacher_id])
    student = relationship("User", foreign_keys=[student_id])
