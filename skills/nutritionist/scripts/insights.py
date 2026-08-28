#!/usr/bin/env python3
"""
Aggregate data and generate text insights for a given period.
Usage: python3 insights.py '<username>' '<start_date>' '<end_date>'
Dates: YYYY-MM-DD format
"""

import csv
import json
import sys
from datetime import date, timedelta, datetime
from pathlib import Path

BASE = Path.home() / ".nutritionist"


def daterange(start: str, end: str):
    start_d = datetime.strptime(start, "%Y-%m-%d").date()
    end_d = datetime.strptime(end, "%Y-%m-%d").date()
    while start_d <= end_d:
        yield str(start_d)
        start_d += timedelta(days=1)


def months_in_range(start: str, end: str) -> list[str]:
    months = set()
    for d in daterange(start, end):
        months.add(d[:7])
    return sorted(months)


def load_meals(username: str, start: str, end: str) -> list[dict]:
    rows = []
    for month in months_in_range(start, end):
        f = BASE / "users" / username / "meals" / f"{month}.csv"
        if f.exists():
            with open(f) as fh:
                for row in csv.DictReader(fh):
                    if start <= row.get("date", "") <= end:
                        rows.append(row)
    return rows


def load_workouts(username: str, start: str, end: str) -> list[dict]:
    rows = []
    for month in months_in_range(start, end):
        f = BASE / "users" / username / "workouts" / f"{month}.csv"
        if f.exists():
            with open(f) as fh:
                for row in csv.DictReader(fh):
                    if start <= row.get("date", "") <= end:
                        rows.append(row)
    return rows


def load_profile(username: str) -> dict:
    p = BASE / "users" / username / "profile.json"
    return json.loads(p.read_text()) if p.exists() else {}


def calculate_tdee(profile: dict) -> dict:
    weight = float(profile.get("weight_kg", 70))
    height = float(profile.get("height_cm", 170))
    age = int(profile.get("age", 30))
    sex = profile.get("sex", "male")
    activity = profile.get("activity_level", "moderately_active")

    if sex == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
    }
    tdee = bmr * multipliers.get(activity, 1.55)

    goal = profile.get("goals", ["maintenance"])[0] if profile.get("goals") else "maintenance"
    goal_adjustments = {"hypertrophy": 300, "fat_loss": -400, "maintenance": 0, "endurance": 200}
    target_calories = tdee + goal_adjustments.get(goal, 0)

    macro_targets = {
        "hypertrophy": {"protein_g": weight * 2.0, "fat_pct": 0.25},
        "fat_loss": {"protein_g": weight * 2.2, "fat_pct": 0.30},
        "maintenance": {"protein_g": weight * 1.6, "fat_pct": 0.25},
        "endurance": {"protein_g": weight * 1.4, "fat_pct": 0.20},
    }
    macros = macro_targets.get(goal, macro_targets["maintenance"])
    fat_g = (target_calories * macros["fat_pct"]) / 9
    protein_g = macros["protein_g"]
    carbs_g = (target_calories - protein_g * 4 - fat_g * 9) / 4

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_calories": round(target_calories),
        "target_protein_g": round(protein_g),
        "target_carbs_g": round(carbs_g),
        "target_fat_g": round(fat_g),
    }


def aggregate_meals(meal_rows: list[dict], start: str, end: str) -> dict:
    days_with_data = set()
    daily = {}

    for row in meal_rows:
        d = row.get("date", "")
        if d not in daily:
            daily[d] = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0}
        days_with_data.add(d)
        for key in daily[d]:
            try:
                daily[d][key] = round(daily[d][key] + float(row.get(key, 0) or 0), 1)
            except (ValueError, TypeError):
                pass

    total_days = len(list(daterange(start, end)))
    days_logged = len(days_with_data)

    if not daily:
        return {"daily": {}, "averages": {}, "days_logged": 0, "total_days": total_days}

    avgs = {}
    for key in ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"]:
        vals = [daily[d][key] for d in daily]
        avgs[key] = round(sum(vals) / len(vals), 1) if vals else 0

    return {"daily": daily, "averages": avgs, "days_logged": days_logged, "total_days": total_days}


def aggregate_workouts(workout_rows: list[dict], start: str, end: str) -> dict:
    days_with_workouts = set()
    workout_days = {}
    cardio_days = []
    weightlifting_days = []
    total_calories_burned = 0
    activity_counts = {}

    for row in workout_rows:
        d = row.get("date", "")
        activity = row.get("activity_type", "other")
        days_with_workouts.add(d)
        activity_counts[activity] = activity_counts.get(activity, 0) + 1

        if activity in ("yoga", "indoor_cycling"):
            if d not in [x["date"] for x in cardio_days]:
                cardio_days.append({
                    "date": d,
                    "activity": activity,
                    "duration_min": float(row.get("duration_min") or 0),
                    "calories": float(row.get("calories_burned") or 0),
                })

        if activity == "weightlifting":
            if d not in weightlifting_days:
                weightlifting_days.append(d)

    total_days = len(list(daterange(start, end)))
    return {
        "days_with_workouts": len(days_with_workouts),
        "total_days": total_days,
        "cardio_sessions": len(cardio_days),
        "weightlifting_sessions": len(weightlifting_days),
        "activity_counts": activity_counts,
    }


