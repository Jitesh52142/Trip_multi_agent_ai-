"""
tools/itinerary_tool.py
------------------------
Distributes places across trip days to produce a structured itinerary.

The tool is intentionally destination-agnostic — it only needs a list of
places and a day count, so it remains reusable across agents.
"""

import math


class ItineraryTool:
    """
    Generates a day-wise itinerary by distributing *places* evenly
    across the given number of *days*.
    """

    # Maximum places to visit per day (keeps the itinerary realistic)
    MAX_PLACES_PER_DAY: int = 3

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def build_itinerary(
        self,
        places: list[str],
        days: int,
        destination: str = "",
    ) -> list[dict]:
        """
        Distribute *places* across *days* and return a structured itinerary.

        Parameters
        ----------
        places:
            Ordered list of places to visit.
        days:
            Total number of travel days.
        destination:
            Optional destination name used for labelling.

        Returns
        -------
        list[dict]
            Each element represents one day::

                {
                    "day": 1,
                    "label": "Day 1",
                    "places": ["Place A", "Place B"]
                }

        Raises
        ------
        ValueError
            If *places* is empty or *days* is non-positive.
        """
        if not places:
            raise ValueError("At least one place is required to build an itinerary.")
        if days <= 0:
            raise ValueError("days must be a positive integer.")

        # Cap places to MAX_PLACES_PER_DAY × days
        capped_places = self._cap_places(places, days)
        chunks = self._split_into_chunks(capped_places, days)

        itinerary: list[dict] = []
        for day_num, day_places in enumerate(chunks, start=1):
            itinerary.append(
                {
                    "day": day_num,
                    "label": f"Day {day_num}",
                    "places": day_places,
                }
            )

        return itinerary

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _cap_places(self, places: list, days: int) -> list:
        """
        Return at most ``MAX_PLACES_PER_DAY × days`` places.
        If fewer places are available they are cycled to fill the days.
        """
        max_places = self.MAX_PLACES_PER_DAY * days
        if len(places) >= max_places:
            return list(places[:max_places])

        # Cycle places to ensure every day has at least one entry
        cycled: list = []
        while len(cycled) < max_places:
            cycled.extend(places)
        return list(cycled[:max_places])

    def _split_into_chunks(
        self, places: list, days: int
    ) -> list:
        """
        Split *places* into *days* chunks as evenly as possible.

        Example: 5 places, 3 days → [2, 2, 1]
        """
        chunk_size = math.ceil(len(places) / days)
        return [
            list(places[i : i + chunk_size])
            for i in range(0, len(places), chunk_size)
        ][:days]

    # ------------------------------------------------------------------
    # Formatting helper
    # ------------------------------------------------------------------

    def format_itinerary(self, itinerary: list[dict]) -> str:
        """
        Return a human-readable multi-line string of the itinerary.

        Parameters
        ----------
        itinerary:
            Output produced by :meth:`build_itinerary`.
        """
        lines: list[str] = []
        for entry in itinerary:
            places_str = ", ".join(entry["places"])
            lines.append(f"  {entry['label']}: {places_str}")
        return "\n".join(lines)
