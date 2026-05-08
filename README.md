# Course Recommendation System

> A full-stack academic planning tool that generates a personalized, conflict-free multi-semester degree plan for UMass Boston CS and CE students — in under a second.

Students often waste time taking courses out of order, missing prerequisites, or overloading a semester. This system models an entire degree program as a directed dependency graph, removes what the student has already completed, and produces an optimal semester-by-semester schedule that respects every prerequisite chain and credit constraint.

---

## Live Demo

Step through the 4-step wizard at **`http://localhost:5000`** after running locally (setup below).

---

## What It Does

| Step | What happens |
|---|---|
| **1 · Major** | Select CS B.S., CS B.A., or CE B.S. — loads the matching requirement graph |
| **2 · Gen Eds** | Check off completed general education categories |
| **3 · Completed courses** | Type-ahead autocomplete from the real course catalog; credit load preference (12 / 15 / 18 cr/sem) |
| **4 · Your plan** | Full multi-semester degree plan with availability badges, "why skipped" explanations, and unknown-course warnings |

### Key outputs on the results page

- **Next semester** — the immediate recommended course list
- **Full degree plan** — every remaining semester laid out in a responsive grid
- **Availability badges** — each course tagged `Fall & Spring`, `Fall only`, or `Spring only` from scraped UMass Boston enrollment data
- **Courses not yet schedulable** — any course the algorithm couldn't fit, with the exact reason (e.g. *"unmet prerequisites: CS 310"* or *"could not fit within 15-credit cap"*)
- **Unknown course warning** — flags codes the student typed that don't exist in the requirement graph

---

## How the Algorithm Works

Degree requirements are loaded from JSON into an in-memory directed graph. Each node is a course; edges represent prerequisite relationships.

```
MATH 140 ──► CS 210 ──► CS 310 ──► CS 410
                │
                └──► CS 240 ──► CS 341 ──► CS 450
```

**Processing pipeline** (runs on every request, < 100 ms):

1. **Mutual corequisite merging** — courses that must be taken together (e.g. `CS 333 + CS 334`) are collapsed into a single composite node so the scheduler treats them atomically
2. **Completed-course pruning** — removes finished courses and decrements prerequisite group counters
3. **Topological sort** (Kahn's BFS algorithm) — produces a dependency-respecting ordering of all remaining courses
4. **Greedy semester packing** — assigns courses to semesters in topological order, respecting the per-semester credit cap; unschedulable courses are recorded with their reason
5. **Availability annotation** — cross-references each recommended course against scraped Fall 2024 / Spring 2025 enrollment CSVs

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 · Flask · Flask-WTF |
| Core algorithm | Custom directed graph · Kahn's topological sort · greedy packing |
| Data pipeline | CSV / JSON parsing from scraped UMass Boston catalog |
| Templates | Jinja2 (4-step wizard) |
| Frontend | Vanilla JS autocomplete · CSS design system (dark theme, no framework) |
| Security | CSRF protection on all form submissions via Flask-WTF |

---

## Project Structure

```
src/
  app.py                  Flask routes, session management, availability annotation
  dependency_graph.py     Directed graph built from JSON requirement files
  schedule_calculator.py  Topological sort + greedy semester planner
  availability.py         Parses enrollment CSVs; caches offered-course sets per semester

data/
  requirements/
    Computer_Science_BA.json
    Computer_Science_BS.json
    Computer_Engineering_BS.json
  course_catalog.csv          Full UMass Boston course catalog (scraped)
  fall_2024.csv               Section availability — Fall 2024
  spring_2025.csv             Section availability — Spring 2025
  general_education_courses.json

static/
  css/styles.css              Dark design system (CSS variables, no framework)
  js/autocomplete.js          Live search + chip UI for course input

templates/                    Jinja2 HTML (index, select_geneds, input_courses, recommendations)

scripts/                      Data scraping + preprocessing utilities
```

---

## Getting Started

```bash
git clone https://github.com/youssefysallam/CS310-Course-Project.git
cd CS310-Course-Project

pip install -r requirements.txt

cd src
python app.py
# → http://127.0.0.1:5000
```

No database, no environment variables, no build step.

---

## Updating Degree Data

Requirement JSON files and enrollment CSVs were scraped from UMass Boston's degree audit and course catalog pages. To refresh them:

```bash
python scripts/scrape_from_degree_audits.py
python scripts/scrape_from_course_catalog.py
```

---

## Engineering Highlights

**Graph-native requirement modeling** — encoding prerequisites as a DAG lets the algorithm discover multi-hop chains automatically (e.g. CS 110 → CS 210 → CS 310 → CS 410) without any hard-coded sequences. Adding a new major requires only a JSON file.

**Topological sort over Dijkstra** — a topological ordering is the correct primitive for prerequisite-constrained scheduling: it guarantees every course appears after all its prerequisites in O(V + E), which is strictly better than Dijkstra's O((V + E) log V) for unweighted DAGs.

**Mutual corequisite detection and merging** — courses with bidirectional corequisite edges (e.g. lecture + lab pairs) are collapsed into atomic composite nodes before scheduling, preventing the planner from splitting them across semesters.

**Real enrollment data** — the availability module parses 1,500+ course sections from UMass Boston's live enrollment export, filters to unique `SUBJECT CATALOG_NBR` pairs, and caches the result in memory so it's only parsed once per server process.

**Zero-dependency core** — `dependency_graph.py` and `schedule_calculator.py` import nothing outside the Python standard library. They're independently testable and portable.
