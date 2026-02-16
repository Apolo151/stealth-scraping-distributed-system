"""
FastAPI service for solving reCAPTCHA v3 challenges.

Endpoints:
- POST /recaptcha/in: Submit a reCAPTCHA solving task
- GET /recaptcha/res: Retrieve the result of a task
"""

import asyncio
import sqlite3
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# Import the solve_with_stealth function from task1
sys.path.append(str(Path(__file__).resolve().parent.parent))
from task1_automation.captcha_automation import solve_with_stealth, PROXIES

# ===== CONFIGURATION =====
MAX_CONCURRENT_TASKS = 10
DB_PATH = Path(__file__).resolve().parent / "tasks.db"
TASK_TTL_MINUTES = 30  # Clean up tasks older than 30 minutes

# ===== GLOBAL STATE =====
semaphore: asyncio.Semaphore
proxy_index = 0


# ===== DATABASE SETUP =====
def init_db():
    """Initialize SQLite database for task storage."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            target_url TEXT NOT NULL,
            proxy TEXT,
            headless INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            token TEXT,
            score REAL,
            success INTEGER,
            error TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_next_proxy() -> str:
    """Get the next proxy in round-robin fashion."""
    global proxy_index
    proxy = PROXIES[proxy_index % len(PROXIES)]
    proxy_index += 1
    return proxy


def save_task(
    task_id: str,
    status: str,
    target_url: str,
    proxy: Optional[str],
    headless: bool,
    token: Optional[str] = None,
    score: Optional[float] = None,
    success: Optional[bool] = None,
    error: Optional[str] = None,
):
    """Save or update a task in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT task_id FROM tasks WHERE task_id = ?", (task_id,))
    exists = cursor.fetchone()

    if exists:
        # Update existing task
        cursor.execute(
            """
            UPDATE tasks
            SET status = ?, completed_at = ?, token = ?, score = ?, success = ?, error = ?
            WHERE task_id = ?
            """,
            (
                status,
                datetime.now().isoformat() if status != "processing" else None,
                token,
                score,
                1 if success else 0 if success is not None else None,
                error,
                task_id,
            ),
        )
    else:
        # Insert new task
        cursor.execute(
            """
            INSERT INTO tasks (task_id, status, target_url, proxy, headless, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                status,
                target_url,
                proxy,
                1 if headless else 0,
                datetime.now().isoformat(),
            ),
        )

    conn.commit()
    conn.close()


def get_task(task_id: str) -> Optional[dict]:
    """Retrieve a task from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "task_id": row[0],
        "status": row[1],
        "target_url": row[2],
        "proxy": row[3],
        "headless": bool(row[4]),
        "created_at": row[5],
        "completed_at": row[6],
        "token": row[7],
        "score": row[8],
        "success": bool(row[9]) if row[9] is not None else None,
        "error": row[10],
    }


def cleanup_old_tasks():
    """Remove tasks older than TASK_TTL_MINUTES."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cutoff = (datetime.now() - timedelta(minutes=TASK_TTL_MINUTES)).isoformat()
    cursor.execute("DELETE FROM tasks WHERE created_at < ?", (cutoff,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    if deleted > 0:
        print(f"[Cleanup] Removed {deleted} old tasks")


# ===== BACKGROUND TASK HANDLER =====
async def process_task(task_id: str, target_url: str, proxy: str, headless: bool):
    """
    Background task that solves the reCAPTCHA and updates the database.
    """
    async with semaphore:  # Limit concurrent tasks
        print(f"[Task {task_id[:8]}] Starting solve for {target_url}")
        try:
            result = await solve_with_stealth(
                target_url=target_url, proxy=proxy, headless=headless
            )

            # Check if solving was successful
            if result.get("token"):
                save_task(
                    task_id=task_id,
                    status="ready",
                    target_url=target_url,
                    proxy=proxy,
                    headless=headless,
                    token=result.get("token"),
                    score=result.get("score"),
                    success=result.get("success"),
                )
                print(
                    f"[Task {task_id[:8]}] Completed successfully (score: {result.get('score')})"
                )
            else:
                save_task(
                    task_id=task_id,
                    status="error",
                    target_url=target_url,
                    proxy=proxy,
                    headless=headless,
                    error="Failed to extract reCAPTCHA token",
                )
                print(f"[Task {task_id[:8]}] Failed: No token extracted")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            save_task(
                task_id=task_id,
                status="error",
                target_url=target_url,
                proxy=proxy,
                headless=headless,
                error=error_msg,
            )
            print(f"[Task {task_id[:8]}] Error: {error_msg}")


# ===== LIFECYCLE MANAGEMENT =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and cleanup on shutdown."""
    global semaphore

    # Startup
    print("🚀 Starting FastAPI reCAPTCHA Solver Service")
    init_db()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    print(f"✅ Database initialized at {DB_PATH}")
    print(f"✅ Concurrent task limit: {MAX_CONCURRENT_TASKS}")
    print(f"✅ Available proxies: {len(PROXIES)}")

    yield

    # Shutdown
    print("🔴 Shutting down service")


