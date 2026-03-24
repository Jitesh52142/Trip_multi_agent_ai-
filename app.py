"""
app.py
------
Flask web server for the Multi-Agent Trip Planner.

Routes
------
GET  /          → Landing page with the trip form
POST /plan      → Run the agent pipeline, redirect to results
GET  /result    → Display the structured trip plan
GET  /api/destinations  → JSON list of supported destinations
"""
from __future__ import annotations

import os
import sys
import warnings

# Suppress Pydantic and LangChain deprecation warnings
warnings.filterwarnings("ignore")

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "trip-planner-secret-2026")

# ── Lazy singletons ──────────────────────────────────────────────────────────
# We defer heavy imports until the first request so Vercel can import this
# module successfully even before packages finish installing.
_system = None
_rec_tool = None


def _get_system():
    """Return (and lazily create) the TripPlannerSystem singleton."""
    global _system
    if _system is None:
        from trip_planner_system import TripPlannerSystem
        _system = TripPlannerSystem()
    return _system


# --------------------------------------------------------------------
# Landing / form page
# --------------------------------------------------------------------

@app.route("/")
def index():
    """Render the trip planning form."""
    return render_template("index.html")


# --------------------------------------------------------------------
# Plan submission
# --------------------------------------------------------------------

@app.route("/plan", methods=["GET", "POST"])
def plan():
    """Collect form data, run the agent pipeline, and return the result."""
    if request.method == "GET":
        return redirect(url_for("index"))
    destination = request.form.get("destination", "").strip()
    budget_raw  = request.form.get("budget", "0").strip()
    days_raw    = request.form.get("days", "0").strip()
    prefs_raw   = request.form.get("preferences", "").strip()

    # Basic server-side validation
    errors = []
    try:
        budget = int(budget_raw)
        if budget <= 0:
            errors.append("Budget must be a positive number.")
    except ValueError:
        budget = 0
        errors.append("Budget must be a whole number.")

    try:
        days = int(days_raw)
        if days <= 0:
            errors.append("Duration must be at least 1 day.")
    except ValueError:
        days = 0
        errors.append("Duration must be a whole number.")

    if not destination:
        errors.append("Please select a destination.")

    if errors:
        return render_template(
            "index.html", errors=errors,
            prev={"destination": destination, "budget": budget_raw,
                  "days": days_raw, "preferences": prefs_raw}
        )

    preferences = [p.strip() for p in prefs_raw.split(",") if p.strip()] if prefs_raw else []

    # Run the agent pipeline
    try:
        result = _get_system().run_with_data(
            destination=destination,
            budget=budget,
            days=days,
            preferences=preferences,
        )
    except Exception as exc:
        return render_template(
            "index.html",
            errors=[f"Internal error: {exc}"],
            prev={"destination": destination, "budget": budget_raw,
                  "days": days_raw, "preferences": prefs_raw}
        )

    if not result.get("success"):
        return render_template(
            "index.html",
            errors=[result.get("error", "An unknown error occurred.")],
            prev={"destination": destination, "budget": budget_raw,
                  "days": days_raw, "preferences": prefs_raw}
        )

    # Render the result directly instead of using session (avoids 4KB cookie limit)
    return render_template("result.html", trip=result)


# --------------------------------------------------------------------
# Results page
# --------------------------------------------------------------------

@app.route("/result")
def result():
    """Display the trip plan result."""
    trip = session.get("trip_result")
    if not trip:
        return redirect(url_for("index"))
    return render_template("result.html", trip=trip)


# --------------------------------------------------------------------
# API – destinations list (for dynamic UI / future use)
# --------------------------------------------------------------------

@app.route("/api/destinations")
def api_destinations():
    """Return supported destinations as JSON."""
    return jsonify({
        "destinations": [] # Dynamic input now supported
    })


# --------------------------------------------------------------------
# Health-check (useful for Vercel cold-start debugging)
# --------------------------------------------------------------------

@app.route("/health")
def health():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "service": "trip-planner"})


# --------------------------------------------------------------------
# Run
# --------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=bool(os.getenv("FLASK_DEBUG", "1")), port=5000)
