# stealth-scraping-distributed-system

This repository provides a modular and scalable solution for advanced web automation and distributed data extraction. 

It features a stealth-based engine capable of achieving high human-like scores on reCAPTCHA v3 through browser fingerprinting and network reputation management. 

The system is built around a FastAPI-driven architecture that utilizes a RabbitMQ message queue for efficient task distribution across horizontally scalable worker nodes.

 Designed for enterprise-level resilience, the codebase includes advanced DOM scraping logic to filter element visibility and a comprehensive monitoring stack for tracking system health, current load, and error logging across a microservices environment.


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