# ===== FASTAPI APP =====
app = FastAPI(
    title="reCAPTCHA v3 Solver API",
    description="Asynchronous reCAPTCHA v3 solving service with task queue",
    version="1.0.0",
    lifespan=lifespan,
)


# ===== REQUEST/RESPONSE MODELS =====
class RecaptchaRequest(BaseModel):
    target_url: str = Field(
        ..., description="The URL where reCAPTCHA needs to be solved"
    )
    proxy: Optional[str] = Field(
        None,
        description="Proxy URL (format: http://user:pass@host:port). If not provided, auto-rotates proxies.",
    )
    headless: bool = Field(
        True, description="Run browser in headless mode (default: True)"
    )


class TaskResponse(BaseModel):
    taskId: str = Field(..., description="Unique task identifier")


class TaskStatusResponse(BaseModel):
    status: str = Field(..., description="Task status: processing, ready, or error")
    solution: Optional[dict] = Field(None, description="Solution data when ready")
    errorDescription: Optional[str] = Field(
        None, description="Error message if status is error"
    )


# ===== ENDPOINTS =====
@app.get("/")
async def root():
    """Health check endpoint."""
    cleanup_old_tasks()  # Clean up on health check
    return {
        "service": "reCAPTCHA v3 Solver API",
        "status": "online",
        "endpoints": {
            "submit_task": "POST /recaptcha/in",
            "get_result": "GET /recaptcha/res?task_id=<taskId>",
        },
    }


@app.post("/recaptcha/in", response_model=TaskResponse)
async def submit_task(request: RecaptchaRequest):
    """
    Submit a new reCAPTCHA solving task.

    Returns a taskId immediately and starts solving in the background.
    """
    # Generate unique task ID
    task_id = str(uuid.uuid4())

    # Use provided proxy or auto-rotate
    proxy = request.proxy if request.proxy else get_next_proxy()

    # Save task as "processing"
    save_task(
        task_id=task_id,
        status="processing",
        target_url=request.target_url,
        proxy=proxy,
        headless=request.headless,
    )

    # Start background task
    asyncio.create_task(
        process_task(
            task_id=task_id,
            target_url=request.target_url,
            proxy=proxy,
            headless=request.headless,
        )
    )

    print(f"[Task {task_id[:8]}] Created and queued")

    return TaskResponse(taskId=task_id)


@app.get("/recaptcha/res", response_model=TaskStatusResponse)
async def get_result(task_id: str = Query(..., description="Task ID to query")):
    """
    Get the result of a reCAPTCHA solving task.

    Returns:
    - processing: Task is still being processed
    - ready: Task completed successfully with solution
    - error: Task failed with error description
    """
    task = get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] == "processing":
        return TaskStatusResponse(status="processing", solution=None, errorDescription=None)

    elif task["status"] == "ready":
        return TaskStatusResponse(
            status="ready",
            solution={
                "token": task["token"],
                "score": task["score"],
                "success": task["success"],
            },
            errorDescription=None,
        )

    elif task["status"] == "error":
        return TaskStatusResponse(
            status="error",
            solution=None,
            errorDescription=task["error"] or "Unknown error"
        )

    else:
        raise HTTPException(status_code=500, detail="Invalid task status")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
