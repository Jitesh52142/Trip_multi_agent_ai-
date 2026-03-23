"""
tools/budget_tool.py
---------------------
Computes the estimated trip cost and validates it against the user's budget.

Keeping budget logic here (not in BudgetAgent) makes it independently
testable and reusable in future extensions.
"""


class BudgetTool:
    """
    Performs all budget-related calculations for a trip.

    Methods are intentionally stateless (pure functions wrapped in a class)
    so they can be used without maintaining instance state.
    """

    # ------------------------------------------------------------------
    # Cost calculation
    # ------------------------------------------------------------------

    def compute_total_cost(self, avg_cost_per_day: int, days: int) -> int:
        """
        Compute the estimated total trip cost.

        Parameters
        ----------
        avg_cost_per_day:
            Average cost per day in INR for the chosen destination.
        days:
            Number of travel days.

        Returns
        -------
        int
            Estimated total cost (INR).

        Raises
        ------
        ValueError
            If *avg_cost_per_day* or *days* are non-positive.
        """
        if avg_cost_per_day <= 0:
            raise ValueError("avg_cost_per_day must be a positive integer.")
        if days <= 0:
            raise ValueError("days must be a positive integer.")

        return avg_cost_per_day * days

    # ------------------------------------------------------------------
    # Budget validation
    # ------------------------------------------------------------------

    def validate_budget(self, total_cost: int, budget: int) -> dict:
        """
        Compare estimated cost against the user's declared budget.

        Parameters
        ----------
        total_cost:
            Estimated trip cost (INR).
        budget:
            User-declared budget (INR).

        Returns
        -------
        dict with keys:
            - ``status``  : "Within Budget" | "Exceeded Budget"
            - ``surplus`` : remaining money (negative if exceeded)
            - ``message`` : human-readable summary
        """
        surplus = budget - total_cost
        if surplus >= 0:
            status = "Within Budget"
            message = (
                f"Great news! Your trip fits within budget. "
                f"You have ₹{surplus:,} to spare."
            )
        else:
            status = "Exceeded Budget"
            message = (
                f"Budget exceeded by ₹{abs(surplus):,}. "
                f"Consider reducing the number of days or choosing a "
                f"more economical destination."
            )

        return {
            "status": status,
            "surplus": surplus,
            "message": message,
        }

    # ------------------------------------------------------------------
    # Minimum budget check
    # ------------------------------------------------------------------

    def is_budget_feasible(self, avg_cost_per_day: int, budget: int) -> bool:
        """
        Return True if the budget covers at least one day of travel.

        Parameters
        ----------
        avg_cost_per_day:
            Average cost per day for the destination.
        budget:
            User's declared budget.
        """
        return budget >= avg_cost_per_day
