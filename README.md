# 🌐 Multi-Agent Trip Planner

A production-style **multi-agent system** built in **pure Python** (no AI frameworks). Demonstrates real agent architecture with role separation, shared memory, and a dedicated tools layer — fully ready to migrate to CrewAI.

---

## 📁 Project Structure

```
multiagentic/
├── main.py                        # Entry point
├── trip_planner_system.py         # Orchestrator (TripPlannerSystem)
│
├── agents/
│   ├── base_agent.py              # Abstract BaseAgent
│   ├── user_agent.py              # Collects & validates user input
│   ├── recommendation_agent.py   # Recommends places
│   ├── planner_agent.py           # Builds day-wise itinerary
│   └── budget_agent.py            # Calculates cost & validates budget
│
├── tools/
│   ├── recommendation_tool.py     # Fetches data from JSON dataset
│   ├── budget_tool.py             # Cost computation & budget checks
│   └── itinerary_tool.py          # Distributes places across days
│
├── memory/
│   └── shared_memory.py           # Singleton shared state store
│
└── data/
    └── destinations.json          # Local dummy dataset
```

---

## 🚀 How to Run

```bash
python main.py
```

No external dependencies — uses only the Python standard library.

---

## 🏗️ Agent Pipeline

```
UserAgent → RecommendationAgent → PlannerAgent → BudgetAgent
    ↕               ↕                  ↕              ↕
              [ SharedMemory — global state dictionary ]
```

| Agent | Reads | Writes |
|---|---|---|
| `UserAgent` | — | destination, budget, days, preferences |
| `RecommendationAgent` | destination, preferences | places, avg_cost_per_day |
| `PlannerAgent` | places, days | itinerary |
| `BudgetAgent` | avg_cost_per_day, days, budget | total_cost, budget_status |

---

## 🧰 Tools

| Tool | Purpose |
|---|---|
| `RecommendationTool` | Loads JSON dataset, validates destination, filters places |
| `BudgetTool` | Computes total cost, validates budget, feasibility check |
| `ItineraryTool` | Distributes places evenly across days (cycles if needed) |

---

## 🗺️ Supported Destinations

| Destination | Avg Cost/Day |
|---|---|
| Goa | ₹3,000 |
| Manali | ₹2,500 |
| Jaipur | ₹2,000 |
| Kerala | ₹3,500 |
| Ladakh | ₹4,000 |

---

## 📊 Sample Output

```
  ══════════════════════════════════════════════════════════════
       🧳  TRIP PLAN SUMMARY
  ══════════════════════════════════════════════════════════════

  📍 Destination         : Goa
  🗓  Duration            : 3 day(s)
  💰 Your Budget          : ₹12,000
  🎯 Preferences          : beach

  ──────────────────────────────────────────────────────────────
  🗺  RECOMMENDED PLACES (2 total)
  ──────────────────────────────────────────────────────────────
     1. Baga Beach
     2. Calangute Beach

  ──────────────────────────────────────────────────────────────
  📅  DAY-WISE ITINERARY
  ──────────────────────────────────────────────────────────────
    Day 1 :  Baga Beach  →  Calangute Beach  →  Anjuna Beach
    Day 2 :  Fort Aguada  →  Baga Beach  →  Calangute Beach
    Day 3 :  Anjuna Beach  →  Fort Aguada

  ──────────────────────────────────────────────────────────────
  💳  BUDGET SUMMARY
  ──────────────────────────────────────────────────────────────
  Avg Cost / Day         : ₹3,000
  Total Days             : 3
  Estimated Cost         : ₹9,000
  Your Budget            : ₹12,000
  Difference             : ₹3,000 remaining

  ✅  Budget Status  :  Within Budget
```

---

## 🔮 Future Extension to CrewAI

Each Python class maps directly to a CrewAI concept:

| This project | CrewAI equivalent |
|---|---|
| `BaseAgent` subclass | `crewai.Agent` |
| `run()` method | Agent's `goal` + `backstory` |
| Tool class | `crewai.Tool` or `@tool` decorator |
| `SharedMemory` | CrewAI shared memory / context |
| `TripPlannerSystem` | `crewai.Crew` with `Process.sequential` |
