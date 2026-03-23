"""
shared_memory.py
----------------
Centralized shared memory store for the multi-agent Trip Planner system.

All agents read from and write to this single shared state dictionary.
This simulates a global blackboard/memory in a real multi-agent system.
"""

from typing import Any


# ---------------------------------------------------------------------------
# Initial shared memory schema
# ---------------------------------------------------------------------------
_shared_memory: dict[str, Any] = {
    "destination": "",
    "budget": 0,
    "days": 0,
    "preferences": [],        # e.g. ["beach", "adventure", "heritage"]
    "places": [],             # populated by RecommendationAgent
    "itinerary": [],          # populated by PlannerAgent  (list of day dicts)
    "total_cost": 0,          # populated by BudgetAgent
    "avg_cost_per_day": 0,    # populated by RecommendationAgent
    "budget_status": "",      # "Within Budget" | "Exceeded Budget"
    "errors": [],             # any error messages collected during execution
}


class SharedMemory:
    """
    Singleton-style wrapper around the shared memory dictionary.

    Provides typed helpers so agents never have to import the raw dict.
    All mutating operations go through ``set()``, keeping the API clean
    and making it trivial to add logging / persistence later.
    """

    _instance: "SharedMemory | None" = None

    def __new__(cls) -> "SharedMemory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for *key* from shared memory."""
        return _shared_memory.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Write *value* to *key* in shared memory."""
        _shared_memory[key] = value

    def append(self, key: str, value: Any) -> None:
        """Append *value* to a list stored at *key*."""
        if not isinstance(_shared_memory.get(key), list):
            _shared_memory[key] = []
        _shared_memory[key].append(value)

    def add_error(self, message: str) -> None:
        """Record an error message in the errors list."""
        self.append("errors", message)

    def has_errors(self) -> bool:
        """Return True if any errors have been recorded."""
        return bool(_shared_memory.get("errors"))

    def reset(self) -> None:
        """Reset all shared memory to initial empty state."""
        _shared_memory.update({
            "destination": "",
            "budget": 0,
            "days": 0,
            "preferences": [],
            "places": [],
            "itinerary": [],
            "total_cost": 0,
            "avg_cost_per_day": 0,
            "budget_status": "",
            "errors": [],
        })

    def snapshot(self) -> dict[str, Any]:
        """Return a shallow copy of the entire shared memory state."""
        return dict(_shared_memory)

    def __repr__(self) -> str:
        return f"SharedMemory({_shared_memory!r})"
