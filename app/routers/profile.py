# app/routers/profile.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.schemas.profile import (
    TeacherProfileDetails,
    StudentProfileDetails,
    StudentDetails,
    TeacherDetails,
    TestResultInProfile,
    ModelTestResultInProfile,   # ← import for model-test schema
    CommentRequest
)
from app.core.security import decode_token
from app.models.student_comment import StudentComment
from app.models.teacher_referral import TeacherReferral
from app.models.teacher_student import TeacherStudents
from app.models.user import User
from app.models.testres import TestResult
from app.models.model_test_results import ModelTestResult   # ← import for ORM
from app.crud.student_comment import add_comment
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")

SYSTEM_ROLES_TEACHER = "Teacher"
SYSTEM_ROLES_STUDENT = "Student"


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
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

    return user, payload


@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user_and_payload=Depends(get_current_user)
):
    user, payload = current_user_and_payload
    roles = payload.get("roles", [])
    user_id = user.id

    if SYSTEM_ROLES_TEACHER in roles:
        # Fetch this teacher’s referral code
        referral = (
            db.query(TeacherReferral)
            .filter(TeacherReferral.teacher_id == user_id)
            .first()
        )

        # Find all (teacher → student) relationships
        teacher_students = (
            db.query(TeacherStudents)
            .filter(TeacherStudents.teacher_id == user_id)
            .all()
        )
        student_ids = [ts.student_id for ts in teacher_students]
        student_count = len(student_ids)

        students: list[StudentDetails] = []
        if student_ids:
            # Eagerly load each student’s test_results
            q = (
                db.query(User)
                .options(joinedload(User.test_results))
                .filter(User.id.in_(student_ids))
                .all()
            )

            for s in q:
                # 1) Fetch/serialize any comments on this student
                comments = (
                    db.query(StudentComment)
                    .filter(StudentComment.student_id == s.id)
                    .all()
                )
                serialized_comments = [c.comment for c in comments]

                # 2) Build TestResultInProfile list for this student
                test_results_in_profile = [
                    TestResultInProfile(
                        testName=tr.testName,
                        testTopic=tr.testTopic,
                        totalQuestions=tr.totalQuestions,
                        rightAnswersCount=tr.rightAnswersCount,
                        wrongAnswersCount=tr.wrongAnswersCount,
                        subTopics=tr.subTopics
                    )
                    for tr in s.test_results
                ]

                # 3) ***NEW*** Fetch/serialize each student’s ModelTestResult rows
                model_test_results = (
                    db.query(ModelTestResult)
                    .filter(ModelTestResult.student_id == s.id)
                    .all()
                )
                serialized_model_test_results = [
                    ModelTestResultInProfile(
                        question=m.question,
                        user_answer=m.user_answer,
                        similarity_score=m.similarity_score
                    )
                    for m in model_test_results
                ]

                # 4) Append StudentDetails (including TestResults, Comments, ModelTestResults)
                students.append(
                    StudentDetails(
                        StudentId=str(s.id),
                        StudentName=s.username,
                        TestResults=test_results_in_profile,
                        Comments=serialized_comments,
                        ModelTestResults=serialized_model_test_results   # ← include here
                    )
                )

        return TeacherProfileDetails(
            Id=str(user_id),
            UserName=user.username,
            Email=user.email,
            PhoneNumber=user.phone_number or "",
            ReferralCode=referral.referral if referral else "",
            StudentCount=student_count,
            Role=SYSTEM_ROLES_TEACHER,
            Students=students
        )

    elif SYSTEM_ROLES_STUDENT in roles:
        # (Unchanged) Student’s own view
        teacher_student = (
            db.query(TeacherStudents)
            .filter(TeacherStudents.student_id == user_id)
            .first()
        )
        if not teacher_student:
            raise HTTPException(status_code=404, detail="Student-Teacher relationship not found.")
        teacher = (
            db.query(User)
            .filter(User.id == teacher_student.teacher_id)
            .first()
        )
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found.")

        # Fetch test results for the current student
        test_results = (
            db.query(TestResult)
            .filter(TestResult.student_id == user_id)
            .all()
        )
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

        # Fetch model‐generated test results
        model_test_results = (
            db.query(ModelTestResult)
            .filter(ModelTestResult.student_id == user_id)
            .all()
        )
        serialized_model_test_results = [
            ModelTestResultInProfile(
                question=m.question,
                user_answer=m.user_answer,
                similarity_score=m.similarity_score
            )
            for m in model_test_results
        ]

        # Fetch comments from the teacher for the student
        comments = (
            db.query(StudentComment)
            .filter(StudentComment.student_id == user_id)
            .all()
        )
        serialized_comments = [c.comment for c in comments]

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
            Comments=serialized_comments
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
    return {
        "message": "Comment added successfully",
        "comment": student_comment.comment
    }
