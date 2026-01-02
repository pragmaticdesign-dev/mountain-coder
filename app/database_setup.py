import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, DATABASE_URL
import models

def init_db():
    os.makedirs("./data", exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    if not os.path.exists("./data/mountain.db"):
        print("⚡ Creating Database...")
        Base.metadata.create_all(bind=engine)
        seed_data(sessionmaker(bind=engine)())
        print("🌱 Data Seeded!")

def seed_data(db):
    # 1. Card
    card = models.Card(title="Top 100", description="Must Do Questions")
    db.add(card)
    db.commit()

    # 2. Question
    q1 = models.Question(
        title="Two Sum",
        description="Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        hints=["Use a HashMap to store complements", "Time complexity should be O(N)"],
        boilerplate_python="import sys\n\ndef solve():\n    # Read input from stdin\n    lines = sys.stdin.read().split()\n    # Write logic here\n    pass\n\nif __name__ == '__main__':\n    solve()",
        boilerplate_java="import java.util.*;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Write logic here\n    }\n}"
    )
    db.add(q1)
    db.commit()

    # 3. Test Cases
    tc1 = models.TestCase(question_id=q1.id, input_data="4\n2 7 11 15\n9", expected_output="0 1", is_public=True)
    db.add(tc1)
    
    q1.cards.append(card)
    db.commit()
    db.close()