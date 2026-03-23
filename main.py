"""
main.py
--------
Entry point for the Multi-Agent Trip Planner system.

Run with:
    python main.py
"""

import sys
import os
import warnings

# Suppress Pydantic and LangChain deprecation warnings from cluttering CLI
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Make sure project root is on sys.path so relative imports work regardless
# of where the script is invoked from.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from trip_planner_system import TripPlannerSystem


def main() -> None:
    """Bootstrap and execute the trip planner."""
    system = TripPlannerSystem()
    try:
        system.run()
    except KeyboardInterrupt:
        print("\n\n  ⛔  Session interrupted by user. Goodbye!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
