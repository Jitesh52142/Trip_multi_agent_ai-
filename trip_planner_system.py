"""
trip_planner_system.py
-----------------------
Orchestrator for the multi-agent Trip Planner system.

Supports two modes:
  1. CLI mode  → python main.py  (UserAgent prompts for input)
  2. Web mode  → called by Flask with data dict (skips UserAgent prompts)
"""

import sys
from typing import Any, NamedTuple

from memory import SharedMemory
from agents import (
    UserAgent,
    RecommendationAgent,
    PlannerAgent,
    BudgetAgent,
)
from tools import ItineraryTool


class StageResult(NamedTuple):
    agent_name: str
    success: bool
    message: str


class TripPlannerSystem:
    """
    Orchestrates the full trip-planning multi-agent pipeline.

    Usage — CLI
    -----------
    >>> system = TripPlannerSystem()
    >>> system.run()

    Usage — Web / programmatic
    --------------------------
    >>> system = TripPlannerSystem()
    >>> result = system.run_with_data(
    ...     destination="Goa", budget=12000, days=3,
    ...     preferences=["beach", "fort"]
    ... )
    """

    _BANNER_WIDTH = 62
    _SEPARATOR    = "─" * 62

    def __init__(self) -> None:
        self._memory   = SharedMemory()
        self._fmt_tool = ItineraryTool()

        self._user_agent   = UserAgent()
        self._rec_agent    = RecommendationAgent()
        self._plan_agent   = PlannerAgent()
        self._budget_agent = BudgetAgent()

    # ------------------------------------------------------------------
    # Web / programmatic entry point
    # ------------------------------------------------------------------

    def run_with_data(
        self,
        destination: str,
        budget: int,
        days: int,
        preferences: list[str],
    ) -> dict[str, Any]:
        """
        Run the full pipeline without interactive input.

        Called by the Flask route handler.  Returns a structured result
        dict that the template can render directly.

        Parameters
        ----------
        destination : str
        budget      : int  (INR)
        days        : int
        preferences : list[str]

        Returns
        -------
        dict with keys: success, error, destination, budget, days,
        preferences, places, itinerary, total_cost, avg_cost_per_day,
        budget_status, surplus, surplus_label
        """
        # Reset shared memory for each fresh request
        self._memory.reset()

        # Pre-populate shared memory (bypasses UserAgent interactive mode)
        self._memory.set("destination", destination.title().strip())
        self._memory.set("budget", budget)
        self._memory.set("days", days)
        self._memory.set("preferences", [p.strip().lower() for p in preferences if p.strip()])

        # Run the remaining three agents
        pipeline = [
            (self._rec_agent,    "Fetching recommendations…"),
            (self._plan_agent,   "Building itinerary…"),
            (self._budget_agent, "Calculating budget…"),
        ]

        for agent, _ in pipeline:
            ok = agent.run()
            if not ok:
                errors = self._memory.get("errors", [])
                return {
                    "success": False,
                    "error": "; ".join(errors) if errors else f"{agent.name} failed.",
                }

        return self._build_result_dict()

    # ------------------------------------------------------------------
    # CLI entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run in interactive CLI mode."""
        self._print_header()
        self._memory.reset()
        self._execute_pipeline_cli()

        if self._memory.has_errors():
            self._print_errors()
            return

        self._render_cli_output()

    # ------------------------------------------------------------------
    # CLI helpers
    # ------------------------------------------------------------------

    def _execute_pipeline_cli(self) -> None:
        pipeline = [
            (self._user_agent,   "Collecting user preferences…"),
            (self._rec_agent,    "Fetching place recommendations…"),
            (self._plan_agent,   "Building day-wise itinerary…"),
            (self._budget_agent, "Calculating budget and costs…"),
        ]
        for agent, description in pipeline:
            print(f"\n  ⚙  {description}")
            success = agent.run()
            if not success:
                print(f"\n  ❌  {agent.name} failed. Halting pipeline.")
                break
            print(f"  ✅  {agent.name} completed.")

    def _render_cli_output(self) -> None:
        r = self._build_result_dict()
        sep = self._SEPARATOR
        print(f"\n  {'=' * self._BANNER_WIDTH}")
        print(f"  {'🧳  TRIP PLAN SUMMARY':^{self._BANNER_WIDTH}}")
        print(f"  {'=' * self._BANNER_WIDTH}")
        print(f"\n  {'📍 Destination':<22}: {r['destination']}")
        print(f"  {'🗓  Duration':<22}: {r['days']} day(s)")
        print(f"  {'💰 Your Budget':<22}: ₹{r['budget']:,}")
        prefs = ", ".join(r["preferences"]) if r["preferences"] else "None"
        print(f"  {'🎯 Preferences':<22}: {prefs}")
        print(f"\n  {sep}")
        print(f"  🗺  RECOMMENDED PLACES ({len(r['places'])} total)")
        print(f"  {sep}")
        for i, p in enumerate(r["places"], 1):
            print(f"    {i:>2}. {p}")
        print(f"\n  {sep}")
        print(f"  📅  DAY-WISE ITINERARY")
        print(f"  {sep}")
        for entry in r["itinerary"]:
            arrow = "  →  ".join(entry["places"])
            print(f"    {entry['label']:>6}: {arrow}")
        print(f"\n  {sep}")
        print(f"  💳  BUDGET SUMMARY")
        print(f"  {sep}")
        print(f"  {'Avg Cost / Day':<22}: ₹{r['avg_cost_per_day']:,}")
        print(f"  {'Estimated Cost':<22}: ₹{r['total_cost']:,}")
        print(f"  {'Your Budget':<22}: ₹{r['budget']:,}")
        icon = "✅" if r["budget_status"] == "Within Budget" else "⚠️ "
        print(f"\n  {icon}  {r['budget_status']}")
        print(f"\n  {'=' * self._BANNER_WIDTH}\n")

    def _print_header(self) -> None:
        print(f"\n  {'=' * self._BANNER_WIDTH}")
        print(f"  {'🌐  MULTI-AGENT TRIP PLANNER':^{self._BANNER_WIDTH}}")
        print(f"  {'=' * self._BANNER_WIDTH}\n")

    def _print_errors(self) -> None:
        errors = self._memory.get("errors", [])
        print(f"\n  {'─' * self._BANNER_WIDTH}")
        print(f"  ❌  ERRORS")
        for err in errors:
            print(f"    • {err}")
        print()

    # ------------------------------------------------------------------
    # Shared result builder
    # ------------------------------------------------------------------

    def _build_result_dict(self) -> dict[str, Any]:
        """Convert current shared memory into a clean result dict."""
        mem = self._memory
        budget     = mem.get("budget", 0)
        total_cost = mem.get("total_cost", 0)
        surplus    = budget - total_cost
        surplus_label = (
            f"₹{abs(surplus):,} {'remaining' if surplus >= 0 else 'over budget'}"
        )

        return {
            "success":          True,
            "destination":      mem.get("destination", ""),
            "budget":           budget,
            "days":             mem.get("days", 0),
            "preferences":      mem.get("preferences", []),
            "places":           mem.get("places", []),
            "itinerary":        mem.get("itinerary", []),
            "total_cost":       total_cost,
            "avg_cost_per_day": mem.get("avg_cost_per_day", 0),
            "budget_status":    mem.get("budget_status", ""),
            "budget_tip":       mem.get("budget_tip", ""),
            "surplus":          surplus,
            "surplus_label":    surplus_label,
        }
