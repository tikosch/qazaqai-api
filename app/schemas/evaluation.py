from pydantic import BaseModel

class EvaluationCreate(BaseModel):
    question_id: int
    user_answer: str


class EvaluationResponse(BaseModel):
    id: int
    question: str
    context: str
    model_answer: str
    user_answer: str
    is_correct: bool
    similarity_score: float

    class Config:
        orm_mode = True
