from sqlalchemy.orm import Session
from app.models.evaluation import Evaluation
from app.schemas.evaluation import EvaluationCreate
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from Levenshtein import ratio as levenshtein_ratio


def create_evaluation(db: Session, user_id: str, evaluation_data: dict):
    evaluation = Evaluation(
        user_id=user_id,
        question=evaluation_data["question"],
        context=evaluation_data["context"],
        user_answer=evaluation_data["user_answer"],
        model_answer=evaluation_data["model_answer"],
        is_correct=evaluation_data["is_correct"],
        similarity_score=evaluation_data["similarity_score"],
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation

def calculate_similarity_score(user_answer: str, model_answer: str) -> float:
    """
    Calculate similarity score using a combination of cosine similarity
    and Levenshtein distance.
    """
    # Normalize answers
    user_answer = user_answer.strip().lower()
    model_answer = model_answer.strip().lower()

    # Cosine similarity using TF-IDF
    vectorizer = TfidfVectorizer().fit_transform([user_answer, model_answer])
    vectors = vectorizer.toarray()
    cosine_sim = np.dot(vectors[0], vectors[1]) / (np.linalg.norm(vectors[0]) * np.linalg.norm(vectors[1]))

    # Levenshtein similarity
    levenshtein_sim = levenshtein_ratio(user_answer, model_answer)

    # Weighted average (adjust weights as needed)
    similarity_score = (0.7 * cosine_sim + 0.3 * levenshtein_sim) * 100

    return round(similarity_score, 2)
