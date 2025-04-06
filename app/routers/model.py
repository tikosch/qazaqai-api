from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import pandas as pd
from app.schemas.question import QuestionRequest
from app.db.session import get_db
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse
from app.crud.evaluation import calculate_similarity_score
from app.core.security import decode_token
from app.utils.semantic_search import find_most_similar_context, get_random_question, get_context_by_id
from app.utils.question_answering import get_model_answer
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.models.model_test_results import ModelTestResult


router = APIRouter()

# Specify the model identifier from Hugging Face
model_identifier = "Kundyzka/XLM-Roberta-large-informatics-kaz"  # Replace with your actual model identifier

# Load model and tokenizer from Hugging Face
tokenizer = AutoTokenizer.from_pretrained(model_identifier)
model = AutoModelForQuestionAnswering.from_pretrained(model_identifier)
model.eval()

# Load the CSV
df = pd.read_csv("filtered_csv.csv")


@router.post("/get-answer", response_model=dict)
def get_context_and_answer(request: QuestionRequest):
    """Fetch context using semantic search and then get the model's answer."""
    user_question = request.question
    context, matched_question = find_most_similar_context(user_question)

    model_answer = get_model_answer(user_question, context)

    return {
        "user_question": user_question,
        "matched_question": matched_question,
        "context": context,
        "model_answer": model_answer
    }

@router.get("/ask-random-question", response_model=dict)
def ask_random_question():
    """Fetch a random question with a unique ID."""
    question_id, question, context = get_random_question()
    return {"id": question_id, "question": question, "context": context}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")

@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_answer(
    request: EvaluationCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Evaluate the user's answer and save the result to the database."""
    # Decode token and get user ID
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("UserId")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Validate question ID
    question, context = get_context_by_id(request.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Invalid question ID")

    # Predict the model's answer
    model_answer = get_model_answer(question, context)

    # Calculate similarity score
    similarity_score = calculate_similarity_score(request.user_answer, model_answer)
    is_correct = similarity_score >= 80.0  # Consider >=80% as correct

    # Save the evaluation result in the database
    new_result = ModelTestResult(
        student_id=user_id,
        question=question,
        user_answer=request.user_answer,
        similarity_score=similarity_score
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)

    return {
        "id": new_result.id,
        "question": question,
        "context": context,
        "model_answer": model_answer,
        "user_answer": request.user_answer,
        "is_correct": is_correct,
        "similarity_score": similarity_score
    }