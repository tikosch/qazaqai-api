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
    CommentRequest,
    ModelTestResultInProfile
)
from app.core.security import decode_token
from app.models.student_comment import StudentComment
from app.models.teacher_referral import TeacherReferral
from app.models.teacher_student import TeacherStudents
from app.models.user import User
from app.models.testres import TestResult
from app.models.model_test_results import ModelTestResult
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
    """
    Decode the JWT, fetch the User from the DB, and return (user, payload).
    Raises 401 if token is invalid or user not found.
    """
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
    """
    If the current user is a Teacher:
      - Fetch referral code
      - Fetch all TeacherStudents rows for this teacher
      - For each student, eagerly load test_results and package into TestResultInProfile
      - Also fetch any StudentComment rows (serialize to List[str])
      - Return TeacherProfileDetails including Students: List[StudentDetails]

    If the current user is a Student:
      - Fetch that student’s TestResult rows (serialize into TestResultInProfile)
      - Fetch ModelTestResult rows (serialize into ModelTestResultInProfile)
      - Fetch any StudentComment rows (serialize to List[str])
      - Return StudentProfileDetails

    Otherwise, raise 403.
    """
    user, payload = current_user_and_payload
    roles = payload.get("roles", [])
    user_id = user.id

    if SYSTEM_ROLES_TEACHER in roles:
        # 1) Fetch referral code (if any)
        referral = (
            db.query(TeacherReferral)
            .filter(TeacherReferral.teacher_id == user_id)
            .first()
        )

        # 2) Find all students linked to this teacher
        teacher_students = (
            db.query(TeacherStudents)
            .filter(TeacherStudents.teacher_id == user_id)
            .all()
        )
        student_ids = [ts.student_id for ts in teacher_students]
        student_count = len(student_ids)

        students: list[StudentDetails] = []
        if student_ids:
            # 3) Eagerly load each User.test_results
            q = (
                db.query(User)
                .options(joinedload(User.test_results))
                .filter(User.id.in_(student_ids))
                .all()
            )

            for s in q:
                # 4) Serialize comments on this student
                comments = (
                    db.query(StudentComment)
                    .filter(StudentComment.student_id == s.id)
                    .all()
                )
                serialized_comments = [c.comment for c in comments]

                # 5) Build TestResultInProfile list for this student
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

                # 6) Append StudentDetails (including TestResults and Comments)
                students.append(
                    StudentDetails(
                        StudentId=str(s.id),
                        StudentName=s.username,
                        TestResults=test_results_in_profile,
                        Comments=serialized_comments
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
        # 1) Verify that this student is linked to a teacher
        teacher_student = (
            db.query(TeacherStudents)
            .filter(TeacherStudents.student_id == user_id)
            .first()
        )
        if not teacher_student:
            raise HTTPException(
                status_code=404,
                detail="Student-Teacher relationship not found."
            )

        # 2) Fetch the teacher’s User record
        teacher = (
            db.query(User)
            .filter(User.id == teacher_student.teacher_id)
            .first()
        )
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found.")

        # 3) Fetch this student’s TestResult rows
        test_results = (
            db.query(TestResult)
            .filter(TestResult.student_id == user_id)
            .all()
        )
        serialized_results = [
            TestResultInProfile(
                testName=tr.testName,
                testTopic=tr.testTopic,
                totalQuestions=tr.totalQuestions,
                rightAnswersCount=tr.rightAnswersCount,
                wrongAnswersCount=tr.wrongAnswersCount,
                subTopics=tr.subTopics
            )
            for tr in test_results
        ]

        # 4) Fetch ModelTestResult rows
        model_test_results = (
            db.query(ModelTestResult)
            .filter(ModelTestResult.student_id == user_id)
            .all()
        )
        serialized_model_test_results: list[ModelTestResultInProfile] = [
            ModelTestResultInProfile(
                question=m.question,
                user_answer=m.user_answer,
                similarity_score=m.similarity_score
            )
            for m in model_test_results
        ]

        # 5) Fetch any comments left by the teacher on this student
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
    """
    Only teachers can call this endpoint. It inserts a new StudentComment,
    linking the teacher to the given student_id with the provided comment text.
    """
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
