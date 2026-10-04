import json
import time
import requests
import streamlit as st

st.set_page_config(
    page_title="Enterprise AI Guardrail & Open Model Microservice",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium CSS Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #6B7280;
        margin-bottom: 1.5rem;
    }
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #EEF2FF;
        color: #4F46E5;
        border: 1px solid #C7D2FE;
    }
    .step-box {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 0.85rem;
        border-radius: 4px;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_URL = "http://127.0.0.1:8000"

# Initialize Session State Variables
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = ""
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = ""
if "logged_in_role" not in st.session_state:
    st.session_state["logged_in_role"] = ""

st.markdown('<div class="main-header">⚡ AegisAI: Enterprise Open LLM Microservice</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">FastAPI + JWT Authentication + Pydantic v2 + RBAC + Autonomous AI Agent + Sliding Rate Limits</div>', unsafe_allow_html=True)

# Sidebar Control
st.sidebar.title("🛠️ Microservice Control")

try:
    health_resp = requests.get(f"{BASE_URL}/health", timeout=2)
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        st.sidebar.success(f"Backend: Healthy ({health_data.get('environment')})")
        st.sidebar.info(f"LLM Engine: `{health_data.get('llm_backend')}`")
    else:
        st.sidebar.error("Backend Error")
except Exception:
    st.sidebar.warning("⚠️ FastAPI Backend offline at localhost:8000. Please launch uvicorn server.")

if st.session_state["jwt_token"]:
    st.sidebar.success(f"🔐 User: **{st.session_state['logged_in_user']}**")
    st.sidebar.markdown(f'<span class="role-badge">Role: {st.session_state["logged_in_role"].upper()}</span>', unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("Logout"):
        st.session_state["jwt_token"] = ""
        st.session_state["logged_in_user"] = ""
        st.session_state["logged_in_role"] = ""
        st.rerun()
else:
    st.sidebar.info("🔑 Not Authenticated. Use Tab 1 to login.")

# Main Navigation Tabs
tab_auth, tab_chat, tab_agent, tab_tools, tab_audit, tab_metrics = st.tabs([
    "🔑 1. Authentication & RBAC",
    "💬 2. Open Model Chat",
    "🤖 3. Autonomous AI Agent",
    "🛠️ 4. Tool Registry",
    "📜 5. Audit Logs",
    "📊 6. Rate Limits & Metrics",
])

# ---------------------------------------------------------
# Tab 1: Authentication & RBAC Manager
# ---------------------------------------------------------
with tab_auth:
    st.subheader("User Authentication & Role-Based Access Control (RBAC)")
    
    st.markdown("#### ⚡ Quick Preset Login (Bootcamp RBAC Accounts)")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    
    def quick_login(u: str, p: str):
        try:
            resp = requests.post(
                f"{BASE_URL}/api/v1/auth/token",
                data={"username": u, "password": p},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state["jwt_token"] = data["access_token"]
                st.session_state["logged_in_user"] = u
                # Fetch profile for role
                me_resp = requests.get(
                    f"{BASE_URL}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {data['access_token']}"},
                )
                if me_resp.status_code == 200:
                    st.session_state["logged_in_role"] = me_resp.json()["user"]["role"]
                st.success(f"Logged in as {u}!")
                st.rerun()
        except Exception as e:
            st.error(f"Login error: {e}")

    with p_col1:
        if st.button("Login as User (demo_user)"):
            quick_login("demo_user", "demo123")
    with p_col2:
        if st.button("Login as Admin (admin_user)"):
            quick_login("admin_user", "admin123")
    with p_col3:
        if st.button("Login as Auditor (auditor_user)"):
            quick_login("auditor_user", "audit123")
    with p_col4:
        if st.button("Login as Developer (dev_user)"):
            quick_login("dev_user", "dev123")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔓 Manual Login")
        login_user = st.text_input("Username", value="demo_user", key="login_u")
        login_pass = st.text_input("Password", value="demo123", type="password", key="login_p")
        
        if st.button("Obtain JWT Access Token"):
            quick_login(login_user, login_pass)

    with col2:
        st.markdown("### 📝 Register New Account")
        reg_user = st.text_input("New Username", key="reg_u")
        reg_email = st.text_input("New Email", key="reg_e")
        reg_role = st.selectbox("Role", ["user", "developer", "auditor", "admin"], key="reg_r")
        reg_pass = st.text_input("New Password", type="password", key="reg_p")
        
        if st.button("Register Account"):
            if reg_user and reg_email and reg_pass:
                try:
                    resp = requests.post(
                        f"{BASE_URL}/api/v1/auth/register",
                        json={"username": reg_user, "email": reg_email, "role": reg_role, "password": reg_pass},
                    )
                    if resp.status_code == 201:
                        st.success("User registered successfully! You can now login.")
                        st.json(resp.json())
                    else:
                        st.error(f"Registration failed: {resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")

# ---------------------------------------------------------
# Tab 2: Open Model Chat & Prompt Engineering
# ---------------------------------------------------------
with tab_chat:
    st.subheader("Open Model Fast Inference & Prompt Engineering Playground")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please login in the **Authentication** tab first.")
    else:
        cfg_col1, cfg_col2, cfg_col3 = st.columns([2, 1, 1])
        with cfg_col1:
            selected_model = st.selectbox(
                "Select Open Model",
                ["llama3-open-8b", "mistral-7b-open", "phi3-mini-open"],
                index=0,
            )
        with cfg_col2:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        with cfg_col3:
            structured_json = st.checkbox("Enforce JSON Schema", value=False)

        # Prompt Template Registry Dropdown
        st.markdown("#### 📜 Reusable Prompt Templates")
        try:
            tmpl_resp = requests.get(f"{BASE_URL}/api/v1/prompts")
            if tmpl_resp.status_code == 200:
                templates = tmpl_resp.json()
                tmpl_options = ["Custom Prompt"] + [t["name"] for t in templates]
                selected_tmpl = st.selectbox("Preset Prompt Template", tmpl_options)
                
                default_sys = "You are an expert open model assistant. Answer concisely."
                if selected_tmpl != "Custom Prompt":
                    matched = next(t for t in templates if t["name"] == selected_tmpl)
                    default_sys = matched["template_text"].replace("{input_text}", "User Query")
            else:
                default_sys = "You are an expert open model assistant."
        except Exception:
            default_sys = "You are an expert open model assistant."

        system_prompt = st.text_area(
            "System Instruction / Prompt Template",
            value=default_sys,
            height=90,
        )

        st.markdown("---")
        user_prompt = st.text_input("Enter your prompt for the local model:", value="What is the capital of France?")

        if st.button("🚀 Execute Model Inference"):
            headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
            payload = {
                "model": selected_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": 512,
                "structured_json": structured_json,
            }

            with st.spinner("Executing local model inference..."):
                t0 = time.time()
                try:
                    resp = requests.post(
                        f"{BASE_URL}/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    latency = round((time.time() - t0) * 1000, 2)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"Inference Completed in {latency} ms!")
                        
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Engine Backend", data.get("backend"))
                        m2.metric("Prompt Tokens", data.get("usage", {}).get("prompt_tokens"))
                        m3.metric("Completion Tokens", data.get("usage", {}).get("completion_tokens"))
                        m4.metric("Total Tokens", data.get("usage", {}).get("total_tokens"))

                        st.markdown("### 🤖 Assistant Output")
                        st.code(data["choices"][0]["message"]["content"], language="json" if structured_json else "markdown")
                    else:
                        st.error(f"Inference Error ({resp.status_code}): {resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

# ---------------------------------------------------------
# Tab 3: Autonomous AI Agent
# ---------------------------------------------------------
with tab_agent:
    st.subheader("Autonomous Multi-Tool AI Agent Workflow")
    st.write("The Autonomous AI Agent evaluates user goals, selects tools automatically, and synthesizes final insights.")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please login first.")
    else:
        sample_tasks = [
            "Scan IP address 45.33.32.156 for threat intelligence and evaluate risk.",
            "Scan Python code for vulnerabilities: eval(user_input) and password='secret123'",
            "Evaluate compliance policy for HIPAA and SOC2: We store logs and encrypt data using AES256",
            "Calculate mathematical evaluation: 15 * 45 + 250",
        ]
        selected_sample = st.selectbox("Preset Agent Goal Task", sample_tasks)
        agent_task_input = st.text_area("Agent Goal Task Prompt", value=selected_sample, height=90)
        
        if st.button("⚡ Run Autonomous Agent"):
            headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
            with st.spinner("Agent running autonomous tool routing & inference..."):
                try:
                    resp = requests.post(
                        f"{BASE_URL}/api/v1/agent/run",
                        headers=headers,
                        json={"task_description": agent_task_input, "model": "llama3-open-8b"},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"Agent Completed Task in {data.get('execution_time_ms')} ms!")
                        
                        st.markdown("### 🔍 Autonomous Tool Execution Steps")
                        for step in data.get("steps", []):
                            st.markdown(
                                f"""
                                <div class="step-box">
                                    <strong>Step {step['step_number']}: Tool '{step['tool_name']}'</strong><br>
                                    <em>Arguments:</em> <code>{json.dumps(step['arguments'])}</code><br>
                                    <em>Result:</em> <code>{json.dumps(step['output'])}</code>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("### 📊 Executive Synthesis Report")
                        st.info(data.get("final_synthesis"))
                    else:
                        st.error(f"Agent Execution Failed ({resp.status_code}): {resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Error executing agent: {e}")

# ---------------------------------------------------------
# Tab 4: Tool Registry & Execution
# ---------------------------------------------------------
with tab_tools:
    st.subheader("LLM Tool Service Boundary Registry")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please login to execute registered tools.")
    else:
        try:
            tools_resp = requests.get(f"{BASE_URL}/api/v1/tools")
            if tools_resp.status_code == 200:
                available_tools = tools_resp.json()
                st.write("Registered System Tools:")
                st.json(available_tools)

                st.markdown("---")
                st.markdown("### Safe Sandboxed Tool Execution")
                selected_tool_name = st.selectbox("Choose Tool", [t["name"] for t in available_tools])
                
                default_arg = '{"expression": "45 * 12 + 150"}'
                if selected_tool_name == "ip_threat_lookup":
                    default_arg = '{"ip_address": "45.33.32.156"}'
                elif selected_tool_name == "vulnerability_scanner":
                    default_arg = '{"code_snippet": "import os\\neval(request.args.get(\'cmd\'))"}'
                elif selected_tool_name == "compliance_evaluator":
                    default_arg = '{"policy_text": "All data is encrypted with TLS and access is controlled via RBAC."}'
                elif selected_tool_name == "weather_lookup":
                    default_arg = '{"city": "Tokyo"}'

                tool_args_str = st.text_area("Tool Arguments (JSON)", value=default_arg, height=100)

                if st.button("Execute Tool"):
                    try:
                        args_dict = json.loads(tool_args_str)
                        headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
                        exec_resp = requests.post(
                            f"{BASE_URL}/api/v1/tools/execute",
                            headers=headers,
                            json={"tool_name": selected_tool_name, "arguments": args_dict},
                        )
                        if exec_resp.status_code == 200:
                            st.success("Tool Executed Successfully!")
                            st.json(exec_resp.json())
                        else:
                            st.error(f"Tool Error ({exec_resp.status_code}): {exec_resp.json().get('detail')}")
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format in arguments.")
        except Exception as e:
            st.error(f"Error fetching tools: {e}")

# ---------------------------------------------------------
# Tab 5: Audit Logs
# ---------------------------------------------------------
with tab_audit:
    st.subheader("Enterprise Structured Audit & Compliance Logs")
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Login as `auditor_user` or `admin_user` to inspect audit logs.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
        try:
            audit_resp = requests.get(f"{BASE_URL}/api/v1/audit-logs", headers=headers)
            if audit_resp.status_code == 200:
                logs = audit_resp.json()
                st.success(f"Retrieved {len(logs)} audit log entries.")
                st.dataframe(logs, use_container_width=True)
            elif audit_resp.status_code == 403:
                st.error("🔒 Access Denied: Your current role lacks `audit:read` permission. Login as `auditor_user` or `admin_user`.")
            else:
                st.error(f"Error loading audit logs: {audit_resp.json().get('detail')}")
        except Exception as e:
            st.error(f"Error fetching audit logs: {e}")

# ---------------------------------------------------------
# Tab 6: Rate Limits & Metrics
# ---------------------------------------------------------
with tab_metrics:
    st.subheader("AI Quotas, Sliding Window Rate Limits & Telemetry")
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Login to view live rate limiting window metrics.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state['jwt_token']}"}
        try:
            me_resp = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
            if me_resp.status_code == 200:
                data = me_resp.json()
                metrics = data.get("usage_metrics", {})
                
                col_a, col_b = st.columns(2)
                col_a.metric("Current RPM (Req/Min)", f"{metrics.get('current_rpm')} / {metrics.get('max_rpm')}")
                col_b.metric("Current TPM (Tokens/Min)", f"{metrics.get('current_tpm')} / {metrics.get('max_tpm')}")
                
                st.progress(metrics.get("current_rpm", 0) / metrics.get("max_rpm", 20))
                st.write("Current User Account & Profile:")
                st.json(data.get("user"))
        except Exception as e:
            st.error(f"Error retrieving usage metrics: {e}")
