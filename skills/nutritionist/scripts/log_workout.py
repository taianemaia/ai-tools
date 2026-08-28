#!/usr/bin/env python3
"""
Append workout entries to the monthly CSV.
Usage: python3 log_workout.py '<username>' '<entries_json>'

entries_json for weightlifting sets:
[{
  "date": "2026-03-16",
  "time": "07:00",
  "activity_type": "weightlifting",
  "exercise_name": "bench press",
  "set": 1,
  "reps": 8,
  "weight_kg": 60.0,
  "cadence_rpm": null,
  "duration_min": null,
  "calories_burned": null,
  "calories_source": null,
  "yoga_level": null,
  "notes": ""
}]

entries_json for yoga/cycling:
[{
  "activity_type": "yoga",
  "yoga_level": "advanced",
  "duration_min": 45,
  "calories_burned": 180,
  "calories_source": "estimated",
  "notes": ""
}]
"""

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

BASE = Path.home() / ".nutritionist"

WORKOUT_HEADERS = [
    "date", "time", "activity_type", "exercise_name",
    "set", "reps", "weight_kg", "cadence_rpm",
    "duration_min", "calories_burned", "calories_source",
    "yoga_level", "notes",
]


def get_workout_file(username: str, entry_date: str) -> Path:
    month = entry_date[:7]
    return BASE / "users" / username / "workouts" / f"{month}.csv"


def write_headers_if_new(path: Path) -> None:
    if not path.exists():
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=WORKOUT_HEADERS)
            writer.writeheader()


def log_workouts(username: str, entries: list[dict]) -> dict:
    today = str(date.today())
    now = datetime.now().strftime("%H:%M")

    logged = []
    for entry in entries:
        entry_date = entry.get("date", today)
        entry["date"] = entry_date
        entry["time"] = entry.get("time", now)

        workout_file = get_workout_file(username, entry_date)
        write_headers_if_new(workout_file)

        row = {h: entry.get(h, "") for h in WORKOUT_HEADERS}

        with open(workout_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=WORKOUT_HEADERS)
            writer.writerow(row)

        logged.append({
            "activity_type": entry.get("activity_type"),
            "exercise_name": entry.get("exercise_name", ""),
            "set": entry.get("set", ""),
            "reps": entry.get("reps", ""),
            "weight_kg": entry.get("weight_kg", ""),
            "duration_min": entry.get("duration_min", ""),
            "calories_burned": entry.get("calories_burned", ""),
            "calories_source": entry.get("calories_source", ""),
        })

    return {"success": True, "logged": logged, "count": len(logged)}


def get_daily_workout_summary(username: str, target_date: str = None) -> dict:
    target_date = target_date or str(date.today())
    month = target_date[:7]
    workout_file = BASE / "users" / username / "workouts" / f"{month}.csv"

    total_calories = 0
    activities = {}

    if not workout_file.exists():
        return {"activities": activities, "total_calories_burned": 0, "date": target_date}

    with open(workout_file) as f:
        for row in csv.DictReader(f):
            if row["date"] != target_date:
                continue

            activity = row.get("activity_type", "other")
            if activity not in activities:
                activities[activity] = {
                    "exercises": [],
                    "total_sets": 0,
                    "duration_min": 0,
                    "calories_burned": 0,
                }

            cal = float(row.get("calories_burned") or 0)
            activities[activity]["calories_burned"] = max(
                activities[activity]["calories_burned"], cal
            )
            total_calories += 0  # avoid double-counting sets

            if activity == "weightlifting":
                activities[activity]["total_sets"] += 1
                ex = row.get("exercise_name", "")
                if ex not in activities[activity]["exercises"]:
                    activities[activity]["exercises"].append(ex)
            else:
                dur = float(row.get("duration_min") or 0)
                activities[activity]["duration_min"] = max(
                    activities[activity]["duration_min"], dur
                )

    # Sum unique calories per activity
    for act_data in activities.values():
        total_calories += act_data["calories_burned"]

    return {
        "activities": activities,
        "total_calories_burned": round(total_calories),
        "date": target_date,
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: log_workout.py '<username>' '<entries_json>'"}))
        sys.exit(1)

    username = sys.argv[1]
    try:
        entries = json.loads(sys.argv[2])
        if isinstance(entries, dict):
            entries = [entries]
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = log_workouts(username, entries)
    result["daily_summary"] = get_daily_workout_summary(username)
    print(json.dumps(result, indent=2))
