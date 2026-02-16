# stealth-scraping-distributed-system

This repository provides a modular and scalable solution for advanced web automation and distributed data extraction. 

It features a stealth-based engine capable of achieving high human-like scores on reCAPTCHA v3 through browser fingerprinting and network reputation management. 

The system is built around a FastAPI-driven architecture that utilizes a RabbitMQ message queue for efficient task distribution across horizontally scalable worker nodes.

 Designed for enterprise-level resilience, the codebase includes advanced DOM scraping logic to filter element visibility and a comprehensive monitoring stack for tracking system health, current load, and error logging across a microservices environment.


## Project Structure & Tasks

### Task 1: Stealth reCAPTCHA Solver
- Implements advanced browser automation to solve reCAPTCHA v3 with high human-likeness.
- Features: human-like mouse movement, scrolling, delays, proxy rotation, and stealth fingerprinting.
- Script: `task1_automation/captcha_automation.py`

### Task 2: FastAPI reCAPTCHA Solving API
- Exposes the stealth solver as an asynchronous API with SQLite persistence.
- Endpoints:
  - `POST /recaptcha/in`: Submit a solve request, returns a TaskID.
  - `GET /recaptcha/res`: Poll for the result using TaskID.
- Limits to 10 concurrent browser tasks and rotates proxies automatically.
- Folder: `task2_api/`

### Task 3: Web Scraping & Image/Text Extraction
- Scrapes images and visible text from target web pages.
- Saves all images as base64 and filters for human-visible images/text only.
- Scripts and results in: `task3_scraping/`

### Task 4: Distributed System Design
- Documents a scalable microservices architecture for distributed scraping.
- Includes architecture diagrams, queue-based task distribution, monitoring, and failover strategies.
- Documentation: `task4_system_design/`

---

## Local Setup

To set up the project locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone
   ```

2. Navigate to the project directory:

   ```bash
   cd stealth-scraping-distributed-system
   ```

3. Create a virtual environment (optional but recommended):

   ```bash  
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```
5. Install Playwright browsers:

   ```bash
   playwright install chromium
   ```

Follow the specific instructions in the `README` of each task folder for running the respective scripts and APIs.

- [Task 1: Stealth reCAPTCHA Solver](task1_automation/README.md)
- [Task 2: FastAPI reCAPTCHA Solving API](task2_api/README.md)
- [Task 3: Web Scraping & Image/Text Extraction](task3_scraping/README.md)
- [Task 4: Distributed System Design](task4_system_design/README.md)

