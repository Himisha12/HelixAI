# ⚡ Production FastAPI Microservice with Open Models & Local Execution

[![CI Pipeline](https://github.com/himishatunwal/fastapi-open-llm-service/actions/workflows/ci.yml/badge.svg)](https://github.com/himishatunwal/fastapi-open-llm-service/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.6-E92063.svg)](https://docs.pydantic.dev/latest/)
[![uv](https://img.shields.io/badge/uv-packaging-purple.svg)](https://github.com/astral-sh/uv)
[![Docker](https://img.shields.io/badge/Docker-Multi--stage-2496ED.svg)](https://www.docker.com/)

A production-grade, containerized **FastAPI Microservice** designed for executing **Open Weights Language Models** (e.g. Llama 3 8B, Mistral 7B, Phi-3 Mini) locally or via free-tier API endpoints. Protected by **JWT Authentication**, strict **Pydantic v2 schema validation**, **AI-specific sliding-window rate controls**, and sandboxed **LLM Tool Calling**.

---

## 🌟 Key Features & Architecture

- **Strict Typing & Pydantic v2 Validation**: End-to-end type safety using `Annotated`, `Field`, and custom Pydantic v2 validators.
- **JWT Authentication & Password Security**: Standard OAuth2 Password Bearer flow with `bcrypt` password hashing and signed JWT tokens (`pyjwt`).
- **AI-Specific Rate & Usage Controls**: Sliding-window memory tracker enforcing dual quotas for **Requests per Minute (RPM)** and **Tokens per Minute (TPM)** per user.
- **Independent Model & Tool Boundaries**: Decoupled clean architecture separating HTTP routing from LLM inference engines (`app/services/llm_service.py`) and sandboxed tool registries (`app/services/tool_service.py`).
- **Flexible Open Model Inference Engine**: Runs fast local inference simulation out-of-the-box, with built-in connection adapters for **Ollama** (`http://localhost:11434`), **HuggingFace Inference API**, and **OpenRouter**.
- **Interactive Streamlit Web Dashboard**: User-friendly UI (`streamlit_app.py`) for login, open model playground, tool calling, JSON schema enforcement, and live quota metrics.
- **Production Engineering Toolchain**: Pre-configured with `uv` package management, multi-stage `Dockerfile`, `docker-compose.yml`, `ruff` linter, `mypy` type checker, and GitHub Actions CI workflow.

---

## 📁 Repository Structure

```text
Week 2 Assignment/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI Workflow
├── .gitignore                     # Git Ignore rules
├── .dockerignore                 # Docker build ignore rules
├── .pre-commit-config.yaml        # Pre-commit hooks configuration
├── pyproject.toml                 # uv package & project dependencies metadata
├── Dockerfile                     # Multi-stage production Docker build
├── docker-compose.yml             # Orchestration for FastAPI API & Streamlit UI
├── README.md                      # Production README documentation
├── .env.example                   # Environment configuration template
├── app/                           # FastAPI Core Application Source Code
│   ├── main.py                    # Application entrypoint & CORS middleware
│   ├── config.py                  # Pydantic v2 Settings configuration
│   ├── api/                       # Versioned API Router (/api/v1)
│   │   ├── router.py              # Main API router assembly
│   │   └── v1/                    # API v1 routes (auth, chat, tools, models)
│   ├── core/                      # Security & JWT logic, Custom Exceptions
│   ├── models/                    # Pydantic v2 Schemas (Auth, Chat, Tools)
│   └── services/                  # Business Logic (Auth, LLM, Tools, Rate Limiter)
├── streamlit_app.py               # Interactive Streamlit Web UI Dashboard
├── tests/                         # Automated Pytest Suite
│   ├── conftest.py                # Pytest async fixtures
│   ├── test_auth.py               # Auth & JWT endpoint tests
│   ├── test_chat.py               # Chat completion & prompt template tests
│   ├── test_tools.py              # Tool execution tests
│   └── test_rate_limiter.py       # Sliding window rate limiter tests
└── docs/                          # Technical Architecture & Demo Documentation
    ├── architecture.md            # Technical Architecture with Mermaid diagrams
    ├── api_specification.md       # Full OpenAPI Endpoint Specification
    └── loom_demo_script.md        # 2-Minute Video Demo Script
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.9+** (Python 3.10 recommended)
- **Git** & **Docker / Docker Compose** (optional for containerized execution)

---

### Option 1: Running Locally (Fastest)

1. **Clone the Repository & Set up Virtual Environment**:
   ```bash
   git clone https://github.com/himishatunwal/fastapi-open-llm-service.git
   cd fastapi-open-llm-service

   # Create virtual environment using uv or python
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies via `uv`**:
   ```bash
   pip install uv
   uv pip install -e ".[dev]" pydantic-settings email-validator
   ```

3. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```

4. **Launch the FastAPI Microservice**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - OpenAPI Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Microservice Health Check: [http://localhost:8000/health](http://localhost:8000/health)

5. **Launch the Streamlit Dashboard** (in a separate terminal window):
   ```bash
   source .venv/bin/activate
   streamlit run streamlit_app.py
   ```
   - Access UI Playground at: [http://localhost:8501](http://localhost:8501)

---

### Option 2: Running with Docker Compose

Run both the FastAPI microservice and Streamlit dashboard in isolated containers with a single command:

```bash
docker compose up --build
```

- **FastAPI API Server**: `http://localhost:8000`
- **Streamlit Web Dashboard**: `http://localhost:8501`

---

## 🧪 Automated Testing & Code Quality

Run the complete test suite with coverage:

```bash
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

Run linter & static type checks:

```bash
# Code linting
ruff check app tests

# Static type checking
mypy app
```

---

## 🔑 Pre-seeded Demo Credentials

For quick evaluation and video demo testing, a demo account is pre-seeded into the system:

- **Username**: `demo_user`
- **Password**: `demo123`

---

## 📚 Curriculum Topic Mapping

| Curriculum Day | Topic / Skill | Implementation in Repository |
| :--- | :--- | :--- |
| **Day 6** | Strict Typing & Pydantic v2 | End-to-end Python type hints, `pydantic.BaseModel`, `Field`, `EmailStr` in [`app/models/`](file:///Users/himishatunwal/Week%202%20Assignment/app/models) |
| **Day 6** | `uv` Packaging | Configured [`pyproject.toml`](file:///Users/himishatunwal/Week%202%20Assignment/pyproject.toml) managed via `uv` |
| **Day 6** | Streamlit UI | Interactive playground [`streamlit_app.py`](file:///Users/himishatunwal/Week%202%20Assignment/streamlit_app.py) |
| **Day 7** | FastAPI Dependency Injection | Custom [`Depends()`](file:///Users/himishatunwal/Week%202%20Assignment/app/api/v1/auth.py) for auth, settings, rate limiting |
| **Day 7** | JWT Authentication Integration | OAuth2 bearer tokens & `bcrypt` hashing in [`app/core/security.py`](file:///Users/himishatunwal/Week%202%20Assignment/app/core/security.py) |
| **Day 7** | AI Rate & Usage Controls | Sliding window RPM/TPM limiter in [`app/services/rate_limiter.py`](file:///Users/himishatunwal/Week%202%20Assignment/app/services/rate_limiter.py) |
| **Day 7** | Service Boundaries | Decoupled architecture in [`app/services/llm_service.py`](file:///Users/himishatunwal/Week%202%20Assignment/app/services/llm_service.py) |
| **Day 8** | Dockerization & Multi-stage | Multi-stage [`Dockerfile`](file:///Users/himishatunwal/Week%202%20Assignment/Dockerfile) & [`docker-compose.yml`](file:///Users/himishatunwal/Week%202%20Assignment/docker-compose.yml) |
| **Day 8** | GitHub Actions CI | Automated lint/type/test workflow in [`.github/workflows/ci.yml`](file:///Users/himishatunwal/Week%202%20Assignment/.github/workflows/ci.yml) |
| **Day 9** | Prompt Engineering | Prompt template compiler & system instruction handling |
| **Day 10** | Fast Inference & Tool Calling | Fast open model runner & sandboxed tools in [`app/services/tool_service.py`](file:///Users/himishatunwal/Week%202%20Assignment/app/services/tool_service.py) |

---

## 📜 License

MIT License. Developed for Production AI Engineering & Microservice Curriculum.
