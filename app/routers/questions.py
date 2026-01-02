from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.get("/cards", response_model=list[schemas.CardResponse])
def get_cards(db: Session = Depends(get_db)):
    cards = db.query(models.Card).all()
    return cards

@router.get("/{q_id}")
def get_question(q_id: int, db: Session = Depends(get_db)):
    q = db.query(models.Question).filter(models.Question.id == q_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Return only public test cases for the UI
    examples = [{"input": t.input_data, "output": t.expected_output} 
                for t in q.test_cases if t.is_public]

    return {
        "id": q.id,
        "title": q.title,
        "description": q.description,
        "hints": q.hints,
        "boilerplate": {
            "python": q.boilerplate_python,
            "java": q.boilerplate_java
        },
        "examples": examples
    }