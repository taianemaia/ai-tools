#!/usr/bin/env python3
"""
Calculate targets and recent patterns to inform a diet plan.
Usage: python3 diet_plan.py '<username>' '<preferences_json>'

preferences_json:
{
  "non_negotiables": ["chocolate after lunch", "bread at breakfast"],
  "avoid": ["red meat", "gluten"],
  "meal_frequency": 5,
  "include_recipes": true
}

This script returns structured data — Claude uses this to generate the actual
narrative diet plan, recipes, and grocery list.
"""

import csv
import json
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

BASE = Path.home() / ".nutritionist"


def load_profile(username: str) -> dict:
    p = BASE / "users" / username / "profile.json"
    return json.loads(p.read_text()) if p.exists() else {}


def calculate_targets(profile: dict) -> dict:
    weight = float(profile.get("weight_kg", 70))
    height = float(profile.get("height_cm", 170))
    age = int(profile.get("age", 30))
    sex = profile.get("sex", "male")
    activity = profile.get("activity_level", "moderately_active")
    goals = profile.get("goals", ["maintenance"])
    goal = goals[0] if goals else "maintenance"

    bmr = (10 * weight + 6.25 * height - 5 * age + (5 if sex == "male" else -161))
    mult = {"sedentary": 1.2, "lightly_active": 1.375, "moderately_active": 1.55, "very_active": 1.725}
    tdee = round(bmr * mult.get(activity, 1.55))

    adj = {"hypertrophy": 300, "fat_loss": -400, "maintenance": 0, "endurance": 200}
    target_cal = tdee + adj.get(goal, 0)

    protein_g = round(weight * {"hypertrophy": 2.0, "fat_loss": 2.2, "maintenance": 1.6, "endurance": 1.4}.get(goal, 1.6))
    fat_pct = {"hypertrophy": 0.25, "fat_loss": 0.30, "maintenance": 0.25, "endurance": 0.20}.get(goal, 0.25)
    fat_g = round((target_cal * fat_pct) / 9)
    carbs_g = round((target_cal - protein_g * 4 - fat_g * 9) / 4)
    fiber_g = 30 if goal == "hypertrophy" else 25

    return {
        "goal": goal,
        "target_calories": target_cal,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "fiber_g": fiber_g,
        "tdee": tdee,
        "weight_kg": weight,
    }


def get_recent_food_patterns(username: str, days: int = 14) -> dict:
    end = str(date.today())
    start = str(date.today() - timedelta(days=days))

    food_counter: Counter = Counter()
    meal_type_foods: dict[str, list] = {}

    months = set()
    d = date.today() - timedelta(days=days)
    while d <= date.today():
        months.add(d.strftime("%Y-%m"))
        d += timedelta(days=1)

    for month in months:
        f = BASE / "users" / username / "meals" / f"{month}.csv"
        if not f.exists():
            continue
        with open(f) as fh:
            for row in csv.DictReader(fh):
                if not (start <= row.get("date", "") <= end):
                    continue
                name = row.get("food_name", "").lower()
                meal_type = row.get("meal_type", "other")
                food_counter[name] += 1
                if meal_type not in meal_type_foods:
                    meal_type_foods[meal_type] = []
                if name not in meal_type_foods[meal_type]:
                    meal_type_foods[meal_type].append(name)

    return {
        "most_frequent": food_counter.most_common(10),
        "by_meal_type": meal_type_foods,
        "total_foods_tracked": len(food_counter),
    }


def distribute_macros_per_meal(targets: dict, meal_frequency: int = 5) -> list[dict]:
    """Distribute daily targets across meals with typical meal sizing."""
    # Typical meal size distribution (breakfast/snack/lunch/snack/dinner)
    distributions = {
        3: [0.30, 0.35, 0.35],  # breakfast, lunch, dinner
        4: [0.25, 0.15, 0.35, 0.25],
        5: [0.20, 0.10, 0.30, 0.10, 0.30],  # B + snack + L + snack + D
        6: [0.18, 0.10, 0.28, 0.10, 0.28, 0.06],
    }
    dist = distributions.get(meal_frequency, distributions[5])
    meal_names = {
        3: ["Breakfast", "Lunch", "Dinner"],
        4: ["Breakfast", "Morning Snack", "Lunch", "Dinner"],
        5: ["Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner"],
        6: ["Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner", "Evening Snack"],
    }.get(meal_frequency, ["Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner"])

    return [
        {
            "meal": meal_names[i],
            "calories": round(targets["target_calories"] * pct),
            "protein_g": round(targets["protein_g"] * pct),
            "carbs_g": round(targets["carbs_g"] * pct),
            "fat_g": round(targets["fat_g"] * pct),
        }
        for i, pct in enumerate(dist)
    ]


def build_diet_context(username: str, preferences: dict) -> dict:
    profile = load_profile(username)
    targets = calculate_targets(profile)
    patterns = get_recent_food_patterns(username)
    meal_freq = preferences.get("meal_frequency", 5)
    meal_targets = distribute_macros_per_meal(targets, meal_freq)

    return {
        "profile": {
            "name": profile.get("name"),
            "weight_kg": profile.get("weight_kg"),
            "goals": profile.get("goals", []),
            "allergies": profile.get("allergies", []),
            "activity_level": profile.get("activity_level"),
        },
        "targets": targets,
        "meal_targets": meal_targets,
        "meal_frequency": meal_freq,
        "preferences": {
            "non_negotiables": preferences.get("non_negotiables", []),
            "avoid": preferences.get("avoid", []),
            "include_recipes": preferences.get("include_recipes", True),
        },
        "recent_patterns": patterns,
        "instructions_for_claude": (
            "Use this data to generate:\n"
            "1. A confirmation of daily macro targets\n"
            "2. A generic daily template with flexible options per meal slot "
            "(e.g., 'Lunch: 100g rice OR 240g potatoes + 150g lean protein OR 130g chicken breast')\n"
            "3. A specific 7-day menu with meals named\n"
            "4. Recipes for the suggested meals\n"
            "5. A grocery list grouped by category\n"
            "For each non-negotiable food, include it in the correct meal slot. "
            "If it is nutritionally suboptimal, add a tip prefixed with '💡 Note:' "
            "and balance remaining macros around it. "
            "Respect all items in the avoid list — do not include them anywhere."
        ),
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: diet_plan.py '<username>' '<preferences_json>'"}))
        sys.exit(1)

    username = sys.argv[1]
    try:
        preferences = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = build_diet_context(username, preferences)
    print(json.dumps(result, indent=2))
