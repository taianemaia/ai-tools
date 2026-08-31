#!/usr/bin/env python3
"""
Append medication entries to the monthly CSV.
Usage: python3 log_medication.py '<username>' '<entries_json>'

entries_json:
[{
  "date": "2026-03-16",
  "time": "07:00",
  "medication_name": "levothyroxine",
  "dosage": "50",
  "unit": "mcg",
  "with_food": false,
  "notes": "take 30min before breakfast"
}]
"""

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

BASE = Path.home() / ".nutritionist"

MED_HEADERS = [
    "date", "time", "medication_name", "dosage", "unit", "with_food", "notes",
]


def get_med_file(username: str, entry_date: str) -> Path:
    month = entry_date[:7]
    return BASE / "users" / username / "medications" / f"{month}.csv"


def write_headers_if_new(path: Path) -> None:
    if not path.exists():
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=MED_HEADERS)
            writer.writeheader()


def log_medications(username: str, entries: list[dict]) -> dict:
    today = str(date.today())
    now = datetime.now().strftime("%H:%M")

    logged = []
    for entry in entries:
        entry_date = entry.get("date", today)
        entry["date"] = entry_date
        entry["time"] = entry.get("time", now)
        entry["with_food"] = str(entry.get("with_food", False)).lower()

        med_file = get_med_file(username, entry_date)
        write_headers_if_new(med_file)

        row = {h: entry.get(h, "") for h in MED_HEADERS}

        with open(med_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=MED_HEADERS)
            writer.writerow(row)

        logged.append({
            "medication_name": entry.get("medication_name"),
            "dosage": f"{entry.get('dosage', '')}{entry.get('unit', '')}",
            "time": entry["time"],
            "with_food": entry["with_food"],
        })

    return {"success": True, "logged": logged, "count": len(logged)}


def get_daily_medications(username: str, target_date: str = None) -> list[dict]:
    target_date = target_date or str(date.today())
    med_file = get_med_file(username, target_date)

    meds = []
    if not med_file.exists():
        return meds

    with open(med_file) as f:
        for row in csv.DictReader(f):
            if row["date"] == target_date:
                meds.append({
                    "time": row.get("time"),
                    "medication": row.get("medication_name"),
                    "dosage": f"{row.get('dosage', '')}{row.get('unit', '')}",
                    "with_food": row.get("with_food", "false") == "true",
                    "notes": row.get("notes", ""),
                })

    return meds


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: log_medication.py '<username>' '<entries_json>'"}))
        sys.exit(1)

    username = sys.argv[1]
    try:
        entries = json.loads(sys.argv[2])
        if isinstance(entries, dict):
            entries = [entries]
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = log_medications(username, entries)
    result["today_medications"] = get_daily_medications(username)
    print(json.dumps(result, indent=2))
