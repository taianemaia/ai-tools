#!/usr/bin/env python3
"""
Append meal entries to the monthly CSV.
Usage: python3 log_meal.py '<username>' '<entries_json>'

entries_json: list of meal entry dicts
[{
  "date": "2026-03-16",        # optional, defaults to today
  "time": "08:00",             # optional, defaults to now
  "meal_type": "breakfast",
  "food_name": "oats rolled",
  "quantity_g": 80,
  "calories": 303.0,
  "protein_g": 10.5,
  "carbs_g": 54.8,
  "fat_g": 5.5,
  "fiber_g": 8.0,
  "source": "USDA:2343886",
  "estimated": false
}]
"""

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

BASE = Path.home() / ".nutritionist"

MEAL_HEADERS = [
    "date", "time", "meal_type", "food_name", "quantity_g",
    "calories", "protein_g", "carbs_g", "fat_g", "fiber_g",
    "source", "estimated",
]


def get_meal_file(username: str, entry_date: str) -> Path:
    month = entry_date[:7]  # YYYY-MM
    path = BASE / "users" / username / "meals" / f"{month}.csv"
    return path


def write_headers_if_new(path: Path) -> None:
    if not path.exists():
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=MEAL_HEADERS)
            writer.writeheader()


def log_meals(username: str, entries: list[dict]) -> dict:
    today = str(date.today())
    now = datetime.now().strftime("%H:%M")

    logged = []
    for entry in entries:
        entry_date = entry.get("date", today)
        entry["date"] = entry_date
        entry["time"] = entry.get("time", now)
        entry["estimated"] = str(entry.get("estimated", False)).lower()

        meal_file = get_meal_file(username, entry_date)
        write_headers_if_new(meal_file)

        row = {h: entry.get(h, "") for h in MEAL_HEADERS}

        with open(meal_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=MEAL_HEADERS)
            writer.writerow(row)

        logged.append({
            "food_name": entry.get("food_name"),
            "meal_type": entry.get("meal_type"),
            "calories": entry.get("calories"),
            "file": str(meal_file),
        })

    return {"success": True, "logged": logged, "count": len(logged)}


def get_daily_totals(username: str, target_date: str = None) -> dict:
    target_date = target_date or str(date.today())
    meal_file = get_meal_file(username, target_date)

    totals = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0}
    meals_by_type = {}

    if not meal_file.exists():
        return {"totals": totals, "meals_by_type": meals_by_type, "date": target_date}

    with open(meal_file) as f:
        for row in csv.DictReader(f):
            if row["date"] != target_date:
                continue
            for key in totals:
                try:
                    totals[key] = round(totals[key] + float(row.get(key, 0) or 0), 1)
                except (ValueError, TypeError):
                    pass
            meal_type = row.get("meal_type", "other")
            if meal_type not in meals_by_type:
                meals_by_type[meal_type] = []
            meals_by_type[meal_type].append({
                "food": row.get("food_name"),
                "grams": row.get("quantity_g"),
                "calories": row.get("calories"),
                "protein_g": row.get("protein_g"),
                "carbs_g": row.get("carbs_g"),
                "fat_g": row.get("fat_g"),
                "estimated": row.get("estimated", "false") == "true",
            })

    return {"totals": totals, "meals_by_type": meals_by_type, "date": target_date}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: log_meal.py '<username>' '<entries_json>'"}))
        sys.exit(1)

    username = sys.argv[1]
    try:
        entries = json.loads(sys.argv[2])
        if isinstance(entries, dict):
            entries = [entries]
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = log_meals(username, entries)

    # Also return today's totals
    result["daily_totals"] = get_daily_totals(username)
    print(json.dumps(result, indent=2))
