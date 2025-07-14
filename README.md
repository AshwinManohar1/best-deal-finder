# AI Shopping Agent

This project is an AI-powered agent designed to find the best price for a given product by searching across various e-commerce websites. It's built using FastAPI for the web interface and a locally-hosted open-source language model served by vLLM for its reasoning capabilities.

## Features

*   **Asynchronous Job Processing**: Submit a product search and get a `job_id` back immediately.
*   **AI-Powered Reasoning**: Uses a local LLM (Qwen1.5-1.8B-Chat) to decide which websites to check.
*   **Live Status Tracking**: Poll an endpoint to get real-time status updates on your search job.
*   **Scalable Architecture**: Decoupled API server and LLM inference server.

## Project Structure

```
/shopping-agent
|
├── .venv/                  # Virtual environment
├── agent/
│   ├── __init__.py
│   └── llm_client.py       # Utility for calling the vLLM server
├── tools/
│   └── __init__.py
├── main.py                 # FastAPI application and endpoints
├── qwen_chat_template.jinja # Chat template for the Qwen model
├── requirements.txt        # Project dependencies
└── README.md               # This file
```

## Setup and Installation

Follow these steps to set up the project locally.

### 1. Prerequisites

*   Python 3.8+
*   `uv` package manager (or `pip`)
*   An NVIDIA GPU with CUDA installed (recommended for vLLM performance)

### 2. Clone and Set Up Environment

```bash
# Clone this repository (if applicable)
# git clone ...
cd shopping-agent

# Create a virtual environment using uv
uv venv

# Activate the virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

This project uses `uv` for fast package management.

```bash
# Install all required Python packages
uv pip install fastapi "uvicorn[standard]" pydantic vllm openai
```

The first time you run the vLLM server, it will automatically download the model weights from Hugging Face (approx. 3.6 GB).

---

## How to Run the Services

This application requires two separate services to be running in two different terminals.

### Terminal 1: Start the vLLM Inference Server

This server hosts the Qwen language model and exposes an OpenAI-compatible API.

```bash
# Make sure your virtual environment is activated
# (.venv) ...

python -m vllm.entrypoints.openai.api_server \
  --model "Qwen/Qwen1.5-1.8B-Chat" \
  --chat-template "qwen_chat_template.jinja" \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90
```

**Keep this terminal open.** You'll know it's ready when you see log messages indicating the server is running on `http://localhost:8000`.

### Terminal 2: Start the FastAPI Application Server

This server runs our main application logic and API endpoints.

```bash
# Make sure your virtual environment is activated
# (.venv) ...

uvicorn main:app --reload
```

This will start the API server on `http://127.0.0.1:8000`. Wait, we have a problem! Both servers are trying to use port 8000. Let's fix that.

**To run both simultaneously, start the FastAPI server on a different port:**

```bash
# Run the FastAPI app on port 8001
uvicorn main:app --reload --port 8001
```

**Keep this terminal open.** The `--reload` flag will automatically restart the server if you make changes to the code.

---

## How to Use the API

Once both servers are running, you can interact with the agent through its API endpoints. Use a tool like `curl` or any API client.

Remember to use the correct port for the FastAPI server (e.g., `8001`).

### 1. Start a New Search Job

Send a `POST` request with the product name you want to search for.

```bash
curl -X POST "http://127.0.0.1:8001/agent/shopping/start" \
-H "Content-Type: application/json" \
-d '{"product_name": "Logitech MX Master 3S Mouse"}'
```

The API will immediately respond with a unique `job_id`:

```json
{"job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"}
```

**Copy this `job_id`** to check the status later.

### 2. Check the Job Status

Send a `GET` request to the status endpoint, using the `job_id` you received.

```bash
# Replace <your-job-id> with the actual ID from the previous step
curl "http://127.0.0.1:8001/agent/shopping/status/<your-job-id>"
```

The response will show the current state of the job, including its status (`PENDING`, `RUNNING`, `COMPLETED`), intermediate steps, and the final result once available.

**Example Response (after completion):**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "status": "COMPLETED",
  "request": {
    "product_name": "Logitech MX Master 3S Mouse"
  },
  "result": {
    "llm_suggestions": "Amazon, Best Buy, Logitech's official website"
  },
  "intermediate_steps": [
    "Agent started. Asking LLM for ideas about 'Logitech MX Master 3S Mouse'.",
    "LLM suggested the following websites to check: Amazon, Best Buy, Logitech's official website"
  ]
}
```

## How to Stop the Services

To stop the application, simply go to each of the two terminals and press `CTRL+C`.