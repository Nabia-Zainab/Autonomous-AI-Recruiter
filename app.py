import streamlit as st
import os
import json
from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, END
from pypdf import PdfReader
import io

# ==============================================================================
# 1. SETUP & CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Multi-Agent AI Recruiter", layout="wide")

st.title("🤖 Multi-Agent AI Recruiter")
st.markdown("### Powered by Groq, LangGraph & Streamlit")

# Sidebar for API Key
api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

if not api_key:
    st.warning("Please enter your Groq API Key in the sidebar to proceed.")
    st.stop()

# Initialize LLM
llm = ChatGroq(
    groq_api_key=api_key,
    model_name="llama-3.3-70b-versatile",
    temperature=0
)

# Initialize Tools
search = DuckDuckGoSearchRun()

# ==============================================================================
# 2. STATE DEFINITION (The "Shared Clipboard")
# ==============================================================================
class AgentState(TypedDict):
    """
    The state of our graph.
    It passes data between agents.
    """
    resume_text: str       # Raw text from PDF
    candidate_profile: dict # Structured data (Name, Skills, Experience)
    research_summary: str   # Findings from DuckDuckGo
    final_decision: dict    # {score, decision, email}
    logs: List[str]         # To track progress for UI

# ==============================================================================
# 3. AGENT DEFINITIONS (The "Employees")
# ==============================================================================

# --- Node 1: Resume Analyst ---
def resume_analyst(state: AgentState):
    """
    Extracts structured data from the resume text.
    """
    print("--- 1. ANALYST_AGENT ---")
    log = "Analyst is reading the resume..."
    
    # Prompt for the LLM
    start_msg = f"""
    You are a Senior Technical Recruiter.
    Extract the following from the resume text:
    - Name (Full Name)
    - Email
    - Years of Experience (Numeric estimate)
    - Key Skills (List of technical skills)
    - Summary (2 sentence professional summary)
    
    Resume Text:
    {state['resume_text']}
    
    Return ONLY valid JSON in this format:
    {{
      "name": "...",
      "email": "...",
      "years_of_experience": 5,
      "skills": ["..."],
      "summary": "..."
    }}
    """
    
    response = llm.invoke([HumanMessage(content=start_msg)])
    try:
        # Simple parsing (in production, use JsonOutputParser)
        # We strip backticks if the LLM output markdown
        content = response.content.replace("```json", "").replace("```", "").strip()
        candidate_profile = json.loads(content)
    except Exception as e:
        candidate_profile = {"error": f"Failed to parse JSON: {e}"}

    return {
        "candidate_profile": candidate_profile,
        "logs": [log, f"Extracted: {candidate_profile.get('name', 'Unknown')}"]
    }

# --- Node 2: Researcher (Web Surfer) ---
def researcher(state: AgentState):
    """
    Searches for the candidate online to verify info.
    """
    print("--- 2. RESEARCHER_AGENT ---")
    profile = state['candidate_profile']
    name = profile.get("name")
    
    if not name or name == "Unknown":
        return {"research_summary": "Skipped research: No name found.", "logs": ["Researcher skipped (No Name)"]}

    log = f"Researcher is searching for: {name}..."
    
    # Search Query
    query = f"{name} software engineer linkedin github"
    try:
        search_results = search.run(query)
    except Exception as e:
        search_results = f"Search failed: {e}"

    # Summarize findings with LLM
    summary_prompt = f"""
    You are a background checker.
    Summarize these search results for candidate '{name}'.
    Focus on:
    - Current Role/Company
    - GitHub Activity (if visible)
    - Consistency with a resume (do they look like a real dev?)
    
    Search Results:
    {search_results}
    """
    summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
    
    return {
        "research_summary": summary_response.content,
        "logs": [log, "Research complete."]
    }

