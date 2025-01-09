from pydantic import BaseModel
from typing import List

class TestResultCreate(BaseModel):
    testName: str
    testTopic: str
    totalQuestions: int
    rightAnswersCount: int
    wrongAnswersCount: int
    subTopics: List[str]  # Match frontend naming

class TestResultResponse(BaseModel):
    id: int
    testName: str
    testTopic: str
    totalQuestions: int
    rightAnswersCount: int
    wrongAnswersCount: int
    subTopics: List[str]  # Match frontend naming

    class Config:
        orm_mode = True
