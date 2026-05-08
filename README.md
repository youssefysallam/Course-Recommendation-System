# Course Recommendation System

A Flask web app that recommends which courses to take next semester to make the fastest progress toward a CS or CE degree at UMass Boston. It models degree requirements and prerequisites as a directed dependency graph, then applies Dijkstra's algorithm to find the shortest path to graduation.

---

## How it works

1. **Select your major** — Computer Science BA, Computer Science BS, or Computer Engineering BS
2. **Enter completed courses** — comma-separated list of courses you've already passed
3. **Mark completed Gen Eds** — check off your fulfilled general education requirements
4. **Get recommendations** — the algorithm computes which eligible courses, taken now, reduce your remaining graduation distance the most

---

## Algorithm

Requirements and prerequisites are modeled as a weighted directed acyclic graph:

```
MATH 140 ──► CS 210 ──► CS 310 ──► CS 410
                │
                └──► CS 240 ──► CS 340
```

Each node is a course requirement; edges represent prerequisites. Completed courses are removed from the graph. Dijkstra's algorithm computes shortest graduation path from the current state, and the first-semester slice of that path is returned as recommendations.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 + Flask + Flask-WTF |
| Algorithm | Dijkstra (custom graph implementation) |
| Templates | Jinja2 |
| Styling | Vanilla CSS (dark theme, no framework dependency) |
| Data | JSON degree requirement files (CS BA, CS BS, CE BS) |

---

## Project Structure

```
src/
  app.py                  Flask routes and session management
  dependency_graph.py     Directed graph from JSON requirement files
  schedule_calculator.py  Dijkstra-based semester planner
  dijkstra_algorithim.py  Core shortest-path implementation
data/requirements/
  Computer_Science_BA.json
  Computer_Science_BS.json
  Computer_Engineering_BS.json
data/
  course_catalog.csv      Full UMass Boston course catalog
  fall_2024.csv           Section availability by semester
  general_education_courses.json
static/css/styles.css     Dark design system
templates/                Jinja2 HTML templates (4-step flow)
scripts/                  Data scraping + preprocessing utilities
```

---

## Getting Started

```bash
pip install -r requirements.txt
cd src
flask run
# → http://localhost:5000
```

---

## Data

Degree requirement JSON files in `data/requirements/` were scraped from UMass Boston's degree audit pages using the scripts in `scripts/`. The course catalog and semester availability were scraped from the UMass Boston course catalog.

To update requirements, run:

```bash
python scripts/scrape_from_degree_audits.py
python scripts/scrape_from_course_catalog.py
```

---

## Key Design Decisions

**Graph over rules engine** — encoding requirements as a dependency graph lets the algorithm discover prerequisite chains automatically rather than hard-coding semester sequences per major.

**Dijkstra on the requirement graph** — gives an optimal first-semester recommendation in O((V + E) log V) regardless of how complex the requirement tree is.

**Flask-WTF CSRF** — all form submissions are protected; session stores major and completed-course selections between steps.
