"""
trip_planner_system.py
-----------------------
Orchestrator for the multi-agent Trip Planner system using the CrewAI framework.
Now uses Google Search (Serper) for completely dynamic, real-world data 
supporting ANY city globally.
"""

from __future__ import annotations

import os
import json
import re
from typing import Any, Dict, List

# If CrewAI is not installed, it will raise ImportError.
from crewai import Agent, Task, Crew, Process

try:
    from tools.searchapi_tool import searchapi_tool
except ImportError:
    import os
    import requests
    from crewai_tools import tool

    @tool("SearchApi Travel Explorer")
    def searchapi_tool(query: str) -> str:
        """Search the web using SearchApi.io for travel information, flights, costs, and attractions."""
        api_key = os.getenv("SEARCHAPI_API_KEY", "NgNQCzCKrNvRCJe7AcMz29gS")
        params = {"engine": "google", "q": query, "api_key": api_key}
        try:
            response = requests.get("https://www.searchapi.io/api/v1/search", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get("organic_results", [])
            snippets = [
                f"Title: {r.get('title', '')}\nSnippet: {r.get('snippet', r.get('description', ''))}"
                for r in results[:5]
            ]
            return "\n".join(snippets) if snippets else "No results found."
        except Exception as e:
            return f"Error executing search: {str(e)}"

# ------------------------------------------------------------------
# LLM & Tools Setup
# ------------------------------------------------------------------

# CrewAI >= v0.28 uses LiteLLM internally.
# The llm parameter on Agent must be a plain string in LiteLLM format.
if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

LLM_MODEL = "gemini/gemini-2.5-flash"

# Initialize Search Tool
search_tool = searchapi_tool

# Configure LiteLLM retries so 429s are automatically retried with backoff
try:
    import litellm
    litellm.num_retries = 5
except ImportError:
    pass

# ------------------------------------------------------------------
# Orchestrator
# ------------------------------------------------------------------

class TripPlannerSystem:
    """
    Orchestrates the full trip-planning multi-agent pipeline using CrewAI.
    """

    def __init__(self) -> None:
        pass

    def run_with_data(
        self,
        destination: str,
        budget: int,
        days: int,
        preferences: List[str],
    ) -> Dict[str, Any]:
        """
        Run the full pipeline without interactive input using Crew components.
        """
        
        # 1. Recommendation Agent
        recommendation_agent = Agent(
            role="Local Travel Expert",
            goal=f"Identify 2-4 top attractions per day for a {days}-day trip to {destination} based on preferences.",
            backstory=(
                "You are a seasoned global travel guide. You use web search to find the "
                "You find the best tourist spots matching traveler preferences concisely and efficiently."
            ),
            tools=[search_tool],
            llm=LLM_MODEL,
            verbose=False,
            max_retry_limit=3
        )

        # 2. Flight & Accommodation Agent
        flight_agent = Agent(
            role="Travel Cost Specialist",
            goal=(
                f"Find real-time flight estimates (round-trip from India) and average daily living costs in INR for {destination}."
            ),
            backstory=(
                "You are a travel finance specialist who uses web searches to find the best flight routes "
                "You find best flight routes and daily expenses (hotel+food). You provide quick estimates in INR."
            ),
            tools=[search_tool],
            llm=LLM_MODEL,
            verbose=False,
            max_retry_limit=3
        )

        # 3. Planner Agent
        planner_agent = Agent(
            role="Itinerary Coordinator",
            goal=f"Create a logically ordered, day-by-day itinerary for a {days}-day trip to {destination}.",
            backstory=(
                "You are a meticulous trip planner. You take lists of places and distribute "
                "them evenly across the available days to create a relaxing and enjoyable itinerary."
            ),
            llm=LLM_MODEL,
            verbose=False,
            max_retry_limit=3
        )

        # 4. Budget Agent
        budget_agent = Agent(
            role="Financial Advisor",
            goal="Calculate total costs based on daily expenses and flights, and evaluate if it fits the user's budget.",
            backstory=(
                "You are an expert at travel budgeting. You calculate expected daily costs, "
                "add flight estimates, and determine if the trip is financially feasible."
            ),
            llm=LLM_MODEL,
            verbose=False,
            max_retry_limit=3
        )

        # ── Tasks ──────────────────────────────────────────────────────────────

        task1 = Task(
            description=(
                f"Search the web for the best places to visit in {destination}. "
                f"The user prefers: {', '.join(preferences) if preferences else 'general popular attractions'}. "
                f"Find enough places to fill a {days}-day trip (about 2-4 places per day). "
                "Return a clean, curated list of actual place names and a very brief description for each."
            ),
            expected_output="A list of strictly selected places to visit matching preferences.",
            agent=recommendation_agent
        )

        task2 = Task(
            description=(
                f"Search costs to {destination}. Find TWO things in INR: "
                f"1. Est. round-trip flight from major Indian city. "
                f"2. Est. daily living cost (hotel, food, transport). "
                "Summarize in one short paragraph with explicit INR numbers."
            ),
            expected_output="Short paragraph with flight cost and daily cost in INR.",
            agent=flight_agent
        )

        task3 = Task(
            description=(
                f"Create a day-by-day itinerary for a {days}-day trip to {destination}. "
                "Use the specific places selected by the Local Travel Expert from the first task. "
                "Group the places logically into days (e.g., 'Day 1', 'Day 2')."
            ),
            expected_output=f"A day-wise itinerary for {days} days. Clear division of places per day.",
            agent=planner_agent
        )

        task4 = Task(
            description=(
                f"Calculate the total trip cost to {destination} for {days} days. "
                f"Budget: ₹{budget}. Preferences: {preferences}. "
                "Extract daily cost INR and flight cost INR from Task 2. "
                "Total = flight + (daily * days). Surplus = budget - total. "
                "Return raw JSON format ONLY (NO markdown fences). Keys required: "
                "\"destination\", \"budget\", \"days\", \"preferences\", "
                "\"places\", \"itinerary\" (list of {'label': 'Day 1', 'places': [...]}), "
                "\"total_cost\", \"avg_cost_per_day\", \"budget_status\" ('Within Budget'/'Exceeded Budget'), "
                "\"budget_tip\", \"surplus\", \"surplus_label\", \"flight_details\"."
            ),
            expected_output="Valid JSON string matching the required schema.",
            agent=budget_agent
        )

        crew = Crew(
            agents=[recommendation_agent, flight_agent, planner_agent, budget_agent],
            tasks=[task1, task2, task3, task4],
            process=Process.sequential,
            verbose=False,
            max_rpm=4  # ~4 req/min keeps us well under Gemini free-tier limit
        )

        # ── Kickoff ────────────────────────────────────────────────────────────
        raw_json = "None"
        try:
            result_output = crew.kickoff()
            raw_json = str(result_output)

            # Strip markdown fences if the LLM wrapped the JSON anyway
            raw_json = re.sub(r'```(?:json)?\s*', '', raw_json)
            raw_json = re.sub(r'```\s*$', '', raw_json).strip()

            # Find the outermost JSON object
            match = re.search(r'\{.*\}', raw_json, re.DOTALL)
            if match:
                clean_json = match.group(0)
            else:
                clean_json = raw_json

            output_dict = json.loads(clean_json)
            output_dict["success"] = True

            # Fallback: build surplus_label if missing
            if "surplus_label" not in output_dict:
                surp = output_dict.get("surplus", 0)
                output_dict["surplus_label"] = (
                    f"₹{abs(surp):,} {'remaining' if surp >= 0 else 'over budget'}"
                )

            # Normalise destination to title-case
            output_dict["destination"] = str(
                output_dict.get("destination", destination)
            ).title()

            return output_dict

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "quota" in err_msg.lower() or "rate limit" in err_msg.lower():
                clean_error = "AI API Rate Limit hit. Please wait a moment and try again."
            elif "404" in err_msg or "not found" in err_msg.lower():
                clean_error = f"Model not found: {LLM_MODEL}. Check your API key has access to this model."
            elif "401" in err_msg or "api key" in err_msg.lower() or "authentication" in err_msg.lower():
                clean_error = "Invalid or missing API key. Check your GOOGLE_API_KEY / GEMINI_API_KEY."
            else:
                # Show the real error so it is visible during debugging
                clean_error = f"Error: {err_msg}"

            return {
                "success": False,
                "error": clean_error
            }

    def run(self) -> None:
        """Run in interactive CLI mode."""
        print("CLI Mode is currently under construction for CrewAI. Please run the web app.")
