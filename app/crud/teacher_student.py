from sqlalchemy.orm import Session
from app.models.teacher_student import TeacherStudents

def create_teacher_student(db: Session, teacher_id: str, student_id: str):
    ts = TeacherStudents(teacher_id=teacher_id, student_id=student_id)
    db.add(ts)
    db.commit()
    db.refresh(ts)
    return ts
