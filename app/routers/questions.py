from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import models, schemas
from database import get_db

router = APIRouter(tags=["Questions"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def build_card_response(card: models.Card) -> dict:
    """Build card response with question count"""
    return {
        "id": card.id,
        "title": card.title,
        "description": card.description,
        "question_count": len(card.questions)
    }


def build_question_summary(question: models.Question) -> dict:
    """Build question summary response"""
    return {
        "id": question.id,
        "title": question.title,
        "difficulty": question.difficulty or "Medium",
        "tags": question.tags or []
    }


def build_question_detail(question: models.Question) -> dict:
    """Build detailed question response"""
    return {
        "id": question.id,
        "title": question.title,
        "description": question.description,
        "input_format": question.input_format,
        "output_format": question.output_format,
        "solution": question.solution,
        "hints": question.hints,
        "boilerplate": {
            "python": question.boilerplate_python,
            "java": question.boilerplate_java
        },
        "examples": [
            {"input": tc.input_data, "output": tc.expected_output}
            for tc in question.test_cases if tc.is_public
        ]
    }


def create_test_cases(question_id: int, test_cases: List, db: Session):
    """Create test cases for a question"""
    for tc in test_cases:
        new_tc = models.TestCase(
            question_id=question_id,
            input_data=tc.input_data,
            expected_output=tc.expected_output,
            is_public=tc.is_public
        )
        db.add(new_tc)


def apply_search_filters(query, search_text: Optional[str], difficulty: Optional[str]):
    """Apply text search and difficulty filters"""
    if search_text:
        pattern = f"%{search_text}%"
        query = query.filter(
            or_(
                models.Question.title.ilike(pattern),
                models.Question.description.ilike(pattern)
            )
        )
    
    if difficulty:
        query = query.filter(models.Question.difficulty == difficulty)
    
    return query


def filter_by_tag(questions: List[models.Question], tag: str) -> List[models.Question]:
    """Filter questions by specific tag"""
    return [
        q for q in questions 
        if tag.lower() in [t.lower() for t in (q.tags or [])]
    ]


def find_questions_by_tag(search_text: str, existing_ids: set, db: Session) -> List[models.Question]:
    """Find additional questions matching search text in tags"""
    all_questions = db.query(models.Question).all()
    return [
        q for q in all_questions
        if q.id not in existing_ids 
        and any(search_text.lower() in t.lower() for t in (q.tags or []))
    ]


# ============================================================================
# CARD ENDPOINTS
# ============================================================================

@router.post("/cards", response_model=schemas.CardResponse)
def create_card(card: schemas.CardCreate, db: Session = Depends(get_db)):
    """Create a new card"""
    new_card = models.Card(title=card.title, description=card.description)
    db.add(new_card)
    db.commit()
    return build_card_response(new_card)


@router.get("/questions/cards", response_model=List[schemas.CardResponse])
def get_cards(db: Session = Depends(get_db)):
    """Get all dashboard cards"""
    cards = db.query(models.Card).all()
    return [build_card_response(c) for c in cards]


@router.get("/questions/cards/{card_id}/questions", response_model=List[schemas.QuestionSummary])
def get_card_questions(card_id: int, db: Session = Depends(get_db)):
    """Get all questions in a specific card"""
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        return []
    return [build_question_summary(q) for q in card.questions]


@router.post("/cards/{card_id}/add_question/{q_id}")
def add_question_to_card(card_id: int, q_id: int, db: Session = Depends(get_db)):
    """Link a question to a card"""
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    question = db.query(models.Question).filter(models.Question.id == q_id).first()
    
    if not card or not question:
        raise HTTPException(status_code=404, detail="Card or Question not found")
    
    if question not in card.questions:
        card.questions.append(question)
        db.commit()
    
    return {"status": "added", "card": card.title, "question": question.title}


# ============================================================================
# QUESTION ENDPOINTS
# ============================================================================

@router.post("/questions", response_model=schemas.QuestionSummary)
def create_question(q: schemas.QuestionCreate, db: Session = Depends(get_db)):
    """Create a new question with optional custom ID"""
    if q.id:
        existing = db.query(models.Question).filter(models.Question.id == q.id).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Question ID {q.id} already exists")

    new_q = models.Question(
        id=q.id,
        title=q.title,
        description=q.description,
        input_format=q.input_format,
        output_format=q.output_format,
        solution=q.solution,
        tags=q.tags,
        difficulty=q.difficulty,
        hints=q.hints,
        boilerplate_python=q.boilerplate_python,
        boilerplate_java=q.boilerplate_java
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)

    create_test_cases(new_q.id, q.test_cases, db)
    db.commit()
    
    return build_question_summary(new_q)


@router.get("/questions/search", response_model=List[schemas.QuestionSummary])
def search_questions(
    q: str = Query(None),
    tag: str = Query(None),
    difficulty: str = Query(None),
    db: Session = Depends(get_db)
):
    """Search and filter questions by text, tag, and difficulty"""
    query = db.query(models.Question)
    query = apply_search_filters(query, q, difficulty)
    results = query.all()
    
    # Apply tag filter if specific tag requested
    if tag:
        results = filter_by_tag(results, tag)
    
    # Include questions with matching tags if general search
    if q and not tag:
        existing_ids = {r.id for r in results}
        extra_results = find_questions_by_tag(q, existing_ids, db)
        results.extend(extra_results)
    
    return [build_question_summary(r) for r in results]

@router.get("/questions/{q_id}", response_model=schemas.QuestionDetail)
def get_question_detail(q_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific question"""
    question = db.query(models.Question).filter(models.Question.id == q_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return build_question_detail(question)

