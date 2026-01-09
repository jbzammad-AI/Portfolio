import json
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse

from engine import rules, schedule

app = FastAPI(
    title="ESL Study Plan API",
    version="1.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LEARNERS_DIR = os.path.join(DATA_DIR, "learners")

with open(os.path.join(DATA_DIR, "skills.json"), "r", encoding="utf-8") as f:
    skills = json.load(f)

with open(os.path.join(DATA_DIR, "entitlements.json"), "r", encoding="utf-8") as f:
    entitlements = json.load(f)

# -------------------------
# HTML RENDERER
# -------------------------
def render_html(learner, plan):
    lessons = "".join(
        f"""
        <div class="lesson">
            <div class="lesson-title">{l['lesson']}</div>
            <div class="lesson-meta">Priority {l['priority']} • {l['scheduled_date']}</div>
        </div>
        """ for l in plan
    )

    exam = (
        f"<span class='badge'>Exam booked: {learner['exam_date']}</span>"
        if learner.get("exam_date")
        else "<span class='badge muted'>No exam booked</span>"
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Study Plan</title>
<style>
body {{
    background:#f4f6f8;
    font-family: system-ui, -apple-system;
    padding:40px;
}}
.card {{
    max-width:720px;
    margin:auto;
    background:white;
    border-radius:14px;
    padding:30px;
    box-shadow:0 10px 30px rgba(0,0,0,.08);
}}
h1 {{ margin:0 0 10px; }}
.sub {{ color:#6b7280; margin-bottom:15px; }}
.badge {{
    display:inline-block;
    padding:6px 12px;
    border-radius:20px;
    background:#e0f2fe;
    color:#0369a1;
    font-size:13px;
}}
.badge.muted {{
    background:#e5e7eb;
    color:#374151;
}}
.lesson {{
    background:#f9fafb;
    border-left:4px solid #2563eb;
    border-radius:8px;
    padding:14px;
    margin-bottom:12px;
}}
.lesson-title {{ font-weight:600; }}
.lesson-meta {{ font-size:13px; color:#6b7280; }}
.footer {{
    margin-top:25px;
    font-size:12px;
    color:#9ca3af;
    text-align:center;
}}
</style>
</head>
<body>
<div class="card">
<h1>Personalised Study Plan</h1>

<div class="sub">
Learner: <strong>{learner.get('name','Learner '+learner['learner_id'])}</strong><br>
Product: <strong>{learner['product_type']}</strong>
</div>

{exam}

<h3>Your Lessons</h3>

{lessons}

<div class="footer">Generated automatically • ESL Study Plan Engine</div>
</div>
</body>
</html>"""

# -------------------------
# PLAN GENERATOR
# -------------------------
def generate_plan(learner):
    allowed = rules.filter_by_entitlement(
        skills, entitlements[learner["product_type"]]
    )
    prioritized = rules.prioritize_weak_skills(
        allowed, learner["weak_skills"]
    )
    final = rules.remove_completed(
        prioritized, learner["learning_history"]
    )
    return schedule.plan_schedule(final, learner.get("exam_date"))

# -------------------------
# MAIN ENDPOINT
# -------------------------
@app.get("/studyplan/{learner_id}")
def study_plan(
    learner_id: str,
    format: str = Query("html", enum=["html", "json"])
):
    path = os.path.join(LEARNERS_DIR, f"learner_{learner_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Learner not found")

    with open(path, "r", encoding="utf-8") as f:
        learner = json.load(f)

    plan = generate_plan(learner)

    if format == "json":
        return JSONResponse({
            "learner_id": learner_id,
            "plan": plan
        })

    return HTMLResponse(render_html(learner, plan))