# --- Node 3: Decision Maker ---
def decision_maker(state: AgentState):
    """
    Makes the final hire/no-hire decision based on all data.
    """
    print("--- 3. DECISION_MAKER ---")
    
    job_description = """
    Job Title: Senior AI Engineer
    Requirements:
    - 5+ years of Python experience
    - Experience with LLMs (LangChain, OpenAI, HuggingFace)
    - Knowledge of Vector Databases (Pinecone, Chroma)
    - Strong backend skills (FastAPI/Django)
    - Good communication skills
    """
    
    prompt = f"""
    You are the Hiring Manager. Evaluate this candidate based on the Job Description.
    
    Candidate Profile: {json.dumps(state['candidate_profile'])}
    Research Findings: {state['research_summary']}
    
    Job Description:
    {job_description}
    
    Task:
    1. Assign a Score (0-100).
    2. Make a Decision (Hire / Interface / Reject).
    3. Draft a short, personalized email to the candidate.
    
    Return ONLY valid JSON:
    {{
      "score": 85,
      "decision": "Interview",
      "email": "Subject: ... Body: ..."
    }}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        content = response.content.replace("```json", "").replace("```", "").strip()
        final_decision = json.loads(content)
    except:
        final_decision = {"score": 0, "decision": "Error", "email": "Could not generate decision."}
        
    return {
        "final_decision": final_decision,
        "logs": ["Decision made."]
    }

# ==============================================================================
# 4. GRAPH CONSTRUCTION (The Workflow)
# ==============================================================================
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("analyst", resume_analyst)
workflow.add_node("researcher", researcher)
workflow.add_node("decision_maker", decision_maker)

# Add Edges (Linear Flow)
workflow.set_entry_point("analyst")
workflow.add_edge("analyst", "researcher")
workflow.add_edge("researcher", "decision_maker")
workflow.add_edge("decision_maker", END)

# Compile
app = workflow.compile()

# ==============================================================================
# 5. UI EXECUTION
# ==============================================================================
uploaded_files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files and st.button("Analyze Candidates"):
    
    for uploaded_file in uploaded_files:
        st.divider()
        st.subheader(f"Processing: {uploaded_file.name}")
        
        # 1. Read PDF
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")
            continue

        # 2. Display 'Thinking' Process
        status_container = st.status("Agent Workflow Running...", expanded=True)
        
        initial_state = {
            "resume_text": text,
            "candidate_profile": {},
            "research_summary": "",
            "final_decision": {},
            "logs": []
        }
        
        # Run graph
        final_state = initial_state
        try:
            # We want to show updates, but for simplicity in Streamlit sync, 
            # we will run it and print logs as we go if we could stream, 
            # but simpler here: run full invoke
            final_state = app.invoke(initial_state)
            
            # Simulated Logs Display (since we can't easily stream intermediate steps in this simple sync pattern)
            status_container.write("✅ Analyst Extracted Data")
            status_container.write(f"   Name: {final_state['candidate_profile'].get('name')}")
            status_container.write("✅ Researcher Verified Online Presence")
            status_container.write("✅ Decision Maker Finalized Score")
            status_container.update(label="Analysis Complete!", state="complete", expanded=False)
            
        except Exception as e:
            st.error(f"Error running workflow: {e}")
            status_container.update(label="Analysis Failed", state="error")
            continue

        # 3. Display Results
        col1, col2 = st.columns([1, 2])
        
        with col1:
            score = final_state['final_decision'].get('score', 0)
            st.metric("Candidate Score", f"{score}/100")
            
            decision = final_state['final_decision'].get('decision', 'Unknown')
            if decision == "Interview":
                st.success(f"Decision: {decision}")
            elif decision == "Reject":
                st.error(f"Decision: {decision}")
            else:
                st.warning(f"Decision: {decision}")

        with col2:
            st.markdown("#### Research Summary")
            st.info(final_state['research_summary'])
            
            st.markdown("#### Email Draft")
            email_content = final_state['final_decision'].get('email', '')
            st.code(email_content, language="markdown")
            
        # JSON details (Optional)
        with st.expander("Full Debug Data"):
            st.json(final_state)
