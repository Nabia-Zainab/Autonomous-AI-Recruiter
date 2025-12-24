# Multi-Agent AI Recruiter - Technical Architecture & Educational Guide

## 1. Why this Tech Stack?

### **Streamlit vs. Chainlit vs. React/Next.js**
*   **Streamlit (Chosen):** It is the fastest way to turn data scripts into shareable web apps. It requires **zero** HTML/CSS knowledge and handles the frontend state purely in Python. For a "Proof of Concept" (PoC) or internal tool like this Recruiter Agent, it's perfect.
*   **Chainlit:** Excellent for "Chat" interfaces specifically. If our app was purely a chatbot (like ChatGPT), Chainlit would be better. But we need a *dashboard* feel with file uploaders, sidebars, and structured metrics, which Streamlit handles better.
*   **React/Next.js:** Overkill for a single developer building a PoC. It requires a separate backend (FastAPI/Flask) and frontend.

### **LangGraph vs. CrewAI vs. AutoGen**
*   **LangGraph (Chosen):** It provides **low-level control** over the flow. It models the application as a "State Machine" (Graph). This is crucial when you need deterministic paths (e.g., Analyst -> Researcher -> Decision Maker). You *know* exactly what happens next.
*   **CrewAI:** Great for "Pattern-based" orchestration (e.g., "Process these tasks hierarchically"). It abstracts away a lot of the control. It's easier to start but harder to debug if agents get stuck in loops.
*   **AutoGen:** Best for "Conversational" multi-agent systems where agents chat with each other to solve code. Our use case is a linear data processing pipeline, so a Graph is more appropriate than a Conversation.

### **Groq Llama 3.3 vs. GPT-4**
*   **Groq (Chosen):** Speed. Groq's LPU (Language Processing Unit) inference is lightning fast (300+ tokens/sec). For an agentic workflow where one agent waits for another, latency kills the user experience. Groq makes it feel near-instant.

## 2. The Agent Workflow (The Graph)

We are using a **StateGraph**. Think of it as passing a shared clipboard (`State`) between employees (`Agents`).

1.  **State Initialization:** User uploads a PDF. We put the raw text into the `State`.
2.  **Node 1: Analyst Agent:** Pick up the `State`. Use LLM to extract Name, Email, Skills. Write back to `State`.
3.  **Node 2: Researcher Agent:** Read Name/Skills from `State`. Search DuckDuckGo. summarize findings. Write back to `State`.
4.  **Node 3: Decision Maker:** Read everything. Score against criteria. Write Final verdict.
5.  **End:** UI displays the final `State`.

## 3. Alternative Approaches (What else could we have done?)
*   **RAG (Retrieval Augmented Generation):** Instead of passing the whole Resume text to the LLM, we could have chunked it and stored it in a Vector DB (FAISS/Chroma).
    *   *Why not here?* Resumes are short (1-2 pages). Modern LLMs (Llama 3.3) have 128k context windows. We can fit 500 resumes in context easily. RAG adds complexity (embeddings, retrieval) without benefit for single-doc processing.
*   **Asynchronous Processing (Celery/Redis):** If this was a production app handling 10,000 resumes, we wouldn't hold the user's browser connection open. We'd accept the file, give a "Job ID", and process it in the background using a message queue.

## 4. Key Learnings in this Code
*   **Structured Output:** Notice how we force the LLM to return JSON. This is critical for agents to "talk" to code.
*   **State Management:** LangGraph's `TypedDict` schema ensures we never lose data between steps.
