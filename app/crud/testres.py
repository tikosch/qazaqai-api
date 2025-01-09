from sqlalchemy.orm import Session
from app.models.testres import TestResult

def save_test_result(db: Session, student_id: str, result_data: dict):
    test_result = TestResult(
        student_id=student_id,
        testName=result_data["testName"],
        testTopic=result_data["testTopic"],
        totalQuestions=result_data["totalQuestions"],
        rightAnswersCount=result_data["rightAnswersCount"],
        wrongAnswersCount=result_data["wrongAnswersCount"],
        subTopics=result_data["subTopics"],
    )
    db.add(test_result)
    db.commit()
    db.refresh(test_result)
    return test_result

def get_test_results_for_student(db: Session, student_id: str):
    return db.query(TestResult).filter(TestResult.student_id == student_id).all()
