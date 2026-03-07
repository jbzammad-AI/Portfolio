import json
import os
from engine import rules, schedule, ai_polish

DATA_DIR = "data"
LEARNERS_DIR = os.path.join(DATA_DIR, "learners")
OUTPUT_JSON_DIR = "output/plans_json"
OUTPUT_HTML_DIR = "output/plans_html"

os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)
os.makedirs(OUTPUT_HTML_DIR, exist_ok=True)

# Load skills and entitlements
with open(os.path.join(DATA_DIR, "skills.json"), "r") as f:
    skills = json.load(f)
with open(os.path.join(DATA_DIR, "entitlements.json"), "r") as f:
    entitlements = json.load(f)

# Get all learner files
learner_files = [f for f in os.listdir(LEARNERS_DIR) if f.endswith(".json")]
total_learners = len(learner_files)
print(f"🔹 Found {total_learners} learners to process.\n")

processed_count = 0

for idx, learner_file in enumerate(learner_files, 1):
    with open(os.path.join(LEARNERS_DIR, learner_file), "r") as f:
        learner = json.load(f)

    # 1. Filter by entitlement
    allowed_lessons = rules.filter_by_entitlement(skills, entitlements[learner["product_type"]])

    # 2. Prioritize weak skills
    priority_lessons = rules.prioritize_weak_skills(allowed_lessons, learner["weak_skills"])

    # 3. Remove completed lessons
    final_lessons = rules.remove_completed(priority_lessons, learner["learning_history"])

    # 4. Schedule
    scheduled_plan = schedule.plan_schedule(final_lessons, learner.get("exam_date"))

    # 5. JSON Output
    json_file = os.path.join(OUTPUT_JSON_DIR, f"{learner['learner_id']}_plan.json")
    with open(json_file, "w") as f:
        json.dump({"learner_id": learner["learner_id"], "plan": scheduled_plan}, f, indent=2)

    # 6. HTML Output using AI polish
    html_content = ai_polish.polish_schedule_ai(scheduled_plan, learner["name"])
    html_file = os.path.join(OUTPUT_HTML_DIR, f"{learner['learner_id']}_plan.html")
    with open(html_file, "w") as f:
        f.write(html_content)

    processed_count += 1

    # Print progress every 100 learners
    if idx % 100 == 0 or idx == total_learners:
        print(f"✅ Processed {idx}/{total_learners} learners...")

print(f"\n🎯 Batch processing complete!")
print(f"Total learners processed: {processed_count}")
print(f"JSON plans saved in: {OUTPUT_JSON_DIR}")
print(f"HTML plans saved in: {OUTPUT_HTML_DIR}")
