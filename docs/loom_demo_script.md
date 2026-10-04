# 🎬 AegisAI 4-Minute Video Demo Script & Sample Assets Guide

This guide provides everything you need to record a seamless 4-minute demo video for your Data & AI Engineering assignment:
1. **Demo Files** located in `demo_assets/`
2. **Copy-Paste Sample Prompts** for each tab
3. **End-to-End 4-Minute Spoken Script** with minute-by-minute timestamps and on-screen actions.

---

## 📁 Demo Sample Assets (`demo_assets/`)

| File Name | Location | Description / Purpose |
| :--- | :--- | :--- |
| **`sales_q3_report.csv`** | [`demo_assets/sales_q3_report.csv`](file:///Users/himishatunwal/Week%202%20Assignment/demo_assets/sales_q3_report.csv) | Enterprise transaction dataset for uploading in **Tab 2 (Document + Web Researcher)** |
| **`ai_architecture_spec.pdf`** | [`demo_assets/ai_architecture_spec.pdf`](file:///Users/himishatunwal/Week%202%20Assignment/demo_assets/ai_architecture_spec.pdf) | Technical architectural PDF document for testing PDF Q&A |
| **`ai_architecture_spec.txt`** | [`demo_assets/ai_architecture_spec.txt`](file:///Users/himishatunwal/Week%202%20Assignment/demo_assets/ai_architecture_spec.txt) | Plain text architecture specification |

---

## 📋 Copy-Paste Sample Prompts

### 🔹 Tab 1: Autonomous SQL AI Agent
* **Prompt 1 (SQL Query Generation)**:
  > `"Write an optimized Snowflake SQL query to aggregate total revenue, average transaction size, and total order count per product category for Q3, filtered for completed status and ordered by total revenue descending."`
* **Prompt 2 (Dialect & DDL Creation)**:
  > `"Generate a PostgreSQL CREATE TABLE schema for enterprise customer transactions including Pydantic v2 data validation constraints, primary key indexing, and timestamp default values."`

### 🔹 Tab 2: AI Document + CSV Reader & Web Researcher
* **Prompt 1 (CSV Document Analysis)**:
  > `"What is the total sales revenue across all completed orders in the uploaded CSV, which region has the highest revenue, and how does this compare with current 2026 enterprise cloud spending benchmarks on the web?"`
* **Prompt 2 (PDF Architectural Spec Query)**:
  > `"Based on the uploaded architecture specification, what are the sliding window rate limits, supported open LLMs, and role access controls?"`

### 🔹 Tab 3: Open Model Fast Inference Studio
* **System Instruction**:
  > `"You are an expert Data & AI Infrastructure Architect specializing in scalable Python FastAPI microservices and vector indexing pipelines."`
* **User Prompt**:
  > `"Compare PyArrow vs Pandas for processing 50GB parquet files in memory. Provide 3 key engineering tradeoffs and Python code snippets."`

---

## ⏱️ End-to-End 4-Minute Spoken Script

```
Total Duration: 04:00
Target Word Count: ~550 - 600 words
Pacing: Energetic, clear, professional Data & AI Engineer tone
```

---

### 🟢 0:00 – 0:45 | Section 1: Introduction & Microservice Architecture
* **On-Screen Action**: 
  - Show Streamlit UI (`http://localhost:8501`) side-by-side with FastAPI Swagger Docs (`http://localhost:8000/docs`).
  - Highlight the top navigation bar and active role indicator.
* **Spoken Speech**:
  > *"Hi everyone! Welcome to **AegisAI** — a containerized, production-grade FastAPI microservice and Streamlit workspace purpose-built for Data and AI Engineers.*
  > 
  > *In real-world data engineering pipelines, we need fast, local, zero-cost LLM intelligence with strict API guardrails. AegisAI solves this by hosting open-weights LLMs — like Llama 3 8B and Mistral 7B — behind signed OAuth2 JWT authentication, role-based access control, sliding-window rate limiting, and autonomous AI agents.*
  > 
  > *The backend is built with FastAPI and Pydantic v2, containerized with multi-stage Docker builds, and fully verified with Pytest."*

---

### 🔵 0:45 – 1:30 | Section 2: 1-Click Preset Auth, RBAC & Token Rate Limits
* **On-Screen Action**:
  - Point to the top **1-Click Preset Auth** dropdown in the header.
  - Switch from **`Data Engineer (engineer_dev)`** to **`Analyst (analyst_user)`** and then **`Admin (admin_user)`**.
  - Show the live **Raw JWT Access Token** container expanding and the dynamic **TPM Limit Adjuster** slider moving from `10,000` to `25,000`.
* **Spoken Speech**:
  > *"At the very top of our interface, notice our 1-Click Preset Auth dropdown. This allows data engineers and security auditors to instantly switch between active roles — Admin, Analyst, Data Engineer, and standard User.*
  > 
  > *When I switch roles, AegisAI instantly generates a cryptographically signed OAuth2 JWT access token using bcrypt hashed credentials. Below, you can inspect the live decoded JWT payload showing user ID, granted permissions, and token expiry.*
  > 
  > *Notice our dynamic Token Quota Adjuster. Administrators can scale tenant rate limits on the fly — for instance, bumping the sliding-window ceiling from 10,000 to 25,000 Tokens Per Minute to handle heavy batch ETL workloads."*

---

### 🟣 1:30 – 2:30 | Section 3: Autonomous SQL AI Agent
* **On-Screen Action**:
  - Click on **Tab 1: Autonomous SQL AI Agent**.
  - Select target database engine: **`Snowflake`**.
  - Paste Prompt: `"Write an optimized Snowflake SQL query to aggregate total revenue and average transaction size per product category, ordered by total revenue descending."`
  - Click **⚡ Execute Autonomous Agent Task**.
  - Scroll down to show the generated SQL query, execution strategy breakdown, and telemetry metrics (execution time, tokens used, model engine).
* **Spoken Speech**:
  > *"Now let's explore Tab 1: our Autonomous SQL AI Agent. For data engineers, writing complex multi-dialect SQL and query optimization plans can be time-consuming.*
  > 
  > *Here, I select target database engine 'Snowflake' and ask the agent to aggregate Q3 revenue and transaction counts by product category.*
  > 
  > *Under the hood, the autonomous agent analyzes the request, selects the dialect translation tool, generates clean dialect-specific SQL, and provides a structured execution strategy. Notice the telemetry block detailing model latency, backend engine, and exact token consumption."*

---

### 🟡 2:30 – 3:30 | Section 4: AI Document + CSV Reader & Web Researcher
* **On-Screen Action**:
  - Click on **Tab 2: AI Document + Web Researcher**.
  - Click **Browse files** and upload `sales_q3_report.csv` from `demo_assets/`.
  - Check the box **"Include Web Search RAG"**.
  - Enter question: `"What is the total revenue in the uploaded CSV, and how does this compare with current 2026 enterprise cloud benchmarks on the web?"`
  - Click **⚡ Research & Answer Question**.
  - Show the response combining internal CSV data numbers (`$117,100.50`) with live web search benchmarks.
* **Spoken Speech**:
  > *"Next is Tab 2: AI Document + Web Researcher. In data engineering, we frequently need to synthesize internal dataset records with external web documentation.*
  > 
  > *I'll drag and drop our `sales_q3_report.csv` file from `demo_assets/`. With Web Search RAG enabled, I ask the agent to total our completed CSV revenue and contextualize it against current 2026 industry benchmarks.*
  > 
  > *The agent parses the uploaded CSV rows in real-time, extracts the exact revenue total, executes web search retrieval, and merges both private data and public web knowledge into a unified executive report."*

---

### 🔴 3:30 – 4:00 | Section 5: Open Model Inference Studio & Conclusion
* **On-Screen Action**:
  - Click on **Tab 3: Open Model Fast Inference Studio**.
  - Set model: `llama3-open-8b`, Temperature: `0.7`, Max Tokens: `512`.
  - Type prompt: `"Compare PyArrow vs Pandas for 50GB parquet files."`
  - Click **⚡ Execute Model Completion**.
  - Show model response, prompt/completion token count metrics, and closing screen.
* **Spoken Speech**:
  > *"Finally, Tab 3 is our Open Model Fast Inference Studio — a playground for testing open models like Llama 3 8B, tweaking temperature parameters, and prototyping custom system instructions.*
  > 
  > *In conclusion, AegisAI delivers an end-to-end, enterprise-ready AI microservice for Data Engineers — combining autonomous SQL generation, document RAG, open LLM inference, and robust RBAC security.*
  > 
  > *Thank you for watching!"*
```

---

## 🎯 Tips for a Smooth Recording
1. **Screen Layout**: Open Streamlit at `http://localhost:8501` in a full-screen browser window.
2. **Preset Auth**: Keep `Data Engineer (engineer_dev)` selected at the start.
3. **Files Ready**: Have `demo_assets/sales_q3_report.csv` visible on your desktop or file finder for easy drag-and-drop.
4. **Volume**: Speak clearly into your microphone with confidence.
