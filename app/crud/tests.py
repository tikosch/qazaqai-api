from sqlalchemy.orm import Session
from app.models.tests import Test, Question
import json

def create_test(db: Session, teacher_id: str, test_data: dict):
    test = Test(
        test_name=test_data["testName"],
        test_topic=test_data["testTopic"],
        teacher_id=teacher_id
    )
    db.add(test)
    db.commit()
    db.refresh(test)

    for question_data in test_data["questions"]:
        question = Question(
            question_text=question_data["question"],
            options=json.dumps(question_data["options"]),
            correct_index=question_data["correctIndex"],
            subtopic=question_data["subtopic"],
            test_id=test.id
        )
        db.add(question)
    db.commit()
    return test

def get_test_by_id(db: Session, test_id: int):
    test = db.query(Test).filter(Test.id == test_id).first()
    return test

def serialize_test(test: Test):
    return {
        "id": test.id,
        "testName": test.test_name,
        "testTopic": test.test_topic,
        "questions": [
            {
                "id": question.id,
                "question": question.question_text,
                "options": json.loads(question.options),  # Deserialize JSON string
                "correctIndex": question.correct_index,
                "subtopic": question.subtopic,
            }
            for question in test.questions
        ]
    }

def get_all_tests(db: Session):
    tests = db.query(Test).all()
    return tests if tests else []  # Ensure it returns an empty list, not None

def delete_test_by_id(db: Session, test_id: int, teacher_id: str):
    test = db.query(Test).filter(Test.id == test_id, Test.teacher_id == teacher_id).first()
    if not test:
        return None
    db.delete(test)
    db.commit()
    return test
