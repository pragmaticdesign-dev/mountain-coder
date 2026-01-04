import subprocess
import time
import os
import tempfile
import shutil
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Tuple, List, Dict, Any, Optional
import models, schemas
from database import get_db

router = APIRouter(tags=["Submit"])

# ============================================================================
# CONSTANTS & CONFIG
# ============================================================================

EXECUTION_TIMEOUT = 2
COMPILATION_TIMEOUT = 60  # Reduced: we only compile once now
DEFAULT_NO_OUTPUT_MESSAGE = "[Process finished with no output. Did you forget input?]"
MAX_WORKERS = 2

LANGUAGE_CONFIGS = {
    "python": {
        "extension": ".py",
        "requires_compile": False,
        "run_cmd": ["python3", "{file}"]
    },
    "java": {
        "extension": ".java",
        "class_name": "Solution",
        "requires_compile": True,
        # REMOVED: -J-Xms256m -J-Xmx512m (Let JVM handle memory defaults for compilation)
      "compile_cmd": ["javac", "-J-Xshare:on", "-J-XX:TieredStopAtLevel=1", "{file}"],
      "run_cmd": ["java", "-Xshare:on", "-Xmx256m", "-cp", "{dir}", "Solution"]
    }
}

# ============================================================================
# CORE EXECUTION ENGINE (Refactored)
# ============================================================================

def create_workspace_and_compile(language: str, code: str) -> Tuple[Optional[Path], str, Optional[List[str]]]:
    """
    1. Creates workspace
    2. Writes code to file
    3. Compiles (if needed)
    Returns: (workspace_path, error_message, run_command_template)
    """
    if language not in LANGUAGE_CONFIGS:
        return None, f"Unsupported language: {language}", None

    config = LANGUAGE_CONFIGS[language]
    workspace_id = str(uuid.uuid4())
    workspace = Path(tempfile.gettempdir()) / f"code_exec_{workspace_id}"
    workspace.mkdir(exist_ok=True)

    try:
        # 1. Determine filename and write code
        filename = f"{config.get('class_name', f'code_{workspace_id}')}{config['extension']}"
        file_path = workspace / filename
        file_path.write_text(code, encoding='utf-8')

        # 2. Compile if required
        if config["requires_compile"]:
            cmd = [arg.format(file=str(file_path), dir=str(workspace)) for arg in config["compile_cmd"]]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=COMPILATION_TIMEOUT, cwd=workspace
            )
            if result.returncode != 0:
                return workspace, f"Compilation Error:\n{result.stderr}", None

        # 3. Prepare run command
        # We format 'file' and 'dir' now so we don't do it per test case
        run_cmd_template = [arg.format(file=str(file_path), dir=str(workspace)) for arg in config["run_cmd"]]
        return workspace, "", run_cmd_template

    except subprocess.TimeoutExpired:
        return workspace, "Compilation Timeout", None
    except Exception as e:
        return workspace, f"System Error: {str(e)}", None

def run_test_case_in_workspace(
    run_cmd: List[str], 
    input_data: str, 
    workspace: Path
) -> Tuple[str, str, float]:
    """Executes a single test run in an existing workspace."""
    start_time = time.time()
    try:
        proc = subprocess.run(
            run_cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT,
            cwd=workspace
        )
        runtime = (time.time() - start_time) * 1000
        error = proc.stderr if proc.returncode != 0 else ""
        return proc.stdout, error, runtime
    except subprocess.TimeoutExpired:
        return "", f"Time Limit Exceeded ({EXECUTION_TIMEOUT}s)", (time.time() - start_time) * 1000
    except Exception as e:
        return "", str(e), 0.0

def cleanup_workspace(workspace: Path):
    try:
        if workspace and workspace.exists():
            shutil.rmtree(workspace)
    except Exception:
        pass

# ============================================================================
# API HANDLERS
# ============================================================================

@router.post("/submit", response_model=schemas.SubmitResponse)
def submit_solution(sub: schemas.SubmitRequest, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == sub.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if not question.test_cases:
        return {"status": "Error", "details": [{"actual": "No test cases found"}]}

    # 1. SETUP: Create Workspace & Compile ONCE
    workspace, error, run_cmd = create_workspace_and_compile(sub.language, sub.code)
    
    # Handle Compilation/Setup Errors immediately
    if error:
        cleanup_workspace(workspace)
        return {
            "status": "Compilation Error",
            "total_passed": 0,
            "total_tests": 0,
            "runtime": 0.0,
            "details": [{"status": "Fail", "actual": error, "expected": ""}]
        }

    results = []
    total_runtime = 0.0
    all_passed = True

    try:
        # 2. EXECUTE: Loop through test cases using the SAME workspace/binary
        for idx, test in enumerate(question.test_cases):
            actual, err, runtime = run_test_case_in_workspace(run_cmd, test.input_data, workspace)
            
            # Normalize and Compare
            actual_clean = actual.strip()
            expected_clean = test.expected_output.strip() if test.expected_output else ""
            
            # Note: If stderr exists, it's a Runtime Error (Fail)
            passed = (not err) and (actual_clean == expected_clean)
            
            total_runtime += runtime
            results.append({
                "test_case": idx + 1,
                "status": "Pass" if passed else "Fail",
                "expected": expected_clean,
                "actual": err if err else actual_clean,
                "runtime_ms": round(runtime, 2)
            })

            if not passed:
                all_passed = False
                break  # Fail fast
                
    finally:
        # 3. TEARDOWN: Clean up after all tests are done
        cleanup_workspace(workspace)

    return {
        "status": "Accepted" if all_passed else "Wrong Answer",
        "total_passed": sum(1 for r in results if r["status"] == "Pass"),
        "total_tests": len(question.test_cases),
        "runtime": round(total_runtime, 2),
        "details": results
    }

@router.post("/submit/run")
def run_custom_code(req: schemas.RunRequest):
    """Refactored to use the same efficient flow"""
    workspace, error, run_cmd = create_workspace_and_compile(req.language, req.code)
    
    if error:
        cleanup_workspace(workspace)
        return {"output": error, "is_error": True}

    try:
        actual, err, _ = run_test_case_in_workspace(run_cmd, req.input_data, workspace)
        output = err if err else actual
        if not output: output = DEFAULT_NO_OUTPUT_MESSAGE
        return {"output": output, "is_error": bool(err)}
    finally:
        cleanup_workspace(workspace)