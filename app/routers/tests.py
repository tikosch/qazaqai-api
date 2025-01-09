from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Session
from app.db.base import Base
from app.db.session import get_db
from app.core.security import decode_token
from app.schemas.tests import TestResponse, CreateTestSchema
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.models.tests import Test
from app.crud.tests import create_test, get_test_by_id, serialize_test, delete_test_by_id
import json

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

@router.post("/tests", response_model=TestResponse)
def create_test_endpoint(
    request: CreateTestSchema,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    payload = decode_token(token)
    teacher_id = payload.get("UserId")
    roles = payload.get("roles", [])
    if "Teacher" not in roles:
        raise HTTPException(status_code=403, detail="Only teachers can create tests.")

    test = create_test(db, teacher_id, request.dict())
    return serialize_test(test)


@router.get("/tests/{test_id}", response_model=TestResponse)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    return serialize_test(test)

@router.get("/tests", response_model=List[dict])
def get_all_tests(db: Session = Depends(get_db)):
    tests = db.query(Test).all()

    if not tests:
        return []  # Return an empty list if no tests exist

    # Use the serialize_test function to format each test
    return [serialize_test(test) for test in tests]

@router.delete("/tests/{test_id}", status_code=204)
def delete_test(
    test_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user, payload = get_current_user(db, token)
    roles = payload.get("roles", [])
    if "Teacher" not in roles:
        raise HTTPException(status_code=403, detail="Only teachers can delete tests.")

    deleted_test = delete_test_by_id(db, test_id, user.id)
    if not deleted_test:
        raise HTTPException(status_code=404, detail="Test not found or you do not have permission to delete it.")
