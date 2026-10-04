import json
import time
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="DataEngine AI Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #0A0F1D;
        color: #F8FAFC;
    }

    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #34D399 50%, #A78BFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(8px);
    }
    .card-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .card-val {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F8FAFC;
    }

    .badge-admin {
        background-color: rgba(139, 92, 246, 0.2);
        color: #A78BFA;
        border: 1px solid rgba(139, 92, 246, 0.4);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-data {
        background-color: rgba(56, 189, 248, 0.2);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-analyst {
        background-color: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-user {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .timeline-step {
        background: rgba(15, 23, 42, 0.8);
        border-left: 3px solid #34D399;
        border-radius: 0 8px 8px 0;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #38BDF8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_URL = "http://127.0.0.1:8000"

# Session State Initialization
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = ""
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = ""
if "logged_in_role" not in st.session_state:
    st.session_state["logged_in_role"] = ""

# Header Branding
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">⚡ DataEngine AI: Production Open LLM Studio</div>
        <div class="hero-subtitle">
            FastAPI + Pydantic v2 + JWT Authentication + Sliding Window Rate Controls + Data Engineering Tool Execution
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Control
st.sidebar.markdown("### 🎛️ Control Center")

try:
    health_resp = requests.get(f"{BASE_URL}/health", timeout=2)
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        st.sidebar.markdown("🟢 **Status**: `HEALTHY`")
        st.sidebar.markdown(f"⚙️ **Engine**: `{health_data.get('llm_backend')}`")
        st.sidebar.markdown(f"📦 **Default Model**: `{health_data.get('default_model')}`")
    else:
        st.sidebar.error("❌ Microservice Unreachable")
except Exception:
    st.sidebar.warning("⚠️ Microservice offline. Run `uvicorn app.main:app` on port 8000.")

st.sidebar.markdown("---")

# Active User Profile Card
if st.session_state["jwt_token"]:
    role = st.session_state["logged_in_role"].lower()
    badge_class = "badge-admin" if role == "admin" else ("badge-data" if role == "data_engineer" else ("badge-analyst" if role == "analyst" else "badge-user"))
    
    st.sidebar.markdown("#### 👤 Active User")
    st.sidebar.markdown(f"**User**: `{st.session_state['logged_in_user']}`")
    st.sidebar.markdown(f'**Role**: <span class="{badge_class}">{role.upper()}</span>', unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state["jwt_token"] = ""
        st.session_state["logged_in_user"] = ""
        st.session_state["logged_in_role"] = ""
        st.rerun()
else:
    st.sidebar.info("🔑 Unauthenticated. Use 1-Click Login below.")

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚡ 1-Click Preset Auth")

def quick_auth(username: str, pwd: str):
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/auth/token",
            data={"username": username, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code == 200:
            tdata = resp.json()
            st.session_state["jwt_token"] = tdata["access_token"]
            st.session_state["logged_in_user"] = username
            
            me_resp = requests.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {tdata['access_token']}"},
            )
            if me_resp.status_code == 200:
                st.session_state["logged_in_role"] = me_resp.json()["user"]["role"]
            st.rerun()
    except Exception as e:
        st.sidebar.error(f"Login error: {e}")

col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    if st.button("👑 Admin"):
        quick_auth("admin_user", "admin123")
    if st.button("📊 Data Eng"):
        quick_auth("data_eng_user", "data123")
with col_s2:
    if st.button("📈 Analyst"):
        quick_auth("analyst_user", "analyst123")
    if st.button("👤 User"):
        quick_auth("demo_user", "demo123")

# Main Navigation Tabs
tab_overview, tab_auth, tab_agent, tab_chat, tab_tools = st.tabs([
    "📊 1. Operations Overview",
    "🔑 2. JWT Auth & RBAC",
    "🤖 3. Autonomous Data AI Agent",
    "💬 4. Open Model Inference Studio",
    "🛠️ 5. Data Tools Sandbox",
])

# ---------------------------------------------------------
# Tab 1: Operations Overview & Quotas
# ---------------------------------------------------------
with tab_overview:
    st.subheader("Microservice Overview & Quota Telemetry")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-title">Backend Framework</div>
                <div class="card-val" style="color:#38BDF8;">FastAPI + Pydantic v2</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi2:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-title">Authentication</div>
                <div class="card-val" style="color:#A78BFA;">OAuth2 JWT + Bcrypt</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi3:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-title">Supported Models</div>
                <div class="card-val" style="color:#34D399;">Llama 3 / Mistral / Phi-3</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi4:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-title">Tooling Engine</div>
                <div class="card-val" style="color:#FBBF24;">SQL / JSON / CSV Tools</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 📈 Live Sliding-Window Rate Controls")
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Authenticate via sidebar buttons to view live usage quota metrics.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
        try:
            me_resp = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
            if me_resp.status_code == 200:
                mdata = me_resp.json()
                metrics = mdata.get("usage_metrics", {})
                user_info = mdata.get("user", {})
                
                q1, q2 = st.columns(2)
                with q1:
                    rpm_curr = metrics.get("current_rpm", 0)
                    rpm_max = metrics.get("max_rpm", 20)
                    st.metric("Requests Per Minute (RPM)", f"{rpm_curr} / {rpm_max} req/min")
                    st.progress(min(1.0, rpm_curr / max(1, rpm_max)))
                    
                with q2:
                    tpm_curr = metrics.get("current_tpm", 0)
                    tpm_max = metrics.get("max_tpm", 10000)
                    st.metric("Tokens Per Minute (TPM)", f"{tpm_curr} / {tpm_max} tokens/min")
                    st.progress(min(1.0, tpm_curr / max(1, tpm_max)))

                st.markdown("---")
                st.markdown("#### User Profile & Granted Claims")
                st.json(user_info)
        except Exception as e:
            st.error(f"Telemetry error: {e}")

# ---------------------------------------------------------
# Tab 2: JWT Auth & RBAC
# ---------------------------------------------------------
with tab_auth:
    st.subheader("OAuth2 JWT Authentication & RBAC")
    
    st.markdown("#### 📋 Role Permission Matrix")
    matrix_data = [
        {"Role": "👑 ADMIN", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "metrics:read": "✅ Yes", "policy:evaluate": "✅ Yes"},
        {"Role": "📊 DATA ENGINEER", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "metrics:read": "✅ Yes", "policy:evaluate": "✅ Yes"},
        {"Role": "📈 ANALYST", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "metrics:read": "✅ Yes", "policy:evaluate": "❌ No"},
        {"Role": "👤 USER", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "metrics:read": "❌ No", "policy:evaluate": "❌ No"},
    ]
    st.dataframe(matrix_data, use_container_width=True)

    st.markdown("---")

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("### 🔓 Manual User Login")
        man_u = st.text_input("Username", value="data_eng_user", key="m_u")
        man_p = st.text_input("Password", value="data123", type="password", key="m_p")
        
        if st.button("Generate JWT Token"):
            quick_auth(man_u, man_p)

    with col_a2:
        st.markdown("### 📝 Register New User")
        reg_u = st.text_input("New Username", key="r_u")
        reg_e = st.text_input("New Email", key="r_e")
        reg_r = st.selectbox("Role Assignment", ["user", "analyst", "data_engineer", "admin"], key="r_r")
        reg_p = st.text_input("New Password", type="password", key="r_p")
        
        if st.button("Create Account"):
            if reg_u and reg_e and reg_p:
                try:
                    resp = requests.post(
                        f"{BASE_URL}/api/v1/auth/register",
                        json={"username": reg_u, "email": reg_e, "role": reg_r, "password": reg_p},
                    )
                    if resp.status_code == 201:
                        st.success("Account created successfully!")
                        st.json(resp.json())
                    else:
                        st.error(f"Error: {resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

# ---------------------------------------------------------
# Tab 3: Autonomous Data AI Agent
# ---------------------------------------------------------
with tab_agent:
    st.subheader("Autonomous Multi-Tool Data Engineering Agent")
    st.write("The Autonomous Agent evaluates data engineering goal prompts, routes execution to data tools (SQL generator, JSON validator, CSV analyzer), and synthesizes executive takeaways.")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please authenticate to run the autonomous agent.")
    else:
        preset_scenarios = {
            "🛢️ PostgreSQL Revenue Analytics Query": "Generate top 10 revenue customers query in Postgres with quarterly window function aggregation and validate payload schema.",
            "📋 Data Schema Validation & Null Check": "Validate JSON dataset record schema and check for null values and missing fields.",
            "📊 CSV Tabular Dataset Profiling": "Profile CSV dataset snippet to compute row counts, data types, and quality metrics: id,name,revenue\\n1,Alpha,5000\\n2,Beta,12000",
            "🧮 Data Metric Calculation": "Calculate monthly throughput and cost metric: (125000 / 30) * 1.15",
        }
        
        sel_preset = st.selectbox("Select Goal Scenario Preset", list(preset_scenarios.keys()))
        task_input_text = st.text_area("Agent Goal Prompt", value=preset_scenarios[sel_preset], height=80)
        sel_agent_model = st.selectbox("Model", ["llama3-open-8b", "mistral-7b-open", "phi3-mini-open"], index=0)

        if st.button("🚀 Run Autonomous Agent"):
            headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
            with st.spinner("Agent evaluating task, invoking data tools, and synthesizing report..."):
                try:
                    resp = requests.post(
                        f"{BASE_URL}/api/v1/agent/run",
                        headers=headers,
                        json={"task_description": task_input_text, "model": sel_agent_model},
                    )
                    if resp.status_code == 200:
                        adata = resp.json()
                        st.success(f"Autonomous Workflow Completed in {adata.get('execution_time_ms')} ms!")
                        
                        st.markdown("#### ⚡ Autonomous Tool Steps Executed")
                        for step in adata.get("steps", []):
                            st.markdown(
                                f"""
                                <div class="timeline-step">
                                    <strong>Step {step['step_number']}: Executed Tool <code>{step['tool_name']}</code></strong><br>
                                    <span style="color:#94A3B8; font-size:0.85rem;">Arguments:</span> <code>{json.dumps(step['arguments'])}</code><br>
                                    <span style="color:#94A3B8; font-size:0.85rem;">Output Result:</span>
                                    <pre style="margin-top:4px; font-size:0.85rem; color:#38BDF8;">{json.dumps(step['output'], indent=2)}</pre>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("#### 📋 Executive Analysis & Synthesis")
                        st.info(adata.get("final_synthesis"))
                    else:
                        st.error(f"Agent Execution Error ({resp.status_code}): {resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Execution error: {e}")

# ---------------------------------------------------------
# Tab 4: Open Model Inference Studio
# ---------------------------------------------------------
with tab_chat:
    st.subheader("Open Model Fast Inference & Prompt Lab")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please authenticate via sidebar buttons to run completions.")
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            chat_model = st.selectbox("Open Model", ["llama3-open-8b", "mistral-7b-open", "phi3-mini-open"], index=0, key="c_mod")
        with c2:
            temp = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        with c3:
            json_enforce = st.checkbox("Enforce Structured JSON", value=False)

        # Prompt Templates Dropdown
        st.markdown("#### 📜 Prompt Engineering Template Registry")
        try:
            p_resp = requests.get(f"{BASE_URL}/api/v1/prompts")
            if p_resp.status_code == 200:
                templates = p_resp.json()
                t_names = ["Custom Prompt"] + [t["name"] for t in templates]
                sel_tmpl = st.selectbox("Template Registry", t_names)
                
                default_sys_text = "You are an expert Data & AI Engineering Assistant."
                if sel_tmpl != "Custom Prompt":
                    matched = next(t for t in templates if t["name"] == sel_tmpl)
                    default_sys_text = matched["template_text"].replace("{input_text}", "Target Data Requirement")
            else:
                default_sys_text = "You are an expert Data & AI Engineering Assistant."
        except Exception:
            default_sys_text = "You are an expert Data & AI Engineering Assistant."

        sys_prompt = st.text_area("System Instruction", value=default_sys_text, height=80)
        st.markdown("---")
        user_prompt_in = st.text_input("User Prompt", value="Write an optimized PostgreSQL SQL query to find top 5 revenue customers in Q3.")

        if st.button("⚡ Execute Model Completion"):
            headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
            payload = {
                "model": chat_model,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt_in},
                ],
                "temperature": temp,
                "max_tokens": 512,
                "structured_json": json_enforce,
            }

            with st.spinner("Processing open model completion..."):
                t0 = time.time()
                try:
                    c_resp = requests.post(f"{BASE_URL}/api/v1/chat/completions", headers=headers, json=payload)
                    lat = round((time.time() - t0) * 1000, 2)
                    
                    if c_resp.status_code == 200:
                        res_data = c_resp.json()
                        st.success(f"Inference Completed in {lat} ms!")
                        
                        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                        m_col1.metric("Backend Engine", res_data.get("backend"))
                        m_col2.metric("Prompt Tokens", res_data.get("usage", {}).get("prompt_tokens"))
                        m_col3.metric("Completion Tokens", res_data.get("usage", {}).get("completion_tokens"))
                        m_col4.metric("Total Tokens", res_data.get("usage", {}).get("total_tokens"))

                        st.markdown("#### 🤖 Model Completion Output")
                        st.code(res_data["choices"][0]["message"]["content"], language="json" if json_enforce else "markdown")
                    else:
                        st.error(f"Inference Error ({c_resp.status_code}): {c_resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

# ---------------------------------------------------------
# Tab 5: Data Tools Sandbox
# ---------------------------------------------------------
with tab_tools:
    st.subheader("Data & AI Engineering Tools Sandbox")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please authenticate via sidebar buttons to run tools.")
    else:
        try:
            t_resp = requests.get(f"{BASE_URL}/api/v1/tools")
            if t_resp.status_code == 200:
                tools_list = t_resp.json()
                st.markdown("#### Registered Tools")
                st.json(tools_list)

                st.markdown("---")
                st.markdown("#### Execute Sandboxed Data Tool")
                selected_tname = st.selectbox("Choose Tool", [t["name"] for t in tools_list])
                
                default_arg_val = '{"data_request": "Top 5 customers by revenue", "dialect": "postgres"}'
                if selected_tname == "data_schema_validator":
                    default_arg_val = '{"json_payload": "{\\"id\\": 1, \\"user\\": \\"alice\\", \\"email\\": \\"alice@data.io\\"}"}'
                elif selected_tname == "csv_data_analyzer":
                    default_arg_val = '{"csv_text": "id,name,revenue\\n1,Alpha,5000\\n2,Beta,12000"}'
                elif selected_tname == "text_summarizer":
                    default_arg_val = '{"text": "Data engineering involves building pipelines to extract, transform, and load data at scale. Clean schema validation prevents downstream pipeline failures.", "style": "executive"}'
                elif selected_tname == "calculator":
                    default_arg_val = '{"expression": "125000 / 30 * 1.15"}'

                arg_input_str = st.text_area("Arguments (JSON)", value=default_arg_val, height=90)

                if st.button("Run Tool"):
                    try:
                        args_dict = json.loads(arg_input_str)
                        headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
                        exec_resp = requests.post(
                            f"{BASE_URL}/api/v1/tools/execute",
                            headers=headers,
                            json={"tool_name": selected_tname, "arguments": args_dict},
                        )
                        if exec_resp.status_code == 200:
                            st.success("Tool Executed Successfully!")
                            st.json(exec_resp.json())
                        else:
                            st.error(f"Tool Error ({exec_resp.status_code}): {exec_resp.json().get('detail')}")
                    except json.JSONDecodeError:
                        st.error("Invalid JSON in arguments.")
        except Exception as e:
            st.error(f"Error fetching tools: {e}")
