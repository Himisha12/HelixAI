import json
import time
import requests
import streamlit as st

st.set_page_config(
    page_title="Open Model Microservice Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #6B7280;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #E5E7EB;
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
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.markdown('<div class="main-header">⚡ Open Model Microservice Playground</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">FastAPI + JWT Authentication + Pydantic v2 + AI Rate Limiting + Tool Execution</div>', unsafe_allow_html=True)

# Sidebar - System Connection & Auth Status
st.sidebar.title("🛠️ Microservice Control")

try:
    health_resp = requests.get(f"{BASE_URL}/health", timeout=2)
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        st.sidebar.success(f"Backend Status: Healthy ({health_data.get('environment')})")
        st.sidebar.info(f"LLM Backend Engine: `{health_data.get('llm_backend')}`")
    else:
        st.sidebar.error("Backend Error")
except Exception:
    st.sidebar.warning("⚠️ FastAPI Backend offline at localhost:8000. Please launch server.")

if st.session_state["jwt_token"]:
    st.sidebar.success(f"🔐 Authenticated as: **{st.session_state['logged_in_user']}**")
    if st.sidebar.button("Logout"):
        st.session_state["jwt_token"] = ""
        st.session_state["logged_in_user"] = ""
        st.rerun()
else:
    st.sidebar.info("🔑 Not Authenticated. Use the Auth tab to login/register.")

# Main Navigation Tabs
tab_auth, tab_chat, tab_tools, tab_models, tab_metrics = st.tabs([
    "🔑 1. Authentication",
    "💬 2. LLM Chat Playground",
    "🛠️ 3. Tool Calling",
    "🤖 4. Model Registry",
    "📊 5. Rate & Usage Metrics",
])

# ---------------------------------------------------------
# Tab 1: Authentication (JWT Token Generation)
# ---------------------------------------------------------
with tab_auth:
    st.subheader("User Registration & JWT Login")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔓 Login")
        login_user = st.text_input("Username", value="demo_user", key="login_u")
        login_pass = st.text_input("Password", value="demo123", type="password", key="login_p")
        
        if st.button("Obtain JWT Access Token"):
            try:
                resp = requests.post(
                    f"{BASE_URL}/api/v1/auth/token",
                    data={"username": login_user, "password": login_pass},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                if resp.status_code == 200:
                    token_data = resp.json()
                    st.session_state["jwt_token"] = token_data["access_token"]
                    st.session_state["logged_in_user"] = login_user
                    st.success("✅ JWT Token successfully issued!")
                    st.json(token_data)
                else:
                    st.error(f"Authentication failed: {resp.json().get('detail')}")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")

    with col2:
        st.markdown("### 📝 Register New Account")
        reg_user = st.text_input("New Username", key="reg_u")
        reg_email = st.text_input("New Email", key="reg_e")
        reg_pass = st.text_input("New Password", type="password", key="reg_p")
        
        if st.button("Register Account"):
            if reg_user and reg_email and reg_pass:
                try:
                    resp = requests.post(
                        f"{BASE_URL}/api/v1/auth/register",
                        json={"username": reg_user, "email": reg_email, "password": reg_pass},
                    )
                    if resp.status_code == 201:
                        st.success("User registered! You can now login on the left.")
                        st.json(resp.json())
                    else:
                        st.error(f"Registration failed: {resp.json().get('detail')}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")
            else:
                st.warning("Please fill all fields.")

# ---------------------------------------------------------
# Tab 2: LLM Chat Playground
# ---------------------------------------------------------
with tab_chat:
    st.subheader("Open Model Fast Inference Playground")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please login under the **Authentication** tab first to enable JWT header.")
    else:
        cfg_col1, cfg_col2, cfg_col3 = st.columns([2, 1, 1])
        with cfg_col1:
            selected_model = st.selectbox(
                "Select Model",
                ["llama3-open-8b", "mistral-7b-open", "phi3-mini-open"],
                index=0,
            )
        with cfg_col2:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        with cfg_col3:
            structured_json = st.checkbox("Enforce JSON Schema", value=False)

        system_prompt = st.text_area(
            "System Instruction / Prompt Template",
            value="You are an expert open model assistant. Answer concisely.",
            height=70,
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

            with st.spinner("Executing model inference..."):
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
# Tab 3: Tool Calling
# ---------------------------------------------------------
with tab_tools:
    st.subheader("LLM Tool Execution Boundary")
    
    if not st.session_state["jwt_token"]:
        st.warning("⚠️ Please login in the Authentication tab to execute tools.")
    else:
        try:
            tools_resp = requests.get(f"{BASE_URL}/api/v1/tools")
            if tools_resp.status_code == 200:
                available_tools = tools_resp.json()
                st.write("Available Registered Tools:")
                st.json(available_tools)

                st.markdown("---")
                st.markdown("### Execute Tool Handler")
                selected_tool_name = st.selectbox("Choose Tool", [t["name"] for t in available_tools])
                
                tool_args_str = st.text_area(
                    "Tool Arguments (JSON)",
                    value='{"expression": "45 * 12 + 150"}' if selected_tool_name == "calculator" else '{"city": "Tokyo"}',
                    height=100,
                )

                if st.button("Run Tool"):
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
                            st.error(f"Tool Error: {exec_resp.json().get('detail')}")
                    except json.JSONDecodeError:
                        st.error("Invalid JSON string provided in arguments.")
        except Exception as e:
            st.error(f"Error fetching tools: {e}")

# ---------------------------------------------------------
# Tab 4: Model Registry
# ---------------------------------------------------------
with tab_models:
    st.subheader("Supported Open Weights Models")
    try:
        models_resp = requests.get(f"{BASE_URL}/api/v1/models")
        if models_resp.status_code == 200:
            st.json(models_resp.json())
        else:
            st.error("Could not retrieve models.")
    except Exception as e:
        st.error(f"Backend offline: {e}")

# ---------------------------------------------------------
# Tab 5: AI Rate & Usage Metrics
# ---------------------------------------------------------
with tab_metrics:
    st.subheader("User Quota & Sliding-Window Rate Controls")
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
                st.write("User Profile Details:")
                st.json(data.get("user"))
        except Exception as e:
            st.error(f"Error retrieving usage metrics: {e}")
