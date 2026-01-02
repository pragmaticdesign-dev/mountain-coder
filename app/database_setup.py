import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, DATABASE_URL
import models

def init_db():
    os.makedirs("./data", exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Always create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    if not os.path.exists("./data/mountain.db_seeded"):
        print("🌱 Seeding Data...")
        #seed_data(sessionmaker(bind=engine)())
        # Create a flag file so we don't re-seed every restart
        with open("./data/mountain.db_seeded", "w") as f: f.write("done")
        print("✅ Data Seeded!")
    else:
        print("⚡ Database ready.")

def seed_data(db):
    # 1. Card
    card = models.Card(title="Top 100", description="Must Do Interview Questions")
    db.add(card)
    db.commit()

    # 2. Question: Two Sum
    py_code = """import sys
def solve():
    input_data = sys.stdin.read().split()
    if not input_data: return
    iterator = iter(input_data)
    try:
        n = int(next(iterator))
        nums = [int(next(iterator)) for _ in range(n)]
        target = int(next(iterator))
    except StopIteration: return
    # Write logic here
    print("0 1")
if __name__ == '__main__': solve()"""

    java_code = """import java.util.*;
public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if(!sc.hasNext()) return;
        int n = sc.nextInt();
        int[] nums = new int[n];
        for(int i=0; i<n; i++) nums[i] = sc.nextInt();
        int target = sc.nextInt();
        // Write logic here
        System.out.println("0 1");
    }
}"""

    solution_text = """### Approach
We can solve this problem efficiently by using a **Hash Map**.

1. Create an empty map to store `{value: index}`.
2. Iterate through the array.
3. For each number `x`, calculate `complement = target - x`.
4. If `complement` is already in the map, we found the pair! Return their indices.
5. Otherwise, add `x` and its index to the map.

**Time Complexity:** O(N)  
**Space Complexity:** O(N)
"""

    q1 = models.Question(
        title="Example 1",
        description="Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        input_format="N, Array elements, Target",
        output_format="Indices separated by space",
        solution=solution_text,
        tags=["Array", "Hash Table"],
        difficulty="Easy",
        hints=["Use a HashMap to store differences."],
        boilerplate_python=py_code,
        boilerplate_java=java_code
    )
    db.add(q1)
    db.commit()

    # 3. Test Cases
    tc1 = models.TestCase(question_id=q1.id, input_data="4\n2 7 11 15\n9", expected_output="0 1", is_public=True)
    db.add(tc1)
    
    q1.cards.append(card)
    db.commit()
    db.close()