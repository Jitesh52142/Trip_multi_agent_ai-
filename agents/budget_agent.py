"""
agents/budget_agent.py
-----------------------
Calculates the estimated cost + validates budget.
Uses LLM to provide a final friendly, human-like budget suggestion message.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from agents.base_agent import BaseAgent
from tools import BudgetTool

class BudgetOutput(BaseModel):
    summary_message: str = Field(description="A short, fun summary advising the user about their trip budget.")

class BudgetAgent(BaseAgent):
    """
    Estimates trip cost and checks budget using math, plus a Gemini review message.
    """

    def __init__(self) -> None:
        super().__init__(
            name="BudgetAgent",
            role="Calculate trip cost and provide an LLM-driven budget summary",
        )
        self._tool = BudgetTool()
        try:
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
            self.structured_llm = self.llm.with_structured_output(BudgetOutput)
        except Exception as e:
            self.structured_llm = None
            self.logger.warning(f"Failed to init LLM: {e}")

    def run(self) -> bool:
        self._log_start()

        avg_cost_per_day: int = self.memory.get("avg_cost_per_day", 0)
        days: int = self.memory.get("days", 0)
        budget: int = self.memory.get("budget", 0)
        destination: str = self.memory.get("destination", "Unknown")

        if avg_cost_per_day <= 0 or days <= 0 or budget <= 0:
            self._log_error("Invalid budget factors (days/budget/cost=0).")
            return False

        if not self._tool.is_budget_feasible(avg_cost_per_day, budget):
            self._log_error(f"Budget ₹{budget:,} is too low for ₹{avg_cost_per_day:,}/day.")
            return False

        try:
            total_cost = self._tool.compute_total_cost(avg_cost_per_day, days)
            result = self._tool.validate_budget(total_cost, budget)
        except ValueError as exc:
            self._log_error(str(exc))
            return False

        # Add LLM flair
        summary_message = result["message"]
        if self.structured_llm:
            prompt = (
                f"User is traveling to {destination} for {days} days on a ₹{budget} budget.\n"
                f"The estimated cost is ₹{total_cost}.\n"
                f"Status: {result['status']} (Surplus/Deficit: ₹{result['surplus']}).\n\n"
                f"Write a cheerful 2-sentence summary tip for this budget."
            )
            try:
                res = self.structured_llm.invoke(prompt)
                summary_message = res.summary_message
            except Exception as e:
                self.logger.error(f"LLM Summary Error: {e}")

        self._store_local("total_cost", total_cost)
        self._store_local("budget_status", result["status"])
        
        self.memory.set("total_cost", total_cost)
        self.memory.set("budget_status", result["status"])
        # We can also store the LLM message if we want, but letting the UI calculate surplus was the original plan
        self.memory.set("budget_tip", summary_message)

        self._log_success(f"Cost: ₹{total_cost:,} | Status: {result['status']}")
        return True
