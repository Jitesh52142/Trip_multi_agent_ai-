"""
agents/user_agent.py
---------------------
Collects and validates user input, then writes it to shared memory.

Responsibility (single):
  Ask the user for destination, budget, duration, and preferences
  then commit clean, validated values to shared memory.
"""

from agents.base_agent import BaseAgent
from tools import RecommendationTool


class UserAgent(BaseAgent):
    """
    Interacts with the end-user via the terminal to gather trip details.

    Writes to shared memory:
        - destination   (str)
        - budget        (int, INR)
        - days          (int)
        - preferences   (list[str])
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserAgent",
            role="Collect and validate trip requirements from the user",
        )
        self._rec_tool = RecommendationTool()

    # ------------------------------------------------------------------
    # BaseAgent interface
    # ------------------------------------------------------------------

    def run(self) -> bool:
        """
        Prompt the user for input, validate each field, and write to
        shared memory.

        Returns
        -------
        bool
            True if all inputs are valid and stored; False otherwise.
        """
        self._log_start()

        # 1. Destination
        destination = self._collect_destination()
        if destination is None:
            return False
        self._store_local("destination", destination)

        # 2. Budget
        budget = self._collect_budget()
        if budget is None:
            return False
        self._store_local("budget", budget)

        # 3. Duration (days)
        days = self._collect_days()
        if days is None:
            return False
        self._store_local("days", days)

        # 4. Preferences (optional)
        preferences = self._collect_preferences()
        self._store_local("preferences", preferences)

        # Commit to shared memory
        self.memory.set("destination", destination)
        self.memory.set("budget", budget)
        self.memory.set("days", days)
        self.memory.set("preferences", preferences)

        self._log_success(
            f"destination={destination}, budget=₹{budget:,}, "
            f"days={days}, preferences={preferences}"
        )
        return True

    # ------------------------------------------------------------------
    # Private collection helpers
    # ------------------------------------------------------------------

    def _collect_destination(self) -> str | None:
        """
        Prompt for destination and validate against the dataset.

        Returns the canonical (title-cased) destination name or None
        on repeated failure.
        """
        supported = self._rec_tool.get_supported_destinations()
        supported_display = ", ".join(supported)

        for attempt in range(3):
            raw = input(
                f"\n🌍 Enter destination [{supported_display}]: "
            ).strip()
            if self._rec_tool.is_valid_destination(raw):
                return raw.title()
            print(
                f"  ⚠️  '{raw}' is not supported. "
                f"Choose from: {supported_display}"
            )

        self._log_error(
            "Destination input failed after 3 attempts."
        )
        return None

    def _collect_budget(self) -> int | None:
        """
        Prompt for budget and ensure it is a positive integer.

        Returns the budget (INR) or None on repeated failure.
        """
        for attempt in range(3):
            raw = input("\n💰 Enter your total budget in INR (e.g. 10000): ").strip()
            try:
                budget = int(raw)
                if budget > 0:
                    return budget
                print("  ⚠️  Budget must be greater than zero.")
            except ValueError:
                print(f"  ⚠️  '{raw}' is not a valid number. Please enter a whole number.")

        self._log_error("Budget input failed after 3 attempts.")
        return None

    def _collect_days(self) -> int | None:
        """
        Prompt for trip duration and ensure it is a positive integer.

        Returns the number of days or None on repeated failure.
        """
        for attempt in range(3):
            raw = input("\n📅 Enter number of days (e.g. 3): ").strip()
            try:
                days = int(raw)
                if days > 0:
                    return days
                print("  ⚠️  Duration must be at least 1 day.")
            except ValueError:
                print(f"  ⚠️  '{raw}' is not valid. Please enter a whole number.")

        self._log_error("Days input failed after 3 attempts.")
        return None

    def _collect_preferences(self) -> list[str]:
        """
        Prompt for optional preference keywords.

        Returns a (possibly empty) list of lowercase keyword strings.
        """
        raw = input(
            "\n🎯 Enter preferences (comma-separated, or press Enter to skip)\n"
            "   e.g. beach, fort, temple, adventure, nature: "
        ).strip()

        if not raw:
            return []

        return [kw.strip().lower() for kw in raw.split(",") if kw.strip()]
