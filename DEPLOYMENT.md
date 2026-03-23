# 🚀 Multi-Agent Trip Planner — Complete Deployment Guide (Vercel)

This project is a multi-agent AI system built entirely in Python using **Langchain**, **Google Gemini (2.5 Flash)**, **Flask**, and **Pydantic**. It simulates a multi-agent interaction via centralized shared memory, bypassing complex third-party frameworks like CrewAI while remaining heavily structured.

## 🛠️ Technology Stack
1. **Frontend:** 
   - Vanilla HTML5 & CSS3
   - Glassmorphism UI (modern blurry backdrops)
   - Dynamic DOM manipulation using Vanilla JS
2. **Backend Framework:**
   - Flask 3.0+ (Micro-web framework for routing and orchestration)
3. **AI & Agent Architecture:**
   - `langchain` and `langchain-core` for Prompt Templates and memory integration.
   - `langchain-google-genai` for structured outputs from Gemini.
   - `pydantic` for strict data validation (enforcing LLM schemas).
4. **Agent Types:**
   - **RecommendationAgent**: Uses LLM to identify matching places.
   - **PlannerAgent**: Distributes places across time periods logically using LLM.
   - **BudgetAgent**: Math-driven calculations paired with LLM-generated summaries.
5. **Memory Management:**
   - Stateful singleton (`SharedMemory`) holding `destination`, `budget`, `itinerary`, and AI reflections across the pipeline execution.
6. **Deployment:**
   - Vercel (`@vercel/python` adapter)

---

## 🗂️ Project Architecture

```
multiagentic/
├── .env                           # Environment variables (API Key)
├── vercel.json                    # Configuration for Vercel deployment
├── requirements.txt               # All pip dependencies
├── app.py                         # Flask application & Vercel entry point
├── trip_planner_system.py         # Multi-agent Orchestrator
├── memory/
│   └── shared_memory.py           # Shared singleton memory
├── tools/
│   ├── budget_tool.py             # Math validation tool
│   ├── itinerary_tool.py          # Baseline tool for the AI planner
│   └── recommendation_tool.py     # Static destination lookup tool
├── data/
│   └── destinations.json          # Dataset for AI context mapping
├── agents/ 
│   ├── base_agent.py              # Base Agent Class
│   ├── budget_agent.py            # Financial AI Analyst
│   ├── planner_agent.py           # Scheduling AI Agent
│   ├── recommendation_agent.py    # Tourist Suggestion AI Agent
│   └── user_agent.py              # CLI user input collector
├── templates/                     # Flask HTML pages
│   ├── index.html                 # Landing Page
│   └── result.html                # Output Dashboard
└── static/
    └── css/style.css              # Glassmorphic Styles
```

---

## ☁️ Deployment on Vercel

The application is natively ready to deploy to Vercel. 

### Prerequisite Checklist
1. You have a free [Vercel account](https://vercel.com/).
2. You have a GitHub account.
3. You have a **Google Gemini API Key**.

### Step-by-Step Deployment Instructions

#### 1. Push Code to GitHub
Push this entire folder (`multiagentic`) to a new public or private repository on GitHub.
Make sure you DO NOT push the `.env` file (ensure you have `.gitignore` set properly, though since it's a manual deploy here, Vercel ignores `.env` physically).

#### 2. Import to Vercel
1. Log in to Vercel and click **Add New Project**.
2. Import the newly created GitHub repository.
3. Keep the **Framework Preset** as `Other`.
4. In the **Environment Variables** section, add your Google API key:
   - Key: `GOOGLE_API_KEY`
   - Value: `AIzaSyBCmf-8l6zR7qhwGBxxbIsgAyv09c20iV4`
   - Add another variable:
   - Key: `SECRET_KEY`
   - Value: `trip-planner-secret-2026`
5. Click **Deploy**.

#### How Vercel Handles This:
Vercel looks at the `vercel.json` file we've provided:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```
This tells Vercel to install packages from `requirements.txt` using `@vercel/python` and to redirect all routing to `app.py`. The Flask `app` instance is exported at the top level, which the Vercel serverless environment automatically locates.

---

## 💻 Local Testing Before Deployment

To safely run this locally before pushing, use these standard Python instructions:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add API key inside .env
# GOOGLE_API_KEY=your_key_here

# 3. Run the Flask Web Interface
python app.py

# 4. Open in Browser
# Navigate to http://127.0.0.1:5000
```

## 🔍 Detailed AI Agent Flows

### User Context Injection
The Flask web form collects data (`destination`, `budget`, `days`, `preferences`) and injects it directly into the `SharedMemory`.

### Recommendation Agent (LangChain + Gemini)
- Pulls available attractions for the destination from `data/destinations.json`.
- Compiles a dynamic `PromptTemplate` incorporating the user's specific text preferences.
- Uses `.with_structured_output` (Pydantic schema) to enforce that Gemini returns a strictly validated `list[str]` of places.

### Planner Agent (LangChain + Gemini)
- Fetches the recommended `list[str]` from memory.
- Uses Gemini to construct logical day blocks, e.g., mapping proximal places to the same day.
- Output parsed rigorously via Pydantic model (`DayPlan` inside `ItineraryOutput`). 

### Budget Agent (Math Engine + Gemini)
- A hybrid agent: uses deterministic math logic (`tools/budget_tool.py`) for absolute financial precision (to ensure no AI hallucinations accidentally tell you a ₹20k trip costs ₹2k).
- Invokes Gemini separately at the end of the calculation specifically to write a creative 2-sentence "budget tip".
