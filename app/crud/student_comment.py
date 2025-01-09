from sqlalchemy.orm import Session
from app.models.student_comment import StudentComment

def add_comment(db: Session, teacher_id: str, student_id: str, comment: str) -> StudentComment:
    student_comment = StudentComment(
        teacher_id=teacher_id,
        student_id=student_id,
        comment=comment
    )
    db.add(student_comment)
    db.commit()
    db.refresh(student_comment)
    return student_comment

def get_comments_for_student(db: Session, student_id: str):
    return db.query(StudentComment).filter(StudentComment.student_id == student_id).all()
