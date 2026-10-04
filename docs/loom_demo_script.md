# 🎬 AegisAI 2-Minute Video Demo Script

This script provides a concise, step-by-step walkthrough for recording the 2-minute Loom demo required for the Week 2 Project exercise.

---

## ⏱️ Video Timeline & Walkthrough

### 0:00 - 0:20 | Introduction & Architecture Overview
- **Visual**: Show the running FastAPI Swagger Docs at `http://localhost:8000/docs` and Streamlit UI at `http://localhost:8501`.
- **Script**:
  > "Hi! Welcome to AegisAI — our production containerized FastAPI microservice running open-weights LLMs locally with enterprise guardrails. This project addresses all Week 2 curriculum requirements: strict Pydantic v2 validation, JWT authentication, multi-role RBAC, sliding-window rate limiting, autonomous tool calling, and structured audit logging."

---

### 0:20 - 0:45 | Authentication, JWT & RBAC Quick Role Switcher
- **Visual**: Navigate to **Tab 1: Authentication & RBAC** in the Streamlit UI. Click **"Login as Admin (admin_user)"** and show the issued JWT access token and granted role badge.
- **Script**:
  > "First, we authenticate using OAuth2 password flow with bcrypt hashed passwords. Our microservice enforces strict Role-Based Access Control with 4 roles: Admin, Auditor, Developer, and User. Notice how logging in issues a signed JWT token containing user role and tenant context."

---

### 0:45 - 1:15 | Open LLM Chat & Autonomous Security Agent
- **Visual**: 
  1. Go to **Tab 2: Open Model Chat**. Select `llama3-open-8b`, choose a preset prompt template, enable **Enforce JSON Schema**, and run inference. Point out prompt/completion token counts and execution latency.
  2. Switch to **Tab 3: Autonomous AI Agent**. Select the sample goal prompt: *"Scan IP address 45.33.32.156 for threat intelligence and evaluate risk."* Click **Execute**. Show the step-by-step tool execution findings and final executive report.
- **Script**:
  > "Next, in our Open Model Chat tab, we run fast inference on local models like Llama 3 8B with Pydantic v2 structured JSON schema validation. In our Autonomous Agent tab, the agent evaluates user goal prompts, automatically triggers sandboxed tools like our IP Threat Intelligence scanner, and synthesizes an executive security report."

---

### 1:15 - 1:45 | Sandboxed Tool Registry, Audit Logs & Rate Limits
- **Visual**:
  1. Go to **Tab 4: Tool Registry**. Show tools like `vulnerability_scanner` and `compliance_evaluator`.
  2. Go to **Tab 5: Audit Logs**. Show real-time SOC2 audit entries logged with timestamp, user ID, tenant ID, and action.
  3. Go to **Tab 6: Rate Limits & Metrics**. Show live sliding-window Requests-per-Minute (RPM) and Tokens-per-Minute (TPM) quota progress bars.
- **Script**:
  > "For security, all tool calls run in a sandboxed execution boundary. Every single action is tracked in our Enterprise Structured Audit Logger for SOC2 compliance. Finally, our sliding-window rate limiter enforces RPM and TPM quotas per tenant, protecting our local models from abuse."

---

### 1:45 - 2:00 | DevOps Toolchain & Conclusion
- **Visual**: Show terminal with passing Pytest suite (`pytest tests/`) and Docker Compose running (`docker compose up`).
- **Script**:
  > "The entire application is packaged with `uv`, fully tested with Pytest, guarded by GitHub Actions CI, and containerized via multi-stage Docker builds. Thank you!"
