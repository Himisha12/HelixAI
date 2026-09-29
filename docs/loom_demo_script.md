# 🎬 2-Minute Loom Video Demo Script & Walkthrough

## Video Title: Containerized FastAPI Microservice with Open Models, JWT Auth & Tool Calling

---

## ⏱️ Video Script Breakdown (Total: 120 seconds)

### 0:00 - 0:20 | Introduction & Project Overview (20s)
> *"Hi everyone! In this demo, I will walk you through our containerized FastAPI microservice running open-weights language models locally with Pydantic v2 schema validation, JWT authentication, AI-specific rate controls, and LLM tool calling."*
- **Action**: Show GitHub repository structure, `docker-compose.yml`, and `pyproject.toml`.

### 0:20 - 0:45 | FastAPI Core & JWT Authentication (25s)
> *"First, let's open the interactive OpenAPI docs at `/docs`. Notice our versioned `/api/v1` routes. When we try calling `/chat/completions` without authentication, it returns a 401 Unauthorized error. Now, let's log in using our OAuth2 token endpoint to obtain a JWT token, which injects our claims and activates user rate tracking."*
- **Action**: Demonstrate `/auth/token` on Swagger UI or Streamlit UI Tab 1.

### 0:45 - 1:15 | Open LLM Inference & Structured Outputs (30s)
> *"Now let's head to our Streamlit Playground. We can select open models like Llama 3 8B or Mistral 7B, set custom temperature parameters, and enforce structured JSON outputs. Notice how the response returns real-time latency in milliseconds along with detailed token metrics—prompt tokens, completion tokens, and total usage."*
- **Action**: Execute chat completion with JSON schema toggle enabled. Show response metrics cards.

### 1:15 - 1:40 | LLM Tool Calling & AI Rate Limiting (25s)
> *"Next, let's look at tool service boundaries. The model can request tool execution, such as mathematical evaluation via our safe calculator tool or system metrics inspection. In Tab 5, we can monitor our live sliding-window rate limits enforcing Requests-Per-Minute (RPM) and Tokens-Per-Minute (TPM) caps to prevent AI abuse."*
- **Action**: Execute `calculator` tool call and show rate limit progress bar in Streamlit Tab 5.

### 1:40 - 2:00 | DevOps Toolchain & Docker Multi-Stage Build (20s)
> *"Finally, the entire stack is containerized with Docker multi-stage builds and automated with `uv`, Ruff linting, Mypy type checks, and GitHub Actions CI. Thank you!"*
- **Action**: Show passing `pytest` suite output in terminal and Docker container status (`docker compose ps`).

---

## 📌 Recording Instructions
1. Launch local backend: `source .venv/bin/activate && uvicorn app.main:app --port 8000`
2. Launch Streamlit dashboard: `streamlit run streamlit_app.py`
3. Open browser to `http://localhost:8501` and record full screen with Loom or OBS.
