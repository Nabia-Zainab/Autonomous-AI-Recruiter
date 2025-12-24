# 🤖 Autonomous Multi-Agent AI Recruiter

### **An Agentic AI System capable of reasoning, web research, and hiring decisions.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange)
![Groq](https://img.shields.io/badge/LLM-Groq%20(Llama3)-purple)

## 🚀 Overview
This project demonstrates a **Multi-Agent System** designed to automate the initial screening process of recruitment. Unlike traditional keyword-matching ATS, this system employs **Agentic AI** to read resumes, perform independent web research (GitHub/LinkedIn verification), and make reasoned decisions based on skills rather than just years of experience.

It solves the problem of **Hiring Bias** by evaluating candidates on their actual capabilities and digital footprint.

## ✨ Key Features
* **Multi-Agent Architecture:** Powered by **LangGraph**, utilizing distinct agents for parsing, researching, and decision-making.
* **Autonomous Web Research:** The **Researcher Agent** uses `DuckDuckGo Search` to verify candidate claims and find open-source contributions (GitHub) or professional history.
* **Context-Aware Scoring:** The **Decision Maker Agent** analyzes data against a specific Job Description, providing a score (0-100) and a reasoning log.
* **Fast Inference:** Built on **Groq API** (Llama-3/Mixtral) for near-instantaneous processing.
* **Interactive UI:** Clean dashboard built with **Streamlit** for live demonstrations.

## 🛠️ Tech Stack
* **Orchestration:** LangGraph, LangChain
* **LLM Engine:** Groq API (Llama-3-70b-Versatile / Mixtral-8x7b)
* **Tools:** DuckDuckGo Search (for live web browsing)
* **Frontend:** Streamlit
* **Data Processing:** PyPDF (PDF Parsing)

---

## 🧠 How It Works (The Agentic Workflow)

The system operates as a **State Graph** with three specialized nodes:

1.  **📄 Resume Analyst Agent:**
    * Ingests the PDF.
    * Extracts structural data: Skills, Experience, Projects, and Contact Info.
    * Identifies the candidate's name for the next step.

2.  **🕵️‍♂️ Researcher Agent (The "Human" Touch):**
    * Takes the candidate's name and searches the web.
    * Looks for GitHub repositories, LinkedIn activity, and portfolio items.
    * *Goal:* Validates if the candidate is an active developer/professional.

3.  **⚖️ Decision Maker Agent:**
    * Synthesizes the *Resume Data* + *Research Findings*.
    * Compares against the "Senior AI Engineer" job description.
    * **Logic:** Prioritizes demonstrated skills (e.g., RAG, Agents) over raw "Years of Experience."
    * **Output:** Generates a Score, a "Hire/Interview/Reject" decision, and a personalized email draft.

---

## ⚡ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/ai-recruiter-agent.git](https://github.com/your-username/ai-recruiter-agent.git)
    cd ai-recruiter-agent
    ```

2.  **Install Dependencies**
    ```bash
    pip install streamlit langgraph langchain-groq duckduckgo-search pypdf
    ```

3.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

4.  **Enter API Key**
    * The app will ask for a **Groq API Key** (Free).
    * Enter it in the sidebar to activate the agents.

---

## 📂 Project Structure

```bash
├── app.py                # Main application logic (Streamlit + LangGraph)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
