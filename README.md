# ⚡ HelixAI: Production FastAPI Microservice with Open Models & Data Engineering Tools

[![CI Pipeline](https://github.com/himishatunwal/fastapi-open-llm-service/actions/workflows/ci.yml/badge.svg)](https://github.com/himishatunwal/fastapi-open-llm-service/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.6-E92063.svg)](https://docs.pydantic.dev/latest/)
[![uv](https://img.shields.io/badge/uv-packaging-purple.svg)](https://github.com/astral-sh/uv)
[![Docker](https://img.shields.io/badge/Docker-Multi--stage-2496ED.svg)](https://www.docker.com/)

A production-grade, containerized **FastAPI Microservice** purpose-built for executing **Open Weights Language Models** (Llama 3 8B, Mistral 7B, Phi-3 Mini) locally or via open API endpoints. Protected by **OAuth2 JWT Authentication**, **Role-Based Access Control (RBAC)**, strict **Pydantic v2 schema validation**, **AI-specific sliding-window rate controls (RPM/TPM)**, an **Autonomous Data AI Agent**, and **Data Engineering Tool Executors**.

---

## 🏗️ System Architecture

![HelixAI System Architecture](docs/architecture_diagram.jpg)

---

## 🌟 Key Features & Architecture

- **Strict Typing & Pydantic v2 Validation**: End-to-end type safety using `Annotated`, `Field`, and custom Pydantic v2 validators across all microservice API contracts.
- **OAuth2 JWT Authentication & RBAC Guards**: OAuth2 Password Bearer flow with `bcrypt` password hashing, signed JWT tokens (`pyjwt`), multi-role RBAC (`admin`, `data_engineer`, `analyst`, `user`), and runtime permission dependency guards (`PermissionChecker`).
- **Autonomous Data AI Agent**: Goal-driven multi-tool workflow router (`/api/v1/agent/run`) that autonomously executes SQL query generators, schema validators, grounded CSV dataset analytics, and PDF text parsers before synthesizing LLM executive reports.
- **Data Engineering & AI Tools**: Sandboxed tool registry supporting:
  - `sql_data_analyst_tool`: Generates dialect-aware SQL (PostgreSQL, Snowflake, BigQuery), translates query dialects, creates DDL schemas, and optimizes execution plans.
  - `pdf_csv_web_researcher`: Computes grounded answers from uploaded CSV dataset records (`sales_q3_report.csv`), extracts PDF text passages (`ai_architecture_spec.pdf`), and performs live web search RAG.
  - `data_schema_validator`: Validates raw JSON payloads for data quality, type correctness, missing fields, and null rates.
  - `text_summarizer`: Extracts intelligent executive summaries, bullet points, and action items.
  - `calculator`: Sandboxed AST mathematical and metric formula evaluator.
- **AI-Specific Rate & Usage Controls**: Memory-efficient sliding-window rate tracker enforcing dual quotas for **Requests per Minute (RPM)** and **Tokens per Minute (TPM)** per user, with dynamic TPM quota scaling (`10,000` $\rightarrow$ `25,000` TPM).
- **Flexible Open Model Inference Engine**: Runs fast local inference simulation out-of-the-box, generating context-aware SQL queries, Python Pydantic v2 code, and rich structured JSON outputs. Built-in connection adapters for **Ollama** (`http://localhost:11434`) and **HuggingFace Inference API**.
- **Interactive Streamlit Web Dashboard**: User-friendly workspace UI (`streamlit_app.py`) featuring 1-click preset role switching, raw JWT inspector, autonomous data agent executor, document RAG uploader, and dynamic token quota controls.
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
│   │   └── v1/                    # API v1 routes (auth, chat, agent, tools, prompts, models)
│   ├── core/                      # Security, JWT, RBAC Guards, Custom Exceptions
│   │   ├── rbac.py                # Roles, Permissions & PermissionChecker Dependency
│   │   ├── security.py            # Bcrypt hashing & JWT signing
│   │   └── exceptions.py          # Custom HTTP Exception classes
│   ├── models/                    # Pydantic v2 Schemas (Auth, Chat, Tools)
│   └── services/                  # Business Logic Services
│       ├── auth_service.py        # RBAC user management & authentication
│       ├── document_analyzer.py   # Grounded CSV & PDF document parser engine
│       ├── llm_service.py         # Open model inference boundary & SQL/Python response generator
│       ├── tool_service.py        # Sandboxed Data Engineering tool execution registry
│       ├── prompt_service.py      # Prompt template registry (SQL, Data Quality, Async Python)
│       └── rate_limiter.py        # Sliding-window RPM/TPM usage controller
├── demo_assets/                   # Sample Assets for Testing & Demo Video
│   ├── sales_q3_report.csv        # Enterprise transaction CSV dataset
│   ├── ai_architecture_spec.pdf   # Architecture specification PDF document
│   └── ai_architecture_spec.txt   # Plain text architecture specification
├── streamlit_app.py               # Interactive Streamlit Web UI Dashboard
├── tests/                         # Automated Pytest Suite (22 Unit Tests)
│   ├── conftest.py                # Pytest async fixtures
│   ├── test_auth.py               # Auth & JWT endpoint tests
│   ├── test_chat.py               # Chat completion & prompt template tests
│   ├── test_agent.py              # Autonomous data agent workflow tests
│   ├── test_document_analyzer.py  # Grounded CSV & PDF document parser tests
│   ├── test_tools.py              # Data tool execution tests
│   └── test_rate_limiter.py       # Sliding window rate limiter tests
└── docs/                          # Technical Architecture & Demo Documentation
    ├── architecture.md            # Technical Architecture with Mermaid & embedded diagram
    ├── architecture_diagram.jpg   # High-resolution visual system architecture flowchart
    └── api_specification.md       # Full OpenAPI Endpoint Specification
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.9+** (Python 3.10 recommended)
- **Git** & **Docker / Docker Compose** (optional for containerized execution)

---

### Running Locally (Fastest)

1. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install uv
   uv pip install -e ".[dev]" pydantic-settings email-validator python-multipart
   ```

2. **Launch the FastAPI Microservice**:
   ```bash
   PYTHONPATH=. uvicorn app.main:app --reload --port 8000
   ```
   - OpenAPI Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Microservice Health Check: [http://localhost:8000/health](http://localhost:8000/health)

3. **Launch the Streamlit Dashboard** (in a separate terminal window):
   ```bash
   source .venv/bin/activate
   streamlit run streamlit_app.py
   ```
   - Access UI Playground at: [http://localhost:8501](http://localhost:8501)

---

## 🔑 Pre-seeded Bootcamp Demo Credentials

| Role | Username | Password | Granted Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin_user` | `admin123` | `admin:all`, `chat:infer`, `tools:execute`, `metrics:read` |
| **Data Engineer** | `data_eng_user` | `data123` | `chat:infer`, `tools:execute`, `metrics:read`, `policy:evaluate` |
| **Analyst** | `analyst_user` | `analyst123` | `chat:infer`, `tools:execute`, `metrics:read`, `models:read` |
| **User** | `demo_user` | `demo123` | `chat:infer`, `tools:execute`, `models:read` |

---

## 🧪 Automated Testing

```bash
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

---

## 📜 License
MIT License - Open Source Data & AI Engineering Microservice.
