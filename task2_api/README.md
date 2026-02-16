# reCAPTCHA v3 Solver API

FastAPI-based asynchronous service for solving reCAPTCHA v3 challenges using stealth techniques.

## Features

- ⚡ **Asynchronous Processing** — Submit tasks and poll for results
- 🔄 **Automatic Proxy Rotation** — Round-robin through 10 proxies
- 🔒 **Concurrent Task Limiting** — Max 10 simultaneous browser instances
- 💾 **SQLite Persistence** — Task state survives restarts
- 🎯 **High Success Rate** — Stealth techniques for good reCAPTCHA scores

## Installation

```bash
# Install dependencies
pip install -r ../requirements.txt

# Install Playwright browser (if not already installed)
playwright install chromium
```

## Running the API

```bash
# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST `/recaptcha/in`

Submit a new reCAPTCHA solving task.

**Request Body:**
```json
{
  "target_url": "https://example.com/recaptcha-page",
  "proxy": "http://user:pass@host:port",  // Optional, auto-rotates if not provided
  "headless": true  // Optional, default: true
}
```

**Response:**
```json
{
  "taskId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/recaptcha/in" \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://cd.captchaaiplus.com/recaptcha-v3-2.php",
    "headless": true
  }'
```

### GET `/recaptcha/res`

Retrieve the result of a task.

**Query Parameters:**
- `task_id` (required) — The task ID returned from `/recaptcha/in`

**Response (Processing):**
```json
{
  "status": "processing"
}
```

**Response (Ready):**
```json
{
  "status": "ready",
  "solution": {
    "token": "03AGdBq27...",
    "score": 0.9,
    "success": true
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "errorDescription": "Failed to extract reCAPTCHA token"
}
```

**Example:**
```bash
curl "http://localhost:8000/recaptcha/res?task_id=550e8400-e29b-41d4-a716-446655440000"
```

## Testing

```bash
# Run the test script
python test_api.py
```

The test script will:
1. Submit a task
2. Poll for completion
3. Display the result

## Configuration

Edit `main.py` to adjust:

```python
MAX_CONCURRENT_TASKS = 10  # Maximum simultaneous browser instances
TASK_TTL_MINUTES = 30      # Auto-cleanup old tasks after 30 minutes
```

## Database

Task data is stored in `tasks.db` (SQLite). The database includes:
- Task ID and status
- Target URL and proxy used
- Timestamps (created/completed)
- Results (token, score, success flag)
- Error messages (if failed)

## Architecture

```
Client Request → /recaptcha/in → Generate TaskID → Background Task
                                       ↓
                                  Queue
                                       ↓
                                  solve_with_stealth()
                                       ↓
                                  SQLite Database
                                       ↑
Client Poll ← /recaptcha/res ← Read Status/Result
```

## Notes

- Tasks are processed asynchronously in the background
- Solving typically takes 10-15 seconds per task
- Old tasks are automatically cleaned up after 30 minutes
- The service uses stealth techniques from `task1_automation/capatcha_automation.py`
- Proxies are rotated automatically if not specified in the request

## Interactive Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
