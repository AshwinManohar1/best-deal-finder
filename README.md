# Best Deal Finder

Best Deal Finder is an AI-powered agent platform that helps you find the best price for any product online. It leverages large language models (LLMs) and a Streamlit web interface for interactive use. The backend uses FastAPI and a local vLLM server for LLM inferencing.

---

## 🚀 Features
- **Automated price search**: Finds the best price and source for any product.
- **Web search and scraping**: Uses APIs and browser automation to gather real-time data.
- **LLM-powered reasoning**: Uses a local LLM (Qwen) to decide which tools to use.
- **Modern web UI**: Streamlit app for easy interaction.
- **API-first**: FastAPI backend for programmatic access.

---

## 🏗️ Architecture

```mermaid
graph TD;
    User-->|Web UI|Streamlit
    User-->|API|FastAPI
    Streamlit-->|REST API|FastAPI
    FastAPI-->|LLM Calls|vLLM Server
    FastAPI-->|Web Search/Scrape|Tools
    Tools-->|External|Web
```

---

## ⚡ Quickstart

### 1. Install Dependencies

This project uses [uv](https://github.com/astral-sh/uv) for Python environment and dependency management:

```bash
uv sync
```

---

### 2. Start the API Server (FastAPI + Uvicorn)

```bash
uv run uvicorn main:app --reload --port 8001
```

---

### 3. Start the vLLM Server

```bash
python -m vllm.entrypoints.openai.api_server \
  --model "Qwen/Qwen1.5-1.8B-Chat" \
  --chat-template "qwen_chat_template.jinja" \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90
```
- Adjust `--model` and other parameters as needed for your hardware and requirements.

---

### 4. Start the Streamlit App

```bash
streamlit run streamlit_app.py
```

---

## 🛠️ API Usage Example

You can use the API directly to start a best-deal search job:

```bash
curl -X POST http://localhost:8001/agent/best-deal/start \
  -H "Content-Type: application/json" \
  -d '{"product_name": "iPhone 15"}'
```

**Response:**
```json
{
  "result": "The best price for iPhone 15 is $799 at BestBuy: https://www.bestbuy.com/iphone-15"
}
```

---

## 🤝 Contributing

1. Fork this repo and clone your fork.
2. Create a new branch for your feature or bugfix.
3. Make your changes and add tests if needed.
4. Run `uv sync` and `pytest` to ensure all tests pass.
5. Submit a pull request!

---

## 📝 Notes
- Ensure you have the required model files and GPU resources for vLLM.
- For more details, see the source code and comments in each script.
- If you have issues, please open an issue or discussion on GitHub.