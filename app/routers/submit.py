import subprocess
import time
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(tags=["Submit"])

@router.post("/submit", response_model=schemas.SubmitResponse)
def submit_solution(sub: schemas.SubmitRequest, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == sub.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    test_cases = question.test_cases
    results = []
    all_passed = True
    total_runtime = 0

    for idx, test in enumerate(test_cases):
        start = time.time()
        actual, error = run_code_docker(sub.language, sub.code, test.input_data)
        runtime = (time.time() - start) * 1000 
        total_runtime += runtime

        passed = False
        if not error and actual.strip() == test.expected_output.strip():
            passed = True
        else:
            all_passed = False
        
        results.append({
            "test_case": idx + 1,
            "status": "Pass" if passed else "Fail",
            "expected": test.expected_output,
            "actual": actual if not error else error,
            "runtime_ms": round(runtime, 2)
        })
        
        if not passed: break # Fail fast

    return {
        "status": "Accepted" if all_passed else "Wrong Answer",
        "total_passed": len([r for r in results if r['status'] == "Pass"]),
        "total_tests": len(test_cases),
        "runtime": round(total_runtime, 2),
        "details": results
    }

def run_code_docker(language, code, input_str):
    try:
        if language == "python":
            with open("temp.py", "w") as f: f.write(code)
            proc = subprocess.run(["python3", "temp.py"], input=input_str, text=True, capture_output=True, timeout=2)
            return proc.stdout, proc.stderr

        elif language == "java":
            with open("Solution.java", "w") as f: f.write(code)
            c_proc = subprocess.run(["javac", "Solution.java"], capture_output=True, text=True)
            if c_proc.returncode != 0: return "", "Compilation Error:\n" + c_proc.stderr
            proc = subprocess.run(["java", "Solution"], input=input_str, text=True, capture_output=True, timeout=2)
            return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return "", "Time Limit Exceeded"
    except Exception as e:
        return "", str(e)
    return "", "Unknown Error"