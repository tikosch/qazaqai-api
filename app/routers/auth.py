from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import SignUpRequest, SignUpResponse, SignInRequest, SignInResponse
from app.db.session import get_db
from app.crud.user import create_user, add_user_role, authenticate_user
from app.crud.referral import get_teacher_referral_by_code, create_teacher_referral
from app.crud.teacher_student import create_teacher_student
from app.utils.referrals import generate_referral_code
from app.core.security import create_access_token
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

SYSTEM_ROLES_TEACHER = "Teacher"
SYSTEM_ROLES_STUDENT = "Student"

@router.post("/signup", response_model=SignUpResponse)
def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    if not request.Referral:
        teacher = create_user(db, request.Username, request.Email, request.Password)
        add_user_role(db, teacher, SYSTEM_ROLES_TEACHER)
        code = generate_referral_code()
        create_teacher_referral(db, teacher.id, code)
        return {"username": teacher.username, "email": teacher.email}  # Changed to snake_case
    else:
        teacher_ref = get_teacher_referral_by_code(db, request.Referral)
        if teacher_ref is None:
            raise HTTPException(status_code=400, detail="Invalid referral code.")
        student = create_user(db, request.Username, request.Email, request.Password)
        add_user_role(db, student, SYSTEM_ROLES_STUDENT)
        create_teacher_student(db, teacher_ref.teacher_id, student.id)
        return {"username": student.username, "email": student.email}  # Changed to snake_case

@router.post("/signin", response_model=SignInResponse)
def signin(request: SignInRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.Email, request.Password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    roles = [role.name for role in user.roles]
    if not roles:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User has no roles assigned.")
    
    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    token_data = {
        "UserId": user.id,
        "roles": roles,
    }
    token = create_access_token(token_data, access_token_expires)
    return SignInResponse(token=token)

