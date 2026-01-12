import streamlit as st
import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- 1. INITIALIZE ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Gemini Agentic Workforce", layout="wide")
st.title("🤖 Backend-Powered Agentic Workforce")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ System Status")
    if API_KEY and API_KEY != "your_actual_key_here":
        st.success("✅ API Key loaded from .env")
    else:
        st.warning("⚠️ No API Key found in .env")
    
    run_mode = st.radio("Execution Mode", ["Real AI", "Mock Mode"], index=1)
    selected_model = st.selectbox("Model", ["gemini-2.0-flash", "gemini-1.5-flash-8b"])
    st.divider()
    st.caption("Stage 4 added: Financial Planner")

# --- 3. THE AGENT ENGINE ---
class WorkforceManager:
    def __init__(self, mode):
        self.mode = mode
        if mode == "Real AI":
            # Using the specific 2026 stable client configuration
            self.client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})

    def run_agent(self, role, sys_msg, user_input):
        if self.mode == "Mock Mode":
            time.sleep(1)
            return self.get_mock_data(role)
        
        try:
            # 2026 STABLE SYNTAX: system_instruction inside GenerateContentConfig
            response = self.client.models.generate_content(
                model=selected_model,
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=sys_msg,
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            return json.loads(response.text)
        except Exception as e:
            st.error(f"❌ {role} Error: {e}")
            return None

    def get_mock_data(self, role):
        mocks = {
            "Optimizer": {"project_name": "Eco-Quest", "mission": "Gamified recycling.", "focus": "Mobile-first UX"},
            "Growth": {"aso_keywords": ["ecology", "game", "green"], "viral_loop": "Share stats for rewards"},
            "Architect": {"tech": "Flutter & Firebase", "structure": "/lib, /assets, /models"},
            "Finance": {"startup_cost": "$5,000", "burn_rate": "$200/mo", "revenue_model": "Freemium"}
        }
        return mocks.get(role, {"status": "success"})

# --- 4. THE CONVEYOR BELT UI ---
user_vision = st.text_area("🚀 Describe your project vision:", height=100)

if st.button("Start Workforce"):
    if not user_vision:
        st.warning("Please enter a vision.")
    else:
        wf = WorkforceManager(run_mode)
        
        # SEQUENCE: Optimizer -> Growth -> Architect -> Finance
        steps = [
            ("Optimizer", "You are a Prompt Engineer. Return JSON: project_name, mission, focus."),
            ("Growth", "You are a Growth Hacker. Return JSON: aso_keywords, viral_loop."),
            ("Architect", "You are a Software Architect. Return JSON: tech_stack, folder_structure."),
            ("Finance", "You are a Financial Planner. Return JSON: startup_cost, burn_rate, revenue_model.")
        ]
        
        context = user_vision
        for role, prompt in steps:
            with st.status(f"🤖 {role} processing...", expanded=True) as s:
                result = wf.run_agent(role, prompt, str(context))
                if result:
                    st.json(result)
                    # We pass the results forward so the next agent has context
                    context = result 
                    
                    # Save each step
                    if not os.path.exists("workforce"): os.makedirs("workforce")
                    with open(f"workforce/{role.lower()}.json", "w") as f:
                        json.dump(result, f, indent=4)
                    s.update(label=f"✅ {role} Complete", state="complete")
        
        st.success("🏁 Workforce completed. All JSON files are in the /workforce folder.")