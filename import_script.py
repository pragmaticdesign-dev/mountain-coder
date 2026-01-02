import requests
import json
import os
import glob

API_URL = "http://localhost:8000"

def import_data():
    if not os.path.exists("import_data"):
        print("❌ Error: 'import_data' folder not found!")
        return

    # Store ALL question IDs encountered to link them to the "ALL" card later
    all_question_ids = []

    # ---------------------------------------------------------
    # PART 1: Import Questions from ALL 'question*.json' files
    # ---------------------------------------------------------
    print("🚀 Importing Questions...")
    
    # Find all files matching import_data/question*.json
    question_files = glob.glob(os.path.join("import_data", "question*.json"))
    
    if not question_files:
        print("   ⚠️ No question files found (expected prefix 'question')")
    
    for filepath in question_files:
        print(f"\n📄 Processing File: {filepath}")
        try:
            with open(filepath, "r") as f:
                questions = json.load(f)
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            continue

        for q in questions:
            q_id = q.get('id')
            print(f"   -> Uploading #{q_id} {q['title']}...", end=" ")
            
            try:
                res = requests.post(f"{API_URL}/questions", json=q)
                
                if res.status_code == 200:
                    print("✅ Success")
                    all_question_ids.append(q_id)
                elif res.status_code == 400:
                    print("⚠️  Exists (Skipping but adding to list)")
                    all_question_ids.append(q_id)
                else:
                    print(f"❌ Failed: {res.text}")
            except Exception as e:
                print(f"❌ Connection Error: {e}")

    # ---------------------------------------------------------
    # PART 2: Import Specific Cards (from cards.json)
    # ---------------------------------------------------------
    print("\n🚀 Importing Specific Cards...")
    cards_path = os.path.join("import_data", "cards.json")
    
    if os.path.exists(cards_path):
        with open(cards_path, "r") as f:
            cards = json.load(f)

        for c in cards:
            create_and_link_card(c["title"], c["description"], c.get("question_ids", []))
    else:
        print("   ⚠️ No cards.json found, skipping specific cards.")

    # ---------------------------------------------------------
    # PART 3: Create the "ALL" Card
    # ---------------------------------------------------------
    print("\n🚀 Creating 'ALL Problems' Card...")
    if all_question_ids:
        # Remove duplicates just in case
        unique_ids = list(set(all_question_ids))
        create_and_link_card(
            title="ALL Problems", 
            description="A complete list of every question in the database.", 
            question_ids=unique_ids
        )
    else:
        print("   ⚠️ No questions found, skipping 'ALL' card.")

    print("\n✨ Import Complete!")

def create_and_link_card(title, description, question_ids):
    """Helper function to create a card and link questions to it"""
    print(f"   -> Creating Card '{title}'...", end=" ")
    
    try:
        # 1. Create Card
        payload = {"title": title, "description": description}
        res = requests.post(f"{API_URL}/cards", json=payload)
        
        # If card exists (unique constraint), we might fail or get 400. 
        # Ideally, your API handles this, or we catch it. 
        # Assuming API returns the ID even if it exists or we handle the error:
        
        if res.status_code == 200:
            card_data = res.json()
            card_id = card_data["id"]
            print(f"✅ (ID: {card_id}) Linking {len(question_ids)} questions...", end=" ")
            
            # 2. Link Questions
            success_count = 0
            for qid in question_ids:
                link_res = requests.post(f"{API_URL}/cards/{card_id}/add_question/{qid}")
                if link_res.status_code == 200:
                    success_count += 1
            print(f"Done ({success_count}/{len(question_ids)} linked)")
            
        else:
            # If 400 (likely title exists), we skip linking for simplicity 
            # or you'd need to fetch the existing ID first.
            print(f"⚠️  Skipping (Likely exists or Error: {res.status_code})")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import_data()