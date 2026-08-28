#!/usr/bin/env python3
"""
Check drug-nutrient interactions for a meal or newly logged medication.
Usage:
  python3 check_interactions.py '<username>' 'meal' '<food_items_json>'
  python3 check_interactions.py '<username>' 'medication' '<medication_json>'

food_items_json: [{"name": "spinach", "grams": 100}, ...]
medication_json: {"medication": "warfarin", "dosage": "5mg"}
"""

import json
import sys
from pathlib import Path
from datetime import date

BASE = Path.home() / ".nutritionist"
SKILL_DIR = Path(__file__).parent.parent
INTERACTIONS_FILE = SKILL_DIR / "drug_interactions.json"

# Foods to nutrient mapping (simplified lookup)
FOOD_NUTRIENTS = {
    # Vitamin K (warfarin concern)
    "spinach": ["vitamin K", "calcium"],
    "kale": ["vitamin K", "calcium"],
    "broccoli": ["vitamin K", "calcium"],
    "brussels sprouts": ["vitamin K"],
    "parsley": ["vitamin K"],
    "lettuce": ["vitamin K"],
    "cabbage": ["vitamin K"],
    "chard": ["vitamin K"],
    # Calcium (levothyroxine, ciprofloxacin concern)
    "milk": ["calcium"],
    "yogurt": ["calcium"],
    "cheese": ["calcium"],
    "dairy": ["calcium"],
    "tofu": ["calcium"],
    "almonds": ["calcium", "magnesium"],
    # Iron
    "red meat": ["iron"],
    "beef": ["iron"],
    "chicken liver": ["iron"],
    "spinach": ["iron", "vitamin K", "calcium"],
    "lentils": ["iron", "fiber"],
    "beans": ["iron", "fiber"],
    # Magnesium
    "nuts": ["magnesium"],
    "seeds": ["magnesium"],
    "dark chocolate": ["magnesium"],
    "avocado": ["magnesium", "potassium"],
    # Potassium (lisinopril concern)
    "banana": ["potassium"],
    "orange": ["potassium"],
    "potato": ["potassium"],
    "sweet potato": ["potassium"],
    "avocado": ["potassium", "magnesium"],
    # Fiber (levothyroxine concern)
    "oats": ["fiber"],
    "bran": ["fiber"],
    "whole grain": ["fiber"],
    # Grapefruit (statins, amlodipine concern)
    "grapefruit": ["grapefruit"],
    # Alcohol
    "wine": ["alcohol"],
    "beer": ["alcohol"],
    "spirits": ["alcohol"],
    "alcohol": ["alcohol"],
    # Soy
    "soy": ["calcium"],
    "tofu": ["calcium"],
    "edamame": ["calcium"],
    # Coffee
    "coffee": ["coffee"],
}


def load_active_medications(username: str) -> list[str]:
    """Get list of medications the user takes (from profile + recent logs)."""
    meds = []

    # From profile
    profile_path = BASE / "users" / username / "profile.json"
    if profile_path.exists():
        profile = json.loads(profile_path.read_text())
        meds.extend([m.lower() for m in profile.get("medications_permanent", [])])

    # From today's medication log
    today = str(date.today())
    month = today[:7]
    med_file = BASE / "users" / username / "medications" / f"{month}.csv"
    if med_file.exists():
        import csv
        with open(med_file) as f:
            for row in csv.DictReader(f):
                if row.get("date") == today:
                    meds.append(row.get("medication_name", "").lower())

    return list(set(meds))


def get_nutrients_in_meal(food_items: list[dict]) -> set[str]:
    """Map food items to nutrients they contain."""
    nutrients = set()
    for item in food_items:
        name = item.get("name", "").lower()
        for food_key, nutrient_list in FOOD_NUTRIENTS.items():
            if food_key in name or name in food_key:
                nutrients.update(nutrient_list)
    return nutrients


def check_meal_interactions(username: str, food_items: list[dict]) -> list[dict]:
    if not INTERACTIONS_FILE.exists():
        return []

    interactions_db = json.loads(INTERACTIONS_FILE.read_text())
    active_meds = load_active_medications(username)
    meal_nutrients = get_nutrients_in_meal(food_items)

    warnings = []
    for med in active_meds:
        med_lower = med.lower()
        if med_lower not in interactions_db:
            continue

        info = interactions_db[med_lower]
        nutrients_to_avoid = [n.lower() for n in info.get("nutrients_to_avoid", [])]
        foods_to_avoid = [f.lower() for f in info.get("foods_to_avoid", [])]

        triggered_nutrients = meal_nutrients.intersection(set(nutrients_to_avoid))
        triggered_foods = []
        for item in food_items:
            name = item.get("name", "").lower()
            for avoid_food in foods_to_avoid:
                if avoid_food in name:
                    triggered_foods.append(item["name"])

        if triggered_nutrients or triggered_foods:
            hours = info.get("avoid_within_hours", 0)
            warnings.append({
                "medication": med,
                "triggered_by": list(triggered_nutrients) + triggered_foods,
                "warning": info["warning"],
                "timing_note": info.get("timing_note", ""),
                "avoid_within_hours": hours,
                "severity": "high" if hours > 0 else "moderate",
            })

    return warnings


def check_medication_interactions(username: str, new_medication: dict) -> list[dict]:
    if not INTERACTIONS_FILE.exists():
        return []

    interactions_db = json.loads(INTERACTIONS_FILE.read_text())
    med_name = new_medication.get("medication", "").lower()

    warnings = []
    if med_name in interactions_db:
        info = interactions_db[med_name]
        warnings.append({
            "medication": med_name,
            "type": "new_medication",
            "warning": info["warning"],
            "timing_note": info.get("timing_note", ""),
            "foods_to_avoid": info.get("foods_to_avoid", []),
            "depletions": info.get("depletions", []),
            "avoid_within_hours": info.get("avoid_within_hours", 0),
        })

    return warnings


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Usage: check_interactions.py '<username>' '<context>' '<data_json>'"}))
        sys.exit(1)

    username = sys.argv[1]
    context = sys.argv[2]  # 'meal' or 'medication'
    try:
        data = json.loads(sys.argv[3])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    if context == "meal":
        warnings = check_meal_interactions(username, data if isinstance(data, list) else [data])
    elif context == "medication":
        warnings = check_medication_interactions(username, data)
    else:
        warnings = []

    print(json.dumps({"warnings": warnings, "count": len(warnings)}, indent=2))
