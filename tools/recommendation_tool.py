"""
tools/recommendation_tool.py
-----------------------------
Fetches destination data from the local JSON dataset.

Agents must call this tool instead of embedding data-access logic directly.
This keeps agents thin and tools reusable (e.g. swap JSON → API later).
"""

import json
import os
from typing import Optional


class RecommendationTool:
    """
    Loads destination data from *destinations.json* and exposes
    query helpers used by RecommendationAgent.
    """

    # Path to the JSON dataset relative to the project root
    _DATA_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "destinations.json"
    )

    def __init__(self) -> None:
        self._data: dict = self._load_data()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_data(self) -> dict:
        """Load and return the destinations JSON file."""
        path = os.path.abspath(self._DATA_PATH)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Destination dataset not found at: {path}"
            )
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_supported_destinations(self) -> list[str]:
        """Return a sorted list of all supported destination names."""
        return sorted(self._data.keys())

    def is_valid_destination(self, destination: str) -> bool:
        """Return True if *destination* exists in the dataset."""
        return destination.title() in self._data

    def get_places(self, destination: str) -> list[str]:
        """
        Return the list of places for *destination*.

        Raises
        ------
        ValueError
            If *destination* is not in the dataset.
        """
        key = destination.title()
        if key not in self._data:
            raise ValueError(
                f"Destination '{destination}' not found. "
                f"Supported: {self.get_supported_destinations()}"
            )
        return list(self._data[key]["places"])

    def get_avg_cost_per_day(self, destination: str) -> int:
        """
        Return the average cost per day (INR) for *destination*.

        Raises
        ------
        ValueError
            If *destination* is not in the dataset.
        """
        key = destination.title()
        if key not in self._data:
            raise ValueError(
                f"Destination '{destination}' not found."
            )
        return int(self._data[key]["avg_cost_per_day"])

    def filter_places_by_preferences(
        self,
        places: list[str],
        preferences: list[str],
    ) -> list[str]:
        """
        Apply a basic keyword filter.  If *preferences* is empty or
        none of the keywords match, the full *places* list is returned
        unchanged so the planner always has something to work with.

        Parameters
        ----------
        places:
            Full list of places for the destination.
        preferences:
            User preference keywords, e.g. ``["beach", "fort"]``.
        """
        if not preferences:
            return places

        lowered = [p.lower() for p in preferences]
        filtered = [
            place for place in places
            if any(kw in place.lower() for kw in lowered)
        ]
        # Fall back to the complete list when filter yields nothing
        return filtered if filtered else places
