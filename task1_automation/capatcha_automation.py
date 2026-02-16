import asyncio
import json
import random
import math
import argparse
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from pathlib import Path

script_dir = Path(__file__).resolve().parent
output_dir = script_dir / "results/"
output_dir.mkdir(exist_ok=True)

TARGET_URL = "https://cd.captchaaiplus.com/recaptcha-v3-2.php"

# ===== PROXY ROTATION =====
PROXIES = [
    "http://mympdxsw-1:e26ou5bcvry9@p.webshare.io:80",
    "http://mympdxsw-2:e26ou5bcvry9@p.webshare.io:80",
    "http://mympdxsw-3:e26ou5bcvry9@p.webshare.io:80",
    "http://mympdxsw-4:e26ou5bcvry9@p.webshare.io:80",
    "http://mympdxsw-5:e26ou5bcvry9@p.webshare.io:80",
    "http://mympdxsw-6:e26ou5bcvry9@p.webshare.io:80",
    "http://mympdxsw-7:e26ou5bcvry9@p.webshare.io:80",
    "http://mympdxsw-8:e26ou5bcvry9@p.webshare.io:80",
    "http://mympdxsw-9:e26ou5bcvry9@p.webshare.io:80",
    "http://mympdxsw-10:e26ou5bcvry9@p.webshare.io:80",
]


def parse_proxy(proxy_url: str) -> dict:
    """Parse proxy URL into Playwright format."""
    parsed = urlparse(proxy_url)
    return {
        "server": f"http://{parsed.hostname}:{parsed.port}",
        "username": parsed.username,
        "password": parsed.password,
    }


async def human_like_mouse_move(page, target_x, target_y):
    """
    Move mouse in a human-like curved path using bezier curve simulation.
    """
    # Get current mouse position (start from a random point if first move)
    current_x = random.randint(100, 300)
    current_y = random.randint(100, 300)

    # Calculate distance
    distance = math.sqrt((target_x - current_x) ** 2 + (target_y - current_y) ** 2)

    # More steps for longer distances
    steps = max(20, int(distance / 10) + random.randint(5, 15))

    # Generate control points for bezier-like curve
    ctrl_x = (current_x + target_x) / 2 + random.randint(-100, 100)
    ctrl_y = (current_y + target_y) / 2 + random.randint(-50, 50)

    for i in range(steps):
        t = i / steps
        # Quadratic bezier curve
        x = (1 - t) ** 2 * current_x + 2 * (1 - t) * t * ctrl_x + t**2 * target_x
        y = (1 - t) ** 2 * current_y + 2 * (1 - t) * t * ctrl_y + t**2 * target_y

        # Add micro-jitter for realism
        x += random.uniform(-2, 2)
        y += random.uniform(-2, 2)

        await page.mouse.move(x, y)

        # Variable speed - slower at start and end
        delay = 0.01 + 0.02 * math.sin(math.pi * t)
        await asyncio.sleep(delay + random.uniform(0, 0.01))

    # Final precise move to target
    await page.mouse.move(target_x, target_y)


async def natural_scroll(page, direction="down", intensity="medium"):
    """
    Perform natural scrolling with variable speed and micro-pauses.
    """
    scroll_amounts = {"light": (50, 150), "medium": (150, 400), "heavy": (400, 800)}

    min_scroll, max_scroll = scroll_amounts.get(intensity, (150, 400))
    total_scroll = random.randint(min_scroll, max_scroll)

    # Break scroll into smaller chunks
    chunks = random.randint(3, 8)

    for _ in range(chunks):
        chunk_scroll = total_scroll // chunks + random.randint(-20, 20)

        if direction == "up":
            chunk_scroll = -chunk_scroll

        await page.mouse.wheel(0, chunk_scroll)

        # Variable delay between scroll chunks
        await asyncio.sleep(random.uniform(0.05, 0.2))

    # Pause after scrolling (reading simulation)
    await asyncio.sleep(random.uniform(0.3, 1.0))


async def realistic_delay(min_sec=0.5, max_sec=2.0, typing=False):
    """
    Generate realistic human-like delays.
    """
    if typing:
        # Typing delays are shorter and more variable
        delay = random.uniform(0.05, 0.15)
    else:
        # Use a distribution that favors middle values
        delay = random.triangular(min_sec, max_sec, (min_sec + max_sec) / 2)

    await asyncio.sleep(delay)


async def solve_with_stealth(
    target_url: str, proxy: str | None = None, headless: bool = False
) -> dict:
    """
    Solves reCAPTCHA using stealth techniques to achieve a good score.

    :param target_url: the URL to solve the captcha for
    :param proxy: the proxy URL to use (optional)
    :param headless: whether to run in headless mode
    :return: dict with token, score, and success information
    """

    if proxy:
        print(f"[+] Using Proxy: {proxy.split('@')[-1]}")

    async with Stealth().use_async(async_playwright()) as p:
        # Launch browser with stealth settings
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

        context = await browser.new_context()
        page = await context.new_page()

        # ===== STEP 1: Human-like "Warm-up" ====
        await page.goto(target_url, wait_until="networkidle")

        # Initial random mouse movement
        await human_like_mouse_move(
            page, random.randint(200, 600), random.randint(200, 400)
        )
        await realistic_delay(1, 2)

        # Natural scrolling to simulate reading
        await natural_scroll(page, "down", "light")
        await realistic_delay(0.5, 1.5)
        await natural_scroll(page, "up", "light")
        await realistic_delay(0.5, 1)

        print("[+] Warm-up complete")

        # ===== STEP 2: Trigger reCAPTCHA =====
        print("[+] Step 2: Triggering reCAPTCHA v3...")

        # Wait for the button to be available
        await page.wait_for_selector("#btn", timeout=10000)
        await realistic_delay(1, 2)

        # Human-like movement to button
        button = await page.query_selector("#btn")

        if button:
            print("[+] Found reCAPTCHA v3 test button...")

            box = await button.bounding_box()

            if box:
                # Move mouse in a curved path to button
                target_x = box["x"] + box["width"] / 2 + random.randint(-5, 5)
                target_y = box["y"] + box["height"] / 2 + random.randint(-3, 3)

                # Human-like curved mouse movement
                await human_like_mouse_move(page, target_x, target_y)
                await realistic_delay(0.3, 0.8)

                # Hover briefly before clicking (reading/hesitation)
                await realistic_delay(0.2, 0.6)

                # Click with human-like timing
                await button.click(delay=random.randint(50, 150))
                print("[+] Button clicked, waiting for reCAPTCHA v3 to execute...")

                # Wait for the output to update with natural delay
                await realistic_delay(3, 5)

        # ===== STEP 3: Extract Token and Result =====
        print("[+] Step 3: Extracting reCAPTCHA token and score...")

        # Initialize result
        result = {"score": None, "success": None, "token": None}

        try:
            # Wait for the #out element to contain the result
            await page.wait_for_function(
                """
                () => {
                    const out = document.getElementById('out');
                    return out && out.textContent.includes('score');
                }
                """,
                timeout=15000,
            )

            # Extract the full result from the output element
            result_text = await page.evaluate("""
                () => {
                    const out = document.getElementById('out');
                    return out ? out.textContent : null;
                }
            """)

            # Parse the JSON from the result
            if result_text and "{" in result_text:
                json_start = result_text.index("{")
                json_str = result_text[json_start:]
                result_json = json.loads(json_str)

                # Extract token and score from the result
                google_response = result_json.get("google_response") or result_json

                result["score"] = google_response.get("score")
                result["success"] = google_response.get("success")
                result["token"] = google_response.get("token") or result_json.get(
                    "token"
                )

                quality = (
                    "  ✅ GOOD >= 0.9"
                    if result["score"] and result["score"] >= 0.9
                    else ""
                )
                print(
                    f"Score: {result['score']}{quality} | Success: {result['success']}"
                )

        except Exception as e:
            print(f"[!] Error extracting result: {e}")

        await browser.close()

        return result


async def run_batch_tests(
    num_tests: int = 250, headless: bool = False, use_proxy: bool = True
):
    """Run multiple tests with rotating proxies and collect statistics."""
    print(f"\n{'=' * 80}")
    print(f"Starting Task 1 Assessment — {num_tests} runs")
    if use_proxy:
        print(f"Using {len(PROXIES)} rotating proxies")
    else:
        print("Running without proxies")
    print(f"{'=' * 80}\n")

    results = []
    high_count = 0
    start_time = datetime.now()

    for i in range(num_tests):
        proxy = PROXIES[i % len(PROXIES)] if use_proxy else None
        if proxy:
            proxy_ip = proxy.split("@")[-1]
            print(f"\n[{i + 1:3d}/{num_tests}] proxy {proxy_ip}")
        else:
            print(f"\n[{i + 1:3d}/{num_tests}] no proxy")

        try:
            res = await solve_with_stealth(TARGET_URL, proxy=proxy, headless=headless)
            results.append(res)

            if res["score"] is not None and res["score"] >= 0.9:
                high_count += 1
        except Exception as e:
            print(f"[!] Test failed: {type(e).__name__}: {e}")
            results.append({"score": None, "success": None, "token": None})

        # Delay between runs to avoid rate limiting
        if i < num_tests - 1:
            delay = random.uniform(6, 14)
            print(f"[+] Waiting {delay:.1f}s before next run...")
            await asyncio.sleep(delay)

    # Calculate statistics
    elapsed = (datetime.now() - start_time).total_seconds() / 60
    total = sum(1 for r in results if r["score"] is not None)
    perc_high = (high_count / total * 100) if total else 0

    # Calculate score distribution
    scores = [r["score"] for r in results if r["score"] is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    print(f"\n{'=' * 80}")
    print("TASK 1 COMPLETE")
    print(f"{'=' * 80}")
    print(
        f"Runs: {num_tests} | Successful extractions: {total} | Time: {elapsed:.1f} min"
    )
    print(f"Average Score: {avg_score:.3f}")
    print(f"Scores ≥ 0.9: {high_count}/{total} → {perc_high:.2f}%")

    if perc_high >= 15:
        print("\n✅ PASSED: at least 15% scores >= 0.9")
    else:
        print("\n❌ Failed: need >= 15% with score >= 0.9")

    # Save full results
    results_file = output_dir / "recaptcha_v3_full_results.txt"
    with open(results_file, "w", encoding="utf-8") as f:
        f.write(f"# Task 1 Assessment — {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write(f"# {total} successful runs, {high_count} ≥0.9 ({perc_high:.2f}%)\n")
        f.write(f"# Average score: {avg_score:.3f}\n\n")
        for idx, r in enumerate(results, 1):
            if r["score"] is not None:
                token_short = str(r["token"])[:80] + "..." if r["token"] else "—"
                f.write(
                    f"[{idx:3d}] Score: {r['score']:.3f} | Success: {r['success']} | Token: {token_short}\n"
                )
            else:
                f.write(f"[{idx:3d}] FAILED\n")

    # Save JSON results
    json_file = output_dir / "recaptcha_v3_results.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "total_runs": num_tests,
                "successful_extractions": total,
                "high_scores": high_count,
                "percentage_high": perc_high,
                "average_score": avg_score,
                "requirement_met": perc_high >= 15,
                "elapsed_minutes": elapsed,
                "results": results,
            },
            f,
            indent=2,
        )

    print("\nResults saved to:")
    print(f"  - {results_file}")
    print(f"  - {json_file}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stealth reCAPTCHA v3 Assessment")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument(
        "--tests-no", type=int, default=1, help="Number of tests to run (default: 1)"
    )
    parser.add_argument("--no-proxy", action="store_true", help="Run without proxies")
    args = parser.parse_args()

    if args.tests_no == 1:
        # Single test mode
        asyncio.run(
            solve_with_stealth(
                TARGET_URL,
                proxy=PROXIES[random.randint(0, len(PROXIES) - 1)]
                if not args.no_proxy
                else None,
                headless=args.headless,
            )
        )
    else:
        # Batch test mode
        asyncio.run(
            run_batch_tests(
                num_tests=args.tests_no,
                headless=args.headless,
                use_proxy=not args.no_proxy,
            )
        )
