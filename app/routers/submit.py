import subprocess
import time
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Tuple, List, Dict, Any
import models, schemas
from database import get_db

router = APIRouter(tags=["Submit"])


# ============================================================================
# CONSTANTS
# ============================================================================

EXECUTION_TIMEOUT = 2  # seconds
DEFAULT_NO_OUTPUT_MESSAGE = "[Process finished with no output. Did you forget input?]"

LANGUAGE_CONFIGS = {
    "python": {
        "file": "temp.py",
        "compile": None,
        "run": ["python3", "temp.py"]
    },
    "java": {
        "file": "Solution.java",
        "compile": ["javac", "Solution.java"],
        "run": ["java", "Solution"]
    }
}


# ============================================================================
# HELPER FUNCTIONS - Code Execution
# ============================================================================

def write_code_to_file(filename: str, code: str):
    """Write code to a temporary file"""
    with open(filename, "w") as f:
        f.write(code)


def compile_code(compile_cmd: List[str]) -> Tuple[bool, str]:
    """Compile code and return success status and error message"""
    proc = subprocess.run(compile_cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, f"Compilation Error:\n{proc.stderr}"
    return True, ""


def execute_code(run_cmd: List[str], input_data: str) -> Tuple[str, str]:
    """Execute code with input and return output and error"""
    try:
        proc = subprocess.run(
            run_cmd,
            input=input_data,
            text=True,
            capture_output=True,
            timeout=EXECUTION_TIMEOUT
        )
        return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return "", "Time Limit Exceeded"
    except Exception as e:
        return "", str(e)


def run_code_docker(language: str, code: str, input_str: str) -> Tuple[str, str]:
    """
    Execute code in specified language with given input.
    Returns (stdout, stderr) tuple.
    NOTE: Currently runs on local machine, not Docker.
    """
    if language not in LANGUAGE_CONFIGS:
        return "", f"Unsupported language: {language}"
    
    config = LANGUAGE_CONFIGS[language]
    
    try:
        # Write code to file
        write_code_to_file(config["file"], code)
        
        # Compile if needed
        if config["compile"]:
            success, error = compile_code(config["compile"])
            if not success:
                return "", error
        
        # Execute code
        return execute_code(config["run"], input_str)
    
    except Exception as e:
        return "", str(e)


# ============================================================================
# HELPER FUNCTIONS - Test Case Processing
# ============================================================================

def normalize_output(output: str) -> str:
    """Normalize output by stripping whitespace"""
    return output.strip() if output else ""


def compare_outputs(actual: str, expected: str) -> bool:
    """Compare actual and expected outputs after normalization"""
    return normalize_output(actual) == normalize_output(expected)


def run_single_test_case(
    test_case: models.TestCase,
    language: str,
    code: str,
    index: int
) -> Dict[str, Any]:
    """Run a single test case and return result details"""
    start_time = time.time()
    actual_output, error = run_code_docker(language, code, test_case.input_data)
    runtime_ms = (time.time() - start_time) * 1000
    
    passed = not error and compare_outputs(actual_output, test_case.expected_output)
    
    return {
        "test_case": index + 1,
        "status": "Pass" if passed else "Fail",
        "expected": test_case.expected_output,
        "actual": actual_output if not error else error,
        "runtime_ms": round(runtime_ms, 2),
        "passed": passed
    }


def run_all_test_cases(
    test_cases: List[models.TestCase],
    language: str,
    code: str,
    fail_fast: bool = True
) -> Tuple[List[Dict], float]:
    """
    Run all test cases and return results with total runtime.
    If fail_fast is True, stops at first failure.
    """
    results = []
    total_runtime = 0.0
    
    for idx, test in enumerate(test_cases):
        result = run_single_test_case(test, language, code, idx)
        total_runtime += result["runtime_ms"]
        results.append(result)
        
        # Fail fast optimization
        if fail_fast and not result["passed"]:
            break
    
    return results, total_runtime


def build_submit_response(
    results: List[Dict],
    total_tests: int,
    total_runtime: float
) -> Dict[str, Any]:
    """Build submission response from test results"""
    passed_count = sum(1 for r in results if r["status"] == "Pass")
    all_passed = passed_count == total_tests and len(results) == total_tests
    
    # Remove 'passed' field from results (internal use only)
    clean_results = [
        {k: v for k, v in r.items() if k != "passed"}
        for r in results
    ]
    
    return {
        "status": "Accepted" if all_passed else "Wrong Answer",
        "total_passed": passed_count,
        "total_tests": total_tests,
        "runtime": round(total_runtime, 2),
        "details": clean_results
    }


def build_error_response(message: str) -> Dict[str, Any]:
    """Build error response for submission"""
    return {
        "status": "Error",
        "total_passed": 0,
        "total_tests": 0,
        "runtime": 0.0,
        "details": [{
            "status": "Fail",
            "actual": message,
            "expected": ""
        }]
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/submit/run")
def run_custom_code(req: schemas.RunRequest):
    """Run custom code with user-provided input (no test cases)"""
    actual_output, error = run_code_docker(req.language, req.code, req.input_data)
    
    # Provide helpful message if no output generated
    if not error and not actual_output:
        actual_output = DEFAULT_NO_OUTPUT_MESSAGE
    
    return {
        "output": actual_output if not error else error,
        "is_error": bool(error)
    }


@router.post("/submit", response_model=schemas.SubmitResponse)
def submit_solution(sub: schemas.SubmitRequest, db: Session = Depends(get_db)):
    """Submit solution and run against all test cases"""
    # Fetch question
    question = db.query(models.Question).filter(
        models.Question.id == sub.question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Validate test cases exist
    if not question.test_cases:
        return build_error_response("No test cases found")
    
    # Run all test cases
    results, total_runtime = run_all_test_cases(
        question.test_cases,
        sub.language,
        sub.code,
        fail_fast=True
    )
    
    # Build and return response
    return build_submit_response(results, len(question.test_cases), total_runtime)