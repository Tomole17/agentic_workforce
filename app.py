import streamlit as st
import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- INITIALIZE ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="2026 Action-Agent Workforce", layout="wide")
st.title("🏗️ Action-Oriented Agentic Workforce")

# --- THE COMPREHENSIVE ROSTER (Planning + Action) ---
AGENT_ROSTER = {
    "The Prompt Engineer": {
        "responsibility": "Catalyst: Optimizes raw vision into a Technical Manifesto.",
        "sys_prompt": "You are a Senior Prompt Engineer. Return JSON with 'project_name', 'mission', and 'technical_focus'."
    },
    "The Architect": {
        "responsibility": "Skeleton: Translates the idea into a technical roadmap.",
        "sys_prompt": "You are a Software Architect. Return JSON with 'tech_stack' and 'folder_structure'."
    },
    "The Coder (Full-Stack)": {
        "responsibility": "The Muscle: Generates actual Flutter/React Native code files.",
        "sys_prompt": "You are a Senior Developer. Based on the Architect's JSON, generate the main application code (e.g., App.js or main.dart) as a string inside a JSON object: {'filename': '...', 'code_content': '...'}"
    },
    "The UI Visionary": {
        "responsibility": "Face: Generates design layouts and user flows.",
        "sys_prompt": "You are a UI Designer. Return JSON with 'color_palette' and 'screen_list'."
    },
    "The Growth Hacker": {
        "responsibility": "Engine: Handles SEO/ASO and marketing strategy.",
        "sys_prompt": "You are a Growth Hacker. Return JSON with 'aso_keywords' and 'viral_loop'."
    },
    "The Monetizer": {
        "responsibility": "Banker: Configures revenue models and pricing.",
        "sys_prompt": "You are a Financial Monetizer. Return JSON with 'pricing_tiers' and 'revenue_model'."
    },
    "The Deployer": {
        "responsibility": "Finalizer: Creates the build scripts (Gradle/Fastlane) for .aab export.",
        "sys_prompt": "You are a DevOps Engineer. Create a JSON 'build_script' that contains the commands to compile this app into an .aab file."
    },
    "The Summarizer": {
        "responsibility": "CEO: Consolidates all outputs into a master project brief.",
        "sys_prompt": "You are the Project CEO. Summarize everything into a clear Markdown Executive Summary."
    }
}

# --- UI CONTROLS ---
col1, col2 = st.columns(2)
with col1:
    selected_agents = st.multiselect("Select Agents:", options=list(AGENT_ROSTER.keys()), default=list(AGENT_ROSTER.keys()))
with col2:
    selected_model = st.selectbox("Select Model:", ["gemini-3-flash-preview", "gemini-2.5-flash-lite", "gemini-2.0-flash"])
    run_mode = st.radio("Execution Mode:", ["Real AI", "Mock Mode"], index=1, horizontal=True)

# --- THE ENGINE ---
class WorkforceManager:
    def __init__(self, mode, model_id):
        self.mode = mode
        self.model_id = model_id
        if mode == "Real AI":
            self.client = genai.Client(api_key=API_KEY)

    def run_agent(self, role, input_context):
        if self.mode == "Mock Mode":
            time.sleep(1)
            return {"status": "Mock success", "agent": role, "data": "Simulated Action Completed."}
        
        is_text_output = (role in ["The Summarizer", "The Coder (Full-Stack)"])
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=input_context,
                config=types.GenerateContentConfig(
                    system_instruction=AGENT_ROSTER[role]["sys_prompt"],
                    response_mime_type="application/json" if not is_text_output else "text/plain",
                    temperature=0.7
                )
            )
            # Return as JSON if possible, otherwise raw text
            try: return json.loads(response.text)
            except: return response.text
        except Exception as e:
            st.error(f"❌ {role} Error: {e}")
            return None

# --- WORKFLOW ---
user_vision = st.text_area("🚀 Describe your App/Game Vision", height=100)

if st.button("Start Action Conveyor Belt"):
    if not user_vision:
        st.warning("Please enter a vision.")
    else:
        wf = WorkforceManager(run_mode, selected_model)
        all_results = {"vision": user_vision}
        
        for agent in selected_agents:
            with st.status(f"🛠️ {agent} is active...", expanded=True) as s:
                # Agents use the cumulative knowledge of the "all_results" dictionary
                result = wf.run_agent(agent, str(all_results))
                
                if result:
                    all_results[agent] = result
                    
                    # Action: Save files based on type
                    if not os.path.exists("workforce"): os.makedirs("workforce")
                    
                    if agent == "The Coder (Full-Stack)":
                        st.code(result, language="javascript")
                        with open("workforce/app_code.txt", "w") as f: f.write(str(result))
                    elif agent == "The Summarizer":
                        st.markdown(result)
                        with open("workforce/EXECUTIVE_SUMMARY.md", "w") as f: f.write(result)
                    else:
                        st.json(result)
                        fname = agent.lower().replace(" ", "_").replace("(", "").replace(")", "")
                        with open(f"workforce/{fname}.json", "w") as f: json.dump(result, f, indent=4)
                    
                    s.update(label=f"✅ {agent} Finished", state="complete")
        
        st.success("🏁 Workforce tasks complete. Your code and plans are in the /workforce folder.")