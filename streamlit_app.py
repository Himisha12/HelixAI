import json
import time
import requests
import streamlit as st

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="AegisMind Command Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Custom Modern UI Styling & Dark Glassmorphism Theme
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Background adjustments */
    .stApp {
        background-color: #090D16;
        color: #F3F4F6;
    }

    /* Header styling */
    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        font-weight: 400;
    }
    
    /* Custom Card */
    .glass-card {
        background: rgba(30, 41, 59, 0.5);
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
        font-size: 1.6rem;
        font-weight: 700;
        color: #F8FAFC;
    }

    /* Role Badges */
    .badge-admin {
        background-color: rgba(139, 92, 246, 0.2);
        color: #A78BFA;
        border: 1px solid rgba(139, 92, 246, 0.4);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-auditor {
        background-color: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-dev {
        background-color: rgba(6, 182, 212, 0.2);
        color: #22D3EE;
        border: 1px solid rgba(6, 182, 212, 0.4);
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

    /* Step Timeline Box */
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
    
    /* Code output overrides */
    code, stCode {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Tab styling */
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
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_URL = "http://127.0.0.1:8000"

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = ""
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = ""
if "logged_in_role" not in st.session_state:
    st.session_state["logged_in_role"] = ""
if "tenant_id" not in st.session_state:
    st.session_state["tenant_id"] = "tenant-enterprise-01"

# ---------------------------------------------------------
# Top Hero Branding Header
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">🛡️ AegisMind Command Console</div>
        <div class="hero-subtitle">
            Enterprise Autonomous AI Governance, Local LLM Microservice & SOC2 Security Audit Engine
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar - Runtime & Auth Status
# ---------------------------------------------------------
st.sidebar.markdown("### 🛡️ Command Console Control")

# Backend Health Check
try:
    health_resp = requests.get(f"{BASE_URL}/health", timeout=2)
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        st.sidebar.markdown("🟢 **Status**: `OPERATIONAL`")
        st.sidebar.markdown(f"⚙️ **Engine**: `{health_data.get('llm_backend')}`")
        st.sidebar.markdown(f"📦 **Default Model**: `{health_data.get('default_model')}`")
    else:
        st.sidebar.error("❌ Microservice Unreachable")
except Exception:
    st.sidebar.warning("⚠️ Microservice offline. Launch `uvicorn app.main:app` on port 8000.")

st.sidebar.markdown("---")

# Active User Profile Card
if st.session_state["jwt_token"]:
    role = st.session_state["logged_in_role"].lower()
    badge_class = f"badge-{role}" if role in ["admin", "auditor", "user"] else "badge-dev"
    
    st.sidebar.markdown("#### 👤 Active Identity")
    st.sidebar.markdown(f"**Username**: `{st.session_state['logged_in_user']}`")
    st.sidebar.markdown(f'**Role**: <span class="{badge_class}">{role.upper()}</span>', unsafe_allow_html=True)
    st.sidebar.markdown(f"**Tenant ID**: `{st.session_state['tenant_id']}`")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Terminate Session (Logout)"):
        st.session_state["jwt_token"] = ""
        st.session_state["logged_in_user"] = ""
        st.session_state["logged_in_role"] = ""
        st.rerun()
else:
    st.sidebar.info("🔑 Unauthenticated. Authenticate in Tab 2.")

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚡ Preset 1-Click Role Login")

def quick_auth(username: str, pwd: str):
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/auth/token",
            data={"username": username, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded", "X-Tenant-ID": st.session_state["tenant_id"]},
        )
        if resp.status_code == 200:
            tdata = resp.json()
            st.session_state["jwt_token"] = tdata["access_token"]
            st.session_state["logged_in_user"] = username
            
            # Fetch user profile to read role
            me_resp = requests.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {tdata['access_token']}", "X-Tenant-ID": st.session_state["tenant_id"]},
            )
            if me_resp.status_code == 200:
                st.session_state["logged_in_role"] = me_resp.json()["user"]["role"]
            st.rerun()
        else:
            st.sidebar.error("Login failed.")
    except Exception as e:
        st.sidebar.error(f"Connection error: {e}")

col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    if st.button("👑 Admin"):
        quick_auth("admin_user", "admin123")
    if st.button("🔍 Auditor"):
        quick_auth("auditor_user", "audit123")
with col_s2:
    if st.button("💻 Developer"):
        quick_auth("dev_user", "dev123")
    if st.button("👤 User"):
        quick_auth("demo_user", "demo123")

# ---------------------------------------------------------
# Main App Tabs
# ---------------------------------------------------------
tab_overview, tab_auth, tab_agent, tab_chat, tab_tools, tab_audit = st.tabs([
    "📊 1. Operations Overview",
    "🔑 2. RBAC & Identity Matrix",
    "🤖 3. Autonomous AI Agent",
    "💬 4. Open Model Inference",
    "🛠️ 5. Tool Registry Sandbox",
    "📜 6. SOC2 Audit Trail",
])

# ---------------------------------------------------------
# Tab 1: Operations Overview & KPI Metrics
# ---------------------------------------------------------
with tab_overview:
    st.subheader("System Status & Quota Telemetry")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-title">Backend Architecture</div>
                <div class="card-val" style="color:#38BDF8;">FastAPI + Pydantic v2</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi2:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-title">Security Model</div>
                <div class="card-val" style="color:#A78BFA;">OAuth2 + JWT + RBAC</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi3:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-title">Open Models Support</div>
                <div class="card-val" style="color:#34D399;">Llama3 / Mistral / Phi3</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi4:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-title">Compliance Governance</div>
                <div class="card-val" style="color:#FBBF24;">SOC2 & HIPAA Audit</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 📈 Live Sliding-Window AI Quota Monitor")
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Authenticate via sidebar preset buttons to view real-time quota metrics.")
    else:
        headers = {
            "Authorization": f"Bearer {st.session_state['jwt_token']}",
            "X-Tenant-ID": st.session_state["tenant_id"],
        }
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
                st.markdown("#### User Profile & Identity Payload")
                st.json(user_info)
        except Exception as e:
            st.error(f"Telemetry error: {e}")

# ---------------------------------------------------------
# Tab 2: RBAC & Identity Matrix
# ---------------------------------------------------------
with tab_auth:
    st.subheader("Role-Based Access Control (RBAC) Governance")
    
    st.markdown(
        """
        AegisAI enforces the **Principle of Least Privilege**. Each request must supply a valid signed JWT access token.
        Dependencies (`PermissionChecker`) enforce permissions at runtime.
        """
    )

    # Permission Matrix Reference Table
    st.markdown("#### 📋 System Role Permission Matrix")
    matrix_data = [
        {"Role": "👑 ADMIN", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "audit:read": "✅ Yes", "metrics:read": "✅ Yes", "policy:evaluate": "✅ Yes"},
        {"Role": "🔍 AUDITOR", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "audit:read": "✅ Yes", "metrics:read": "✅ Yes", "policy:evaluate": "✅ Yes"},
        {"Role": "💻 DEVELOPER", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "audit:read": "❌ No", "metrics:read": "✅ Yes", "policy:evaluate": "✅ Yes"},
        {"Role": "👤 USER", "chat:infer": "✅ Yes", "tools:execute": "✅ Yes", "audit:read": "❌ No", "metrics:read": "❌ No", "policy:evaluate": "❌ No"},
    ]
    st.dataframe(matrix_data, use_container_width=True)

    st.markdown("---")

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("### 🔓 Manual User Authentication")
        man_u = st.text_input("Username", value="admin_user", key="m_u")
        man_p = st.text_input("Password", value="admin123", type="password", key="m_p")
        tenant_in = st.text_input("Tenant Scope ID", value="tenant-enterprise-01", key="m_t")
        
        if st.button("Generate JWT Access Token"):
            st.session_state["tenant_id"] = tenant_in
            quick_auth(man_u, man_p)

    with col_a2:
        st.markdown("### 📝 Register New User")
        reg_u = st.text_input("New Username", key="r_u")
        reg_e = st.text_input("New Email", key="r_e")
        reg_r = st.selectbox("Role Assignment", ["user", "developer", "auditor", "admin"], key="r_r")
        reg_p = st.text_input("New Password", type="password", key="r_p")
        
        if st.button("Create Account"):
            if reg_u and reg_e and reg_p:
                try:
                    resp = requests.post(
                        f"{BASE_URL}/api/v1/auth/register",
                        json={"username": reg_u, "email": reg_e, "role": reg_r, "password": reg_p},
                        headers={"X-Tenant-ID": st.session_state["tenant_id"]},
                    )
                    if resp.status_code == 201:
                        st.success("Account registered successfully!")
                        st.json(resp.json())
                    else:
                        st.error(f"Error: {resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection failure: {e}")

# ---------------------------------------------------------
# Tab 3: Autonomous AI Agent
# ---------------------------------------------------------
with tab_agent:
    st.subheader("Autonomous Multi-Tool AI Agent Workflow")
    st.write("The Autonomous Agent evaluates goal prompts, invokes sandboxed tools dynamically, and synthesizes executive security reports.")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please authenticate via sidebar preset buttons to run the autonomous agent.")
    else:
        preset_scenarios = {
            "🔍 IP Threat Intelligence Scan": "Scan IP address 45.33.32.156 for threat intelligence, risk scores, and geolocation.",
            "⚡ Static Code OWASP Vulnerability Check": "Scan Python source code snippet for security risks: eval(user_input) and password = 'supersecretpass123'",
            "⚖️ SOC2 & HIPAA Governance Audit": "Evaluate compliance policy text for HIPAA and SOC2: All customer data encrypted with TLS 1.3 and access is restricted via RBAC.",
            "🧮 Sandboxed Math Computation": "Perform mathematical evaluation: (450 * 12) + (1850 / 5) - 25",
        }
        
        selected_scenario_name = st.selectbox("Select Autonomous Scenario Preset", list(preset_scenarios.keys()))
        agent_task_text = st.text_area("Agent Goal Investigation Prompt", value=preset_scenarios[selected_scenario_name], height=80)
        selected_agent_model = st.selectbox("LLM Inference Engine Model", ["llama3-open-8b", "mistral-7b-open", "phi3-mini-open"], index=0)

        if st.button("🚀 Run Autonomous AI Agent"):
            headers = {
                "Authorization": f"Bearer {st.session_state['jwt_token']}",
                "X-Tenant-ID": st.session_state["tenant_id"],
            }
            with st.spinner("Agent running autonomous task routing and tool execution..."):
                try:
                    resp = requests.post(
                        f"{BASE_URL}/api/v1/agent/run",
                        headers=headers,
                        json={"task_description": agent_task_text, "model": selected_agent_model},
                    )
                    if resp.status_code == 200:
                        adata = resp.json()
                        st.success(f"Task Completed Successfully in {adata.get('execution_time_ms')} ms!")
                        
                        st.markdown("#### ⚡ Autonomous Tool Execution Steps")
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

                        st.markdown("#### 📋 Executive Report Synthesis")
                        st.info(adata.get("final_synthesis"))
                    else:
                        st.error(f"Agent Execution Error ({resp.status_code}): {resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Execution failed: {e}")

# ---------------------------------------------------------
# Tab 4: Open Model Inference Studio
# ---------------------------------------------------------
with tab_chat:
    st.subheader("Open Model Fast Inference & Prompt Engineering Studio")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please authenticate via sidebar preset buttons to use the chat studio.")
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            chat_model = st.selectbox("Open Weights Model", ["llama3-open-8b", "mistral-7b-open", "phi3-mini-open"], index=0, key="c_model")
        with c2:
            temp = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        with c3:
            json_enforce = st.checkbox("Enforce JSON Schema", value=False)

        # Prompt Templates Dropdown
        st.markdown("#### 📜 Reusable System Prompt Templates")
        try:
            p_resp = requests.get(f"{BASE_URL}/api/v1/prompts")
            if p_resp.status_code == 200:
                templates = p_resp.json()
                t_names = ["Custom Instruction"] + [t["name"] for t in templates]
                sel_tmpl = st.selectbox("Template Registry", t_names)
                
                default_sys_text = "You are an expert open model assistant. Answer concisely."
                if sel_tmpl != "Custom Instruction":
                    matched = next(t for t in templates if t["name"] == sel_tmpl)
                    default_sys_text = matched["template_text"].replace("{input_text}", "Target Payload")
            else:
                default_sys_text = "You are an expert open model assistant."
        except Exception:
            default_sys_text = "You are an expert open model assistant."

        sys_prompt = st.text_area("System Instruction", value=default_sys_text, height=80)
        st.markdown("---")
        user_prompt_in = st.text_input("User Prompt", value="Analyze the security implications of local AI execution in containerized environments.")

        if st.button("⚡ Execute Model Completion"):
            headers = {
                "Authorization": f"Bearer {st.session_state['jwt_token']}",
                "X-Tenant-ID": st.session_state["tenant_id"],
            }
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

            with st.spinner("Processing local model completion..."):
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

                        st.markdown("#### 🤖 Model Completion Payload")
                        st.code(res_data["choices"][0]["message"]["content"], language="json" if json_enforce else "markdown")
                    else:
                        st.error(f"Inference Error ({c_resp.status_code}): {c_resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection failure: {e}")

# ---------------------------------------------------------
# Tab 5: Tool Registry Sandbox
# ---------------------------------------------------------
with tab_tools:
    st.subheader("LLM Service Boundary Tool Registry")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please authenticate via sidebar preset buttons to execute tools.")
    else:
        try:
            t_resp = requests.get(f"{BASE_URL}/api/v1/tools")
            if t_resp.status_code == 200:
                tools_list = t_resp.json()
                st.markdown("#### Registered System Tools")
                st.json(tools_list)

                st.markdown("---")
                st.markdown("#### Execute Sandboxed Tool")
                selected_tname = st.selectbox("Choose Tool", [t["name"] for t in tools_list])
                
                default_arg_val = '{"expression": "45 * 12 + 150"}'
                if selected_tname == "ip_threat_lookup":
                    default_arg_val = '{"ip_address": "45.33.32.156"}'
                elif selected_tname == "vulnerability_scanner":
                    default_arg_val = '{"code_snippet": "import os\\neval(request.args.get(\'cmd\'))"}'
                elif selected_tname == "compliance_evaluator":
                    default_arg_val = '{"policy_text": "All data encrypted with TLS and access controlled via RBAC."}'
                elif selected_tname == "weather_lookup":
                    default_arg_val = '{"city": "Tokyo"}'

                arg_input_str = st.text_area("Arguments (JSON)", value=default_arg_val, height=90)

                if st.button("Run Tool Execution"):
                    try:
                        args_dict = json.loads(arg_input_str)
                        headers = {
                            "Authorization": f"Bearer {st.session_state['jwt_token']}",
                            "X-Tenant-ID": st.session_state["tenant_id"],
                        }
                        exec_resp = requests.post(
                            f"{BASE_URL}/api/v1/tools/execute",
                            headers=headers,
                            json={"tool_name": selected_tname, "arguments": args_dict},
                        )
                        if exec_resp.status_code == 200:
                            st.success("Tool Execution Succeeded!")
                            st.json(exec_resp.json())
                        else:
                            st.error(f"Tool Error ({exec_resp.status_code}): {exec_resp.json().get('detail')}")
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format in arguments.")
        except Exception as e:
            st.error(f"Error fetching tools: {e}")

# ---------------------------------------------------------
# Tab 6: SOC2 Audit Trail
# ---------------------------------------------------------
with tab_audit:
    st.subheader("Enterprise Structured Audit Log Inspector")
    st.write("Tracks all security-relevant auth logins, permission checks, model inferences, and tool executions.")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Authenticate as `auditor_user` or `admin_user` to inspect audit logs.")
    else:
        headers = {
            "Authorization": f"Bearer {st.session_state['jwt_token']}",
            "X-Tenant-ID": st.session_state["tenant_id"],
        }
        try:
            audit_resp = requests.get(f"{BASE_URL}/api/v1/audit-logs", headers=headers)
            if audit_resp.status_code == 200:
                logs_data = audit_resp.json()
                st.success(f"Retrieved {len(logs_data)} structured audit log entries.")
                st.dataframe(logs_data, use_container_width=True)
            elif audit_resp.status_code == 403:
                st.error("🔒 Access Denied: Your current role lacks `audit:read` permission. Login as `auditor_user` or `admin_user` using sidebar preset buttons.")
            else:
                st.error(f"Error loading audit trail: {audit_resp.json().get('detail')}")
        except Exception as e:
            st.error(f"Error fetching audit trail: {e}")
