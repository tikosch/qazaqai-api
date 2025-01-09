from sqlalchemy.orm import Session
from app.models.teacher_referral import TeacherReferral

def get_teacher_referral_by_code(db: Session, code: str) -> TeacherReferral:
    return db.query(TeacherReferral).filter(TeacherReferral.referral == code).first()

def create_teacher_referral(db: Session, teacher_id: str, referral_code: str):
    ref = TeacherReferral(teacher_id=teacher_id, referral=referral_code)
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ref
