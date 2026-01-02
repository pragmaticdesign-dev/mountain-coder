from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class TestCaseBase(BaseModel):
    input_data: str
    expected_output: str
    is_public: bool = False

class QuestionCreate(BaseModel):
    title: str
    description: str
    hints: List[str] = []
    boilerplate_python: str
    boilerplate_java: str
    test_cases: List[TestCaseBase] = []

class QuestionSummary(BaseModel):
    id: int
    title: str
    description: str

class CardResponse(BaseModel):
    id: int
    title: str
    description: str
    questions: List[QuestionSummary]

class SubmitRequest(BaseModel):
    question_id: int
    language: str  
    code: str

class SubmitResponse(BaseModel):
    status: str
    total_passed: int
    total_tests: int
    runtime: float
    details: List[Any]