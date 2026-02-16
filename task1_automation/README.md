# Task 1: Stealth reCAPTCHA Solver

This module implements a stealthy, human-like browser automation system to solve reCAPTCHA v3 challenges and achieve high scores.

## Features
- Human-like mouse movement, scrolling, and delays
- Proxy rotation for network reputation management
- User agent, viewport, and timezone randomization
- Stealth fingerprinting using Playwright and playwright-stealth
- Batch testing and result statistics

## Main Script
- **File:** `captcha_automation.py`
- **Key Function:** `solve_with_stealth(target_url, proxy=None, headless=False)`
    - Automates browser actions to solve reCAPTCHA v3 and extract the token and score

## Usage

### Single Solve Example
```bash
python captcha_automation.py --headless --tests-no 1
```

### Batch Solve Example
```bash
python captcha_automation.py --tests-no 50 --no-proxy
```

- Results are saved in the `results/` folder as `.txt` and `.json` files.

## Outputs
- `results/recaptcha_v3_full_results.txt`: Human-readable log of all runs
- `results/recaptcha_v3_results.json`: JSON summary with scores, tokens, and stats

## Requirements
- Python 3.8+
- Playwright & playwright-stealth
- Install dependencies from the project root:
  ```bash
  pip install -r requirements.txt
  playwright install chromium
  ```

## Notes
- Designed for integration with the FastAPI API in Task 2
- All stealth and human-like behaviors are implemented in this module
- See `TASK1QA_Abdallah_Ismail.md` for QA and assessment details
