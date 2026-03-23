"""
agents/recommendation_agent.py
--------------------------------
Fetches places from the local dummy JSON, then uses Langchain and
Gemini to smartly filter them based on user preferences.
"""

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from agents.base_agent import BaseAgent
from tools import RecommendationTool

class PlacesOutput(BaseModel):
    places: list[str] = Field(description="List of selected place names")

class RecommendationAgent(BaseAgent):
    """
    Recommends places to visit using an LLM to apply preferences smartly.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RecommendationAgent",
            role="Suggest places to visit based on destination and preferences via LLM",
        )
        self._tool = RecommendationTool()
        try:
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
            self.structured_llm = self.llm.with_structured_output(PlacesOutput)
        except Exception as e:
            self.structured_llm = None
            self.logger.warning(f"Failed to init LLM: {e}")

    def run(self) -> bool:
        self._log_start()

        destination: str = self.memory.get("destination", "")
        preferences: list[str] = self.memory.get("preferences", [])

        if not destination or not self._tool.is_valid_destination(destination):
            self._log_error(f"Destination '{destination}' is not valid.")
            return False

        try:
            all_places = self._tool.get_places(destination)
            avg_cost = self._tool.get_avg_cost_per_day(destination)
        except ValueError as exc:
            self._log_error(str(exc))
            return False

        if self.structured_llm:
            prompt = (
                f"You are a Trip Planner AI.\n"
                f"Destination: {destination}\n"
                f"Available Places: {all_places}\n"
                f"User Preferences: {preferences}\n\n"
                f"Select the most appropriate places that match the preferences. Provide at least 1-2 places, or return all if preferences are empty or don't strongly match."
            )
            try:
                res = self.structured_llm.invoke(prompt)
                recommended = res.places if res.places else all_places
            except Exception as e:
                self.logger.error(f"LLM Error: {e}")
                recommended = self._tool.filter_places_by_preferences(all_places, preferences)
        else:
            recommended = self._tool.filter_places_by_preferences(all_places, preferences)

        if not recommended:
            self._log_error("No places available after filtering.")
            return False

        self._store_local("places", recommended)
        self._store_local("avg_cost_per_day", avg_cost)

        self.memory.set("places", recommended)
        self.memory.set("avg_cost_per_day", avg_cost)

        self._log_success(
            f"{len(recommended)} place(s) recommended for {destination}. "
            f"Avg cost/day: ₹{avg_cost:,}"
        )
        return True
