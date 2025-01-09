from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class TeacherReferral(Base):
    __tablename__ = "teacher_referrals"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("users.id"))
    referral = Column(String, unique=True, index=True)

    teacher = relationship("User")