def generate_insights(username: str, start: str, end: str) -> dict:
    profile = load_profile(username)
    targets = calculate_tdee(profile)
    meal_rows = load_meals(username, start, end)
    workout_rows = load_workouts(username, start, end)

    meal_stats = aggregate_meals(meal_rows, start, end)
    workout_stats = aggregate_workouts(workout_rows, start, end)

    avgs = meal_stats.get("averages", {})
    total_days = meal_stats["total_days"]
    days_logged = meal_stats["days_logged"]

    positives = []
    warnings = []
    suggestions = []

    # --- Meal insights ---
    if days_logged == 0:
        warnings.append("No meals logged for this period.")
    else:
        logging_rate = days_logged / total_days * 100
        if logging_rate >= 80:
            positives.append(f"Great consistency — meals logged on {days_logged}/{total_days} days ({logging_rate:.0f}%).")
        else:
            warnings.append(f"Meals only logged on {days_logged}/{total_days} days ({logging_rate:.0f}%). More data means better insights.")

        avg_protein = avgs.get("protein_g", 0)
        target_protein = targets["target_protein_g"]
        if avg_protein >= target_protein * 0.9:
            positives.append(f"Protein intake on target: avg {avg_protein}g/day (target {target_protein}g).")
        elif avg_protein >= target_protein * 0.75:
            warnings.append(f"Protein slightly below target: avg {avg_protein}g/day vs {target_protein}g target. Consider adding a protein source to one meal.")
        else:
            warnings.append(f"Protein significantly below target: avg {avg_protein}g/day vs {target_protein}g target.")
            suggestions.append(f"Add ~{round(target_protein - avg_protein)}g protein/day — e.g., an extra 150g chicken breast (45g protein) or 200g Greek yogurt (20g protein).")

        avg_cal = avgs.get("calories", 0)
        target_cal = targets["target_calories"]
        diff_pct = abs(avg_cal - target_cal) / target_cal * 100
        if diff_pct <= 10:
            positives.append(f"Calorie intake well-calibrated: avg {avg_cal} kcal/day (target {target_cal} kcal).")
        elif avg_cal > target_cal * 1.15:
            warnings.append(f"Calorie surplus: avg {avg_cal} kcal/day is {round(avg_cal - target_cal)} kcal above target ({target_cal} kcal).")
        elif avg_cal < target_cal * 0.85:
            warnings.append(f"Calorie deficit: avg {avg_cal} kcal/day is {round(target_cal - avg_cal)} kcal below target ({target_cal} kcal).")

        avg_fiber = avgs.get("fiber_g", 0)
        if avg_fiber >= 25:
            positives.append(f"Good fiber intake: avg {avg_fiber}g/day (recommended ≥25g).")
        else:
            warnings.append(f"Low fiber intake: avg {avg_fiber}g/day (recommended ≥25g).")
            suggestions.append("Increase fiber: add vegetables, legumes, or whole grains to meals.")

    # --- Workout insights ---
    cardio = workout_stats["cardio_sessions"]
    lifting = workout_stats["weightlifting_sessions"]

    if cardio >= 3:
        positives.append(f"Good cardio volume: {cardio} sessions this period.")
    elif cardio == 0:
        warnings.append("No cardio sessions logged this period.")
        suggestions.append("Aim for 2–3 cardio sessions/week (cycling, yoga, or other aerobic activity).")
    else:
        warnings.append(f"Low cardio volume: only {cardio} session(s) this period.")

    if lifting >= 3:
        positives.append(f"Good weightlifting frequency: {lifting} sessions this period.")
    elif lifting == 0 and profile.get("goals", [""])[0] == "hypertrophy":
        warnings.append("No weightlifting sessions logged — hypertrophy goal requires resistance training.")

    return {
        "period": {"start": start, "end": end},
        "targets": targets,
        "meal_averages": avgs,
        "workout_summary": workout_stats,
        "insights": {
            "positives": positives,
            "warnings": warnings,
            "suggestions": suggestions,
        },
        "raw": {
            "meal_stats": meal_stats,
            "workout_stats": workout_stats,
        }
    }


if __name__ == "__main__":
    if len(sys.argv) < 4:
        today = str(date.today())
        week_ago = str(date.today() - timedelta(days=7))
        print(json.dumps({"error": "Usage: insights.py '<username>' '<start_date>' '<end_date>'",
                          "example": f"insights.py 'taiane' '{week_ago}' '{today}'"}))
        sys.exit(1)

    username = sys.argv[1]
    start = sys.argv[2]
    end = sys.argv[3]

    result = generate_insights(username, start, end)
    print(json.dumps(result, indent=2))
