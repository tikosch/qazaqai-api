from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.testres import TestResultCreate, TestResultResponse
from app.crud.testres import save_test_result
from app.db.session import get_db
from app.core.security import decode_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    student_id = payload.get("UserId")
    return student_id


@router.post("/test-results", response_model=TestResultResponse)
def create_test_result(
    request: TestResultCreate,
    db: Session = Depends(get_db),
    student_id: str = Depends(get_current_user),
):
    # Save the test result in the database
    test_result = save_test_result(db, student_id, request.dict())
    return test_result  # Directly return the ORM object