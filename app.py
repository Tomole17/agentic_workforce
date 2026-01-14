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

st.set_page_config(page_title="2026 Agentic Workforce", layout="wide")
st.title("🚀 Enterprise Agentic Workforce")

# --- UPDATED ROSTER ---
AGENT_ROSTER = {
    "The Prompt Engineer": {
        "responsibility": "Catalyst: Optimizes raw vision into a technical Manifesto.",
        "sys_prompt": "You are a Senior Prompt Engineer. Return JSON with 'project_name', 'mission', and 'technical_focus'."
    },
    "The Architect (Lead Dev)": {
        "responsibility": "Skeleton: Translates the idea into a technical roadmap.",
        "sys_prompt": "You are a Software Architect. Return JSON with 'tech_stack' and 'folder_structure'."
    },
    "The UI/UX Visionary": {
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
    "The Summarizer": {
        "responsibility": "CEO: Consolidates all outputs into a master project brief.",
        "sys_prompt": "You are the Project CEO. Summarize all previous JSON data into a clear Markdown Executive Summary."
    }
}

# --- UI CONTROLS ---
col1, col2 = st.columns(2)
with col1:
    selected_agents = st.multiselect("Select Agents:", options=list(AGENT_ROSTER.keys()), default=list(AGENT_ROSTER.keys()))
with col2:
    # Restored models for 2026
    selected_model = st.selectbox("Select Model:", ["gemini-3-flash-preview", "gemini-2.5-flash-lite", "gemini-2.0-flash"])
    run_mode = st.radio("Execution Mode:", ["Real AI", "Mock Mode"], index=1, horizontal=True)

# --- THE ENGINE ---
class WorkforceManager:
    def __init__(self, mode, model_id):
        self.mode = mode
        self.model_id = model_id
        if mode == "Real AI":
            self.client = genai.Client(api_key=API_KEY)

    def run_agent(self, role, user_input, is_summary=False):
        if self.mode == "Mock Mode":
            time.sleep(1)
            return {"status": "Mock success", "agent": role} if not is_summary else "# Mock Executive Summary\nDone."
        
        try:
            # FIX: Using the correct snake_case field names for 2026 SDK
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=AGENT_ROSTER[role]["sys_prompt"],
                    response_mime_type="application/json" if not is_summary else "text/plain",
                    temperature=0.7
                )
            )
            return json.loads(response.text) if not is_summary else response.text
        except Exception as e:
            st.error(f"❌ {role} Error: {e}")
            return None

# --- WORKFLOW ---
user_vision = st.text_area("🚀 Input your Project Vision", height=100)

if st.button("Start Conveyor Belt"):
    if not user_vision:
        st.warning("Please enter a vision.")
    else:
        wf = WorkforceManager(run_mode, selected_model)
        all_outputs = {"original_vision": user_vision}
        
        for agent in selected_agents:
            with st.status(f"🤖 {agent} processing...", expanded=True) as s:
                is_summary = (agent == "The Summarizer")
                # Summarizer gets ALL previous data; others get the rolling context
                input_data = str(all_outputs) if is_summary else user_vision
                
                result = wf.run_agent(agent, input_data, is_summary=is_summary)
                
                if result:
                    if is_summary:
                        st.markdown(result)
                        with open("workforce/EXECUTIVE_SUMMARY.md", "w") as f: f.write(result)
                    else:
                        st.json(result)
                        all_outputs[agent] = result
                        # Save JSON
                        if not os.path.exists("workforce"): os.makedirs("workforce")
                        filename = agent.lower().replace(" ", "_").replace("(", "").replace(")", "")
                        with open(f"workforce/{filename}.json", "w") as f: json.dump(result, f, indent=4)
                    
                    s.update(label=f"✅ {agent} Finished", state="complete")
        
        st.success("🏁 Project Conveyor Belt Complete. Files saved in /workforce")