from pydantic import BaseModel, EmailStr
from typing import Optional, List

class TestResultInProfile(BaseModel):
    testName: str
    testTopic: str
    totalQuestions: int
    rightAnswersCount: int
    wrongAnswersCount: int
    subTopics: List[str]

    class Config:
        orm_mode = True

class StudentDetails(BaseModel):
    StudentId: str
    StudentName: str
    TestResults: List[TestResultInProfile]
    Comments: List[str]

class TeacherDetails(BaseModel):
    TeacherId: str
    TeacherName: str

class TeacherProfileDetails(BaseModel):
    Id: str
    UserName: str
    Email: EmailStr
    StudentCount: int
    PhoneNumber: str
    Role: str
    ReferralCode: Optional[str]
    Students: Optional[List[StudentDetails]] = None
    
    class Config:
        orm_mode = True

class ModelTestResultInProfile(BaseModel):
    question: str
    user_answer: str
    similarity_score: float

    class Config:
        orm_mode = True

class StudentProfileDetails(BaseModel):
    Id: str
    UserName: str
    Email: EmailStr
    PhoneNumber: str
    Teacher: TeacherDetails
    TestResults: List[TestResultInProfile]
    ModelTestResults: List[ModelTestResultInProfile]  # New field for model test results
    Comments: List[str]

    class Config:
        orm_mode = True

class UserProfileResponse(BaseModel):
    # Define fields based on your requirements
    id: str
    username: str
    email: EmailStr
    phone_number: Optional[str]
    roles: List[str]
    # Add other fields as needed

    class Config:
        orm_mode = True

from typing import List

class CommentRequest(BaseModel):
    comment: str