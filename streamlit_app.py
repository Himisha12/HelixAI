import json
import time
import requests
import streamlit as st
import jwt

# Page Configuration
st.set_page_config(
    page_title="DataEngine AI Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
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

    .top-navbar {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.85) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 1.2rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #34D399 50%, #A78BFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
    }

    .login-container {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        margin-bottom: 2rem;
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
        font-size: 1.4rem;
        font-weight: 700;
        color: #F8FAFC;
    }

    .badge-admin {
        background-color: rgba(139, 92, 246, 0.2);
        color: #A78BFA;
        border: 1px solid rgba(139, 92, 246, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .badge-data {
        background-color: rgba(56, 189, 248, 0.2);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .badge-analyst {
        background-color: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .badge-user {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
    }

    .timeline-step {
        background: rgba(15, 23, 42, 0.8);
        border-left: 3px solid #38BDF8;
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
        padding: 8px 18px;
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

DEMO_ACCOUNTS = {
    "👑 Admin": ("admin_user", "admin123", "admin"),
    "📊 Data Engineer": ("data_eng_user", "data123", "data_engineer"),
    "📈 Data Analyst": ("analyst_user", "analyst123", "analyst"),
    "👤 Standard User": ("demo_user", "demo123", "user"),
}

# Session State Initialization
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = ""
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = ""
if "logged_in_role" not in st.session_state:
    st.session_state["logged_in_role"] = ""

def authenticate_user(username: str, pwd: str) -> bool:
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
            return True
        else:
            st.error(f"Authentication failed: {resp.json().get('detail')}")
            return False
    except Exception as e:
        st.error(f"Backend offline: {e}")
        return False

# =========================================================
# 🔐 DEDICATED SEPARATE LOGIN PAGE (When Unauthenticated)
# =========================================================
if not st.session_state["jwt_token"]:
    st.markdown(
        """
        <div class="top-navbar">
            <div class="hero-title">🔐 AegisAI Identity & JWT Authentication Gateway</div>
            <div class="hero-subtitle">OAuth2 Password Flow + Bcrypt Password Hashing + Signed JWT Token Generation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l1, col_l2 = st.columns([1, 1])

    with col_l1:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### 🔑 User Authentication")
        
        selected_role_auth = st.selectbox("Select Account Role", list(DEMO_ACCOUNTS.keys()), index=1)
        u_def, p_def, r_def = DEMO_ACCOUNTS[selected_role_auth]

        input_user = st.text_input("Username", value=u_def)
        input_pass = st.text_input("Password", value=p_def, type="password")

        if st.button("🚀 Sign In & Issue JWT Access Token", use_container_width=True):
            if authenticate_user(input_user, input_pass):
                st.success(f"JWT Token issued for {input_user}!")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 **Pre-seeded Accounts**: Admin (`admin_user`), Data Engineer (`data_eng_user`), Analyst (`analyst_user`), User (`demo_user`).")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_l2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### 👁️ JWT Token & Header Inspector")
        st.write("Demonstrates how JWT tokens are issued and attached to HTTP Authorization headers for FastAPI RBAC validation.")
        
        sample_u, sample_p, sample_r = DEMO_ACCOUNTS[selected_role_auth]
        
        try:
            sample_resp = requests.post(
                f"{BASE_URL}/api/v1/auth/token",
                data={"username": sample_u, "password": sample_p},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if sample_resp.status_code == 200:
                t_raw = sample_resp.json()["access_token"]
                
                st.markdown("#### 1. Raw Issued JWT Access Token")
                st.code(t_raw, language="text")

                decoded_header = jwt.get_unverified_header(t_raw)
                decoded_payload = jwt.decode(t_raw, options={"verify_signature": False})

                st.markdown("#### 2. Decoded JWT Header & Claims Payload")
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    st.write("**Header**:")
                    st.json(decoded_header)
                with c_d2:
                    st.write("**Claims Payload**:")
                    st.json(decoded_payload)

                st.markdown("#### 3. Outgoing HTTP Authorization Header")
                st.code(f"Authorization: Bearer {t_raw}", language="http")
        except Exception:
            st.warning("Start FastAPI backend server on port 8000 to preview live JWT token decoding.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# =========================================================
# MAIN APP CONSOLE (Post-Authentication)
# =========================================================

# Top Navigation Header & Role Switcher Toolbar
st.markdown(
    """
    <div class="top-navbar">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div class="hero-title">⚡ DataEngine AI Studio</div>
                <div class="hero-subtitle">Production Open LLM Microservice & Data Engineering Agent Console</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

hdr_col1, hdr_col2, hdr_col3 = st.columns([2, 2, 1])

with hdr_col1:
    role = st.session_state.get("logged_in_role", "user").lower()
    badge_cls = "badge-admin" if role == "admin" else ("badge-data" if role == "data_engineer" else ("badge-analyst" if role == "analyst" else "badge-user"))
    st.markdown(f"**User**: `{st.session_state['logged_in_user']}` &nbsp;|&nbsp; Role: <span class=\"{badge_cls}\">{role.upper()}</span>", unsafe_allow_html=True)

with hdr_col2:
    selected_role_label = st.selectbox(
        "🔄 Switch Active Role (1-Click)",
        list(DEMO_ACCOUNTS.keys()),
        index=1 if role == "data_engineer" else (0 if role == "admin" else (2 if role == "analyst" else 3)),
        key="hdr_role_switch",
    )
    target_u, target_p, target_r = DEMO_ACCOUNTS[selected_role_label]
    if target_r != st.session_state["logged_in_role"]:
        authenticate_user(target_u, target_p)
        st.rerun()

with hdr_col3:
    if st.button("🚪 Logout"):
        st.session_state["jwt_token"] = ""
        st.session_state["logged_in_user"] = ""
        st.session_state["logged_in_role"] = ""
        st.rerun()

st.markdown("---")

# ---------------------------------------------------------
# Core Navigation Tabs
# ---------------------------------------------------------
tab_analyst, tab_doc_web, tab_chat, tab_gov = st.tabs([
    "🤖 1. AI Data Analyst & SQL Agent",
    "📄 2. AI Document + Web Researcher",
    "💬 3. Open Model Inference Studio",
    "📊 4. System Governance & Token Quotas",
])

# ---------------------------------------------------------
# Tab 1: AI Data Analyst & SQL Agent
# ---------------------------------------------------------
with tab_analyst:
    st.subheader("🤖 AI Data Analyst & Autonomous SQL Agent")
    st.write("Takes natural language data questions, decides whether to write SQL, perform math calculations, or profile schemas, and returns structured results.")
    
    analyst_scenarios = {
        "🛢️ PostgreSQL Regional Revenue Query": "Generate top 5 revenue customers query in Postgres with quarterly DENSE_RANK window function and region partitioning.",
        "🔄 SQL Dialect Translator (Postgres -> Snowflake)": "Translate query to Snowflake SQL and convert date functions to DATEADD/DATE_TRUNC.",
        "⚡ SQL Query Execution Plan Optimizer": "Explain query execution plan for sales_orders table and suggest indexes to eliminate Sequential Scans.",
        "🧮 Data Metric Calculation": "Calculate monthly throughput metric: (125000 / 30) * 1.15",
    }

    sel_scen = st.selectbox("Scenario Preset", list(analyst_scenarios.keys()))
    analyst_prompt_in = st.text_area("Natural Language Question / Data Goal", value=analyst_scenarios[sel_scen], height=85)
    
    c_an1, c_an2, c_an3 = st.columns([1, 1, 1])
    with c_an1:
        dialect_sel = st.selectbox("Target SQL Dialect", ["postgres", "snowflake", "bigquery", "spark"], index=0)
    with c_an2:
        model_sel = st.selectbox("LLM Model Engine", ["llama3-open-8b", "mistral-7b-open", "phi3-mini-open"], index=0)
    with c_an3:
        temp_val = st.slider(
            "Temperature", 0.0, 1.0, 0.2, 0.1,
            help="0.0 = Deterministic (Best for SQL/Math), 0.7 = Balanced, 1.0 = Creative"
        )

    if st.button("🚀 Run AI Data Analyst Agent"):
        headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
        with st.spinner("AI Data Analyst evaluating request, running tool, and synthesizing output..."):
            try:
                resp = requests.post(
                    f"{BASE_URL}/api/v1/agent/run",
                    headers=headers,
                    json={"task_description": f"{analyst_prompt_in} (Dialect: {dialect_sel})", "model": model_sel},
                )
                if resp.status_code == 200:
                    sdata = resp.json()
                    st.success(f"Analyst Agent Completed Task in {sdata.get('execution_time_ms')} ms!")
                    
                    st.markdown("#### ⚡ Autonomous Tool Steps Executed")
                    for step in sdata.get("steps", []):
                        st.markdown(
                            f"""
                            <div class="timeline-step">
                                <strong>Step {step['step_number']}: [{step['action']}] Tool <code>{step['tool_name']}</code></strong><br>
                                <span style="color:#94A3B8; font-size:0.85rem;">Arguments:</span> <code>{json.dumps(step['arguments'])}</code><br>
                                <span style="color:#94A3B8; font-size:0.85rem;">Output Result:</span>
                                <pre style="margin-top:4px; font-size:0.85rem; color:#38BDF8;">{json.dumps(step['output'], indent=2)}</pre>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    st.markdown("#### 📋 Structured Analyst Report")
                    st.info(sdata.get("final_synthesis"))
                else:
                    st.error(f"Analyst Agent Error ({resp.status_code}): {resp.json().get('detail')}")
            except Exception as e:
                st.error(f"Execution error: {e}")

# ---------------------------------------------------------
# Tab 2: AI Document + Web Researcher
# ---------------------------------------------------------
with tab_doc_web:
    st.subheader("📄 AI Document + Web Researcher")
    st.write("Combines uploaded PDFs, CSV datasets, or text documents with live web search research to answer questions using both internal private documents and external public knowledge.")
    
    uploaded_f = st.file_uploader("Upload Document (CSV, TXT, or PDF Text)", type=["csv", "txt", "log"])
    
    sample_csv_default = (
        "id,customer_name,revenue,region,orders_count\n"
        "101,Acme Corp,125000,US-East,45\n"
        "102,Globex Systems,85000,US-West,32\n"
        "103,Soylent Data,210000,EU-Central,78\n"
        "104,Initech,45000,US-East,12\n"
        "105,Umbrella Corp,310000,APAC,95"
    )

    doc_text = ""
    if uploaded_f is not None:
        try:
            doc_text = uploaded_f.getvalue().decode("utf-8")
            st.success(f"Uploaded file '{uploaded_f.name}' ({len(doc_text)} bytes) loaded!")
        except Exception as e:
            st.error(f"File reading error: {e}")
    else:
        doc_text = st.text_area("Or Paste Document / CSV Content:", value=sample_csv_default, height=120)

    c_w1, c_w2 = st.columns([3, 1])
    with c_w1:
        user_q = st.text_input("Ask ANY Question (Combining Document Data & Web Search):", value="What is the total revenue in the CSV, and what are current cloud data warehouse benchmarks for this scale?")
    with c_w2:
        enable_web_search = st.checkbox("Include Web Search RAG", value=True)

    if st.button("⚡ Research & Answer Question"):
        headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
        with st.spinner("Analyzing uploaded document and performing web research..."):
            try:
                resp = requests.post(
                    f"{BASE_URL}/api/v1/agent/run",
                    headers=headers,
                    json={
                        "task_description": f"Read document and perform web research: {user_q}",
                        "document_payload": doc_text,
                        "enable_web_research": enable_web_search,
                        "model": "llama3-open-8b"
                    },
                )
                if resp.status_code == 200:
                    res_data = resp.json()
                    st.success("Document & Web Research Completed!")
                    
                    st.markdown("#### 🔍 Extracted Document & Web Knowledge Telemetry")
                    for step in res_data.get("steps", []):
                        st.json(step["output"])

                    st.markdown("#### 🤖 Synthesized Answer (Document Data + Web Knowledge)")
                    st.info(res_data.get("final_synthesis"))
                else:
                    st.error(f"Research Error ({resp.status_code}): {resp.json().get('detail')}")
            except Exception as e:
                st.error(f"Error executing research: {e}")

# ---------------------------------------------------------
# Tab 3: Open Model Inference Studio
# ---------------------------------------------------------
with tab_chat:
    st.subheader("💬 Open Model Fast Inference & Prompt Studio")
    st.write("Direct raw prompt playground for prompt engineering, system instruction design, temperature testing, and Pydantic v2 structured JSON validation (`/api/v1/chat/completions`).")
    
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        chat_model = st.selectbox("Open Model Engine", ["llama3-open-8b", "mistral-7b-open", "phi3-mini-open"], index=0, key="c_mod")
    with c2:
        temp = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, help="0.0 = Deterministic, 0.7 = Balanced, 1.0 = Creative")
    with c3:
        max_tok = st.slider("Max Tokens", 64, 2048, 512, 64, help="Adjust token generation limit")
    with c4:
        json_enforce = st.checkbox("Structured JSON", value=False)

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

    sys_prompt = st.text_area("System Instruction", value=default_sys_text, height=75)
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
            "max_tokens": max_tok,
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
# Tab 4: System Governance & Token Quotas
# ---------------------------------------------------------
with tab_gov:
    st.subheader("📊 System Governance, Quotas & Token Limits")
    st.write("Monitors per-user sliding window token limits (TPM), request quotas (RPM), model registry, and granted RBAC claims.")

    headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
    try:
        me_resp = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        if me_resp.status_code == 200:
            mdata = me_resp.json()
            metrics = mdata.get("usage_metrics", {})
            user_info = mdata.get("user", {})
            
            st.markdown("#### 📈 Active Sliding Window Usage Quotas")
            q1, q2 = st.columns(2)
            with q1:
                rpm_curr = metrics.get("current_rpm", 0)
                rpm_max = metrics.get("max_rpm", 20)
                st.metric("Requests Per Minute (RPM Cap)", f"{rpm_curr} / {rpm_max} req/min")
                st.progress(min(1.0, rpm_curr / max(1, rpm_max)))
                
            with q2:
                tpm_curr = metrics.get("current_tpm", 0)
                tpm_max = metrics.get("max_tpm", 10000)
                st.metric("Tokens Per Minute (TPM Cap)", f"{tpm_curr} / {tpm_max} tokens/min")
                st.progress(min(1.0, tpm_curr / max(1, tpm_max)))

            st.markdown("---")
            st.markdown("#### 🎛️ Interactive Token Quota Adjuster")
            st.write("Adjust the Token-Per-Minute (TPM) limit dynamically to test rate-limiting behavior:")
            
            tpm_adj = st.slider("Set Dynamic TPM Limit", 1000, 50000, tpm_max, 1000)
            if st.button("Apply New TPM Limit"):
                from app.services.rate_limiter import rate_limiter
                rate_limiter.update_tpm_limit(tpm_adj)
                st.success(f"TPM Limit updated to {tpm_adj} tokens/min!")
                st.rerun()

            st.markdown("---")
            st.markdown("#### 📋 Role Permission Matrix (RBAC)")
            matrix_data = [
                {"Role": "👑 ADMIN", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "metrics:read": "✅ Yes", "policy:evaluate": "✅ Yes"},
                {"Role": "📊 DATA ENGINEER", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "metrics:read": "✅ Yes", "policy:evaluate": "✅ Yes"},
                {"Role": "📈 ANALYST", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "metrics:read": "✅ Yes", "policy:evaluate": "❌ No"},
                {"Role": "👤 USER", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "metrics:read": "❌ No", "policy:evaluate": "❌ No"},
            ]
            st.dataframe(matrix_data, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 🤖 Supported Open Models Registry")
            models_resp = requests.get(f"{BASE_URL}/api/v1/models")
            if models_resp.status_code == 200:
                st.json(models_resp.json())

    except Exception as e:
        st.error(f"Telemetry error: {e}")
