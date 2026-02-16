"""
Simple test script to verify the FastAPI reCAPTCHA solving service.

Usage:
    python test_api.py
"""

import time
import requests

API_URL = "http://localhost:8000"


def test_api():
    """Test the /recaptcha/in and /recaptcha/res endpoints."""
    print("=" * 80)
    print("Testing FastAPI reCAPTCHA Solver")
    print("=" * 80)

    # Test 1: Submit a task
    print("\n[TEST 1] Submitting task to /recaptcha/in...")
    payload = {
        "target_url": "https://cd.captchaaiplus.com/recaptcha-v3-2.php",
        "headless": False,
    }

    try:
        response = requests.post(f"{API_URL}/recaptcha/in", json=payload)
        response.raise_for_status()
        data = response.json()
        task_id = data.get("taskId")
        print(f"✅ Task created: {task_id}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to submit task: {e}")
        return

    # Test 2: Poll for result
    print(f"\n[TEST 2] Polling /recaptcha/res for task {task_id[:8]}...")
    max_attempts = 60  # 60 attempts = 5 minutes max
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        time.sleep(5)  # Wait 5 seconds between polls

        try:
            response = requests.get(f"{API_URL}/recaptcha/res", params={"task_id": task_id})
            response.raise_for_status()
            result = response.json()

            status = result.get("status")
            print(f"  [{attempt}] Status: {status}")

            if status == "ready":
                solution = result.get("solution", {})
                print("\n✅ Task completed!")
                print(f"   Token: {solution.get('token', 'N/A')[:80]}...")
                print(f"   Score: {solution.get('score', 'N/A')}")
                print(f"   Success: {solution.get('success', 'N/A')}")
                break
            elif status == "error":
                error = result.get("errorDescription", "Unknown error")
                print(f"\n❌ Task failed: {error}")
                break
            elif status == "processing":
                continue
            else:
                print(f"\n❌ Unknown status: {status}")
                break

        except requests.exceptions.RequestException as e:
            print(f"  [{attempt}] ❌ Error polling result: {e}")
            break

    if attempt >= max_attempts:
        print(f"\n❌ Timeout: Task did not complete within {max_attempts * 5} seconds")

    print("\n" + "=" * 80)
    print("Test complete")
    print("=" * 80)


if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/")
        print(f"✅ API is running: {response.json()}")
    except requests.exceptions.RequestException:
        print(f"❌ API is not running at {API_URL}")
        print("   Start the API first with: uvicorn main:app --reload")
        exit(1)

    test_api()
