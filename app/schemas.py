from pydantic import BaseModel
from typing import List, Optional, Any

# --- Shared Models ---
class TestCaseBase(BaseModel):
    input_data: str
    expected_output: str
    is_public: bool = False

# --- Question Creation (Admin) ---
class QuestionCreate(BaseModel):
    id: Optional[int] = None  # <--- NEW: Allow manual ID (e.g., 1 for Two Sum)
    title: str
    description: str
    input_format: str
    output_format: str
    solution: str
    tags: List[str] = []
    difficulty: str = "Medium"
    hints: List[str] = []
    boilerplate_python: str
    boilerplate_java: str
    test_cases: List[TestCaseBase] = []

# --- Responses for Lists (Dashboard/Table) ---
class QuestionSummary(BaseModel):
    id: int
    title: str
    difficulty: Optional[str] = "Medium" # Use Optional to prevent 422 if DB is empty
    tags: List[str] = []

# --- Responses for IDE (Full Details) ---
class QuestionDetail(BaseModel):
    id: int
    title: str
    description: str
    input_format: str
    output_format: str
    solution: str
    hints: List[str]
    boilerplate: dict
    examples: List[dict]

# --- Card Models ---
class CardCreate(BaseModel):
    title: str
    description: str

class CardResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = "" # Handle cases where description might be missing
    question_count: int             # The router MUST return this field

# --- Submission Models ---
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

class RunRequest(BaseModel):
    language: str
    code: str
    input_data: str