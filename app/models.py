from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Boolean, JSON
from sqlalchemy.orm import relationship
from database import Base

card_questions = Table(
    "card_questions",
    Base.metadata,
    Column("card_id", Integer, ForeignKey("cards.id"), primary_key=True),
    Column("question_id", Integer, ForeignKey("questions.id"), primary_key=True),
)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(Text)
    input_format = Column(Text)
    output_format = Column(Text)
    solution = Column(Text)
    tags = Column(JSON)
    difficulty = Column(String, default="Medium")
    hints = Column(JSON)      
    boilerplate_python = Column(Text)
    boilerplate_java = Column(Text)
    
    test_cases = relationship("TestCase", back_populates="question")
    # Corrected Relationship:
    cards = relationship("Card", secondary=card_questions, back_populates="questions")

class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    input_data = Column(Text)
    expected_output = Column(Text)
    is_public = Column(Boolean, default=False)
    
    question = relationship("Question", back_populates="test_cases")

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    description = Column(String)
    # Corrected Relationship:
    questions = relationship("Question", secondary=card_questions, back_populates="cards")