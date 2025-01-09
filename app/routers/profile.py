from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.schemas.profile import TeacherProfileDetails, StudentProfileDetails, StudentDetails, TeacherDetails, TestResultInProfile, CommentRequest
from app.core.security import decode_token
from app.models.student_comment import StudentComment
from app.models.teacher_referral import TeacherReferral
from app.models.teacher_student import TeacherStudents
from app.models.user import User
from app.models.testres import TestResult
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.crud.student_comment import add_comment
from app.models.model_test_results import ModelTestResult

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")

SYSTEM_ROLES_TEACHER = "Teacher"
SYSTEM_ROLES_STUDENT = "Student"

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        user_id: str = payload.get("UserId")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user, payload  # Return both user and payload

@router.get("/profile")
def get_profile(db: Session = Depends(get_db), current_user_and_payload=Depends(get_current_user)):
    user, payload = current_user_and_payload
    roles = payload.get("roles", [])
    user_id = user.id

    if SYSTEM_ROLES_TEACHER in roles:
        referral = db.query(TeacherReferral).filter(TeacherReferral.teacher_id == user_id).first()
        teacher_students = db.query(TeacherStudents).filter(TeacherStudents.teacher_id == user_id).all()
        count = len(teacher_students)
        student_ids = [ts.student_id for ts in teacher_students]

        students = []
        if student_ids:
            q = db.query(User).options(joinedload(User.test_results)).filter(User.id.in_(student_ids)).all()
            for s in q:
                comments = db.query(StudentComment).filter(StudentComment.student_id == s.id).all()
                serialized_comments = [comment.comment for comment in comments]
                students.append(
                    StudentDetails(
                        StudentId=str(s.id),
                        StudentName=s.username,
                        TestResults=[
                            TestResultInProfile(
                                testName=tr.testName,
                                testTopic=tr.testTopic,
                                totalQuestions=tr.totalQuestions,
                                rightAnswersCount=tr.rightAnswersCount,
                                wrongAnswersCount=tr.wrongAnswersCount,
                                subTopics=tr.subTopics
                            )
                            for tr in s.test_results
                        ],
                        Comments=serialized_comments
                    )
                )

            
        return TeacherProfileDetails(
            Id=str(user_id),
            UserName=user.username,
            Email=user.email,
            PhoneNumber=user.phone_number or "",
            ReferralCode=referral.referral if referral else "",
            StudentCount=count,
            Role=SYSTEM_ROLES_TEACHER,
            Students=students
        )
    elif SYSTEM_ROLES_STUDENT in roles:
        teacher_student = db.query(TeacherStudents).filter(TeacherStudents.student_id == user_id).first()
        if not teacher_student:
            raise HTTPException(status_code=404, detail="Student-Teacher relationship not found.")
        teacher = db.query(User).filter(User.id == teacher_student.teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found.")

        # Fetch test results for the current student
        test_results = db.query(TestResult).filter(TestResult.student_id == user_id).all()
        serialized_results = [
            TestResultInProfile(
                testName=result.testName,
                testTopic=result.testTopic,
                totalQuestions=result.totalQuestions,
                rightAnswersCount=result.rightAnswersCount,
                wrongAnswersCount=result.wrongAnswersCount,
                subTopics=result.subTopics
            )
            for result in test_results
        ]
        model_test_results = db.query(ModelTestResult).filter(ModelTestResult.student_id == user_id).all()
        serialized_model_test_results = [
        {
            "question": result.question,
            "user_answer": result.user_answer,
            "similarity_score": result.similarity_score
        }
        for result in model_test_results
    ]

        # Fetch comments from the teacher for the student
        comments = db.query(StudentComment).filter(StudentComment.student_id == user_id).all()
        serialized_comments = [comment.comment for comment in comments]

        return StudentProfileDetails(
            Id=str(user_id),
            UserName=user.username,
            Email=user.email,
            PhoneNumber=user.phone_number or "",
            Teacher=TeacherDetails(
                TeacherId=str(teacher.id),
                TeacherName=teacher.username
            ),
            TestResults=serialized_results,
            ModelTestResults=serialized_model_test_results,
            Comments=serialized_comments  # Include comments in the response
        )
    else:
        raise HTTPException(status_code=403, detail="Role not supported")

@router.post("/students/{student_id}/comments")
def add_student_comment(
    student_id: str,
    request: CommentRequest,
    db: Session = Depends(get_db),
    current_user_and_payload=Depends(get_current_user)
):
    user, payload = current_user_and_payload
    roles = payload.get("roles", [])
    if SYSTEM_ROLES_TEACHER not in roles:
        raise HTTPException(status_code=403, detail="Only teachers can add comments.")

    teacher_id = user.id
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    student_comment = add_comment(db, teacher_id, student_id, request.comment)
    return {"message": "Comment added successfully", "comment": student_comment.comment}