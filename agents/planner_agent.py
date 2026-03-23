"""
agents/planner_agent.py
------------------------
Generates a day-wise itinerary by distributing recommended places
across the trip duration using LangChain and an LLM.
"""

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.base_agent import BaseAgent
from tools import ItineraryTool

class DayPlan(BaseModel):
    day: int = Field(description="Day number")
    label: str = Field(description="Display label, e.g., 'Day 1'")
    places: list[str] = Field(description="List of places to visit on this day from the context places")

class ItineraryOutput(BaseModel):
    itinerary: list[DayPlan]

class PlannerAgent(BaseAgent):
    """
    Creates a day-by-day travel itinerary using LangChain to smartly distribute places.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PlannerAgent",
            role="Generate a structured day-wise itinerary using Gemini LLM",
        )
        self._tool = ItineraryTool()
        try:
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
            self.structured_llm = self.llm.with_structured_output(ItineraryOutput)
        except Exception as e:
            self.structured_llm = None
            self.logger.warning(f"Failed to init LLM: {e}")

    def run(self) -> bool:
        self._log_start()

        places: list[str] = self.memory.get("places", [])
        days: int = self.memory.get("days", 0)
        destination: str = self.memory.get("destination", "Unknown")

        if not places:
            self._log_error("No places found. Ensure RecommendationAgent ran successfully.")
            return False

        if days <= 0:
            self._log_error(f"Invalid duration (days={days}).")
            return False

        prompt = (
            f"You are a local guide for {destination}.\n"
            f"Here are the places the user wants to visit: {places}\n"
            f"The trip length is {days} days.\n"
            f"Split the places across the {days} days intuitively (max 3-4 places per day)."
        )

        try:
            if self.structured_llm:
                res = self.structured_llm.invoke(prompt)
                itinerary = [day.model_dump() for day in res.itinerary]
            else:
                itinerary = self._tool.build_itinerary(places=places, days=days, destination=destination)
        except Exception as exc:
            self.logger.error(f"LLM Itinerary Error: {exc}")
            itinerary = self._tool.build_itinerary(places=places, days=days, destination=destination)

        self._store_local("itinerary", itinerary)
        self.memory.set("itinerary", itinerary)

        self._log_success(f"Itinerary built for {days} day(s).")
        return True
