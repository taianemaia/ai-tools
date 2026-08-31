#!/usr/bin/env python3
"""
Estimate calories burned during exercise using MET values.
Usage: python3 estimate_calories.py '<activity_type>' '<details_json>' <weight_kg>

activity_type: weightlifting | yoga | indoor_cycling
details_json for weightlifting: {"sets": [...], "duration_min": 60}
details_json for yoga: {"level": "basic|medium|advanced", "duration_min": 45}
details_json for indoor_cycling: {"duration_min": 90, "intensity": "light|moderate|vigorous"}
"""

import json
import sys
import math

# MET values by activity and intensity
MET_VALUES = {
    "weightlifting": {
        "light": 3.0,       # general, low effort
        "moderate": 3.5,    # general
        "vigorous": 6.0,    # vigorous, power lifting
        "default": 3.5,
    },
    "yoga": {
        "basic": 2.5,
        "medium": 3.3,
        "advanced": 4.0,
        "default": 3.0,
    },
    "indoor_cycling": {
        "light": 5.5,       # <50W, very light effort
        "moderate": 7.0,    # 100W, moderate effort
        "vigorous": 10.5,   # 150W+, vigorous
        "default": 7.0,
    },
}


def estimate_weightlifting(details: dict, weight_kg: float) -> dict:
    duration_min = details.get("duration_min", 0)

    if not duration_min:
        sets = details.get("sets", [])
        if sets:
            # estimate: ~2.5 min per set including rest
            duration_min = len(sets) * 2.5
        else:
            duration_min = 60  # fallback

    intensity = details.get("intensity", "moderate")
    met = MET_VALUES["weightlifting"].get(intensity, MET_VALUES["weightlifting"]["default"])

    calories = met * weight_kg * (duration_min / 60)
    return {
        "activity": "weightlifting",
        "duration_min": round(duration_min),
        "met": met,
        "estimated_calories": round(calories),
        "method": "MET estimation",
        "note": f"Based on MET={met} ({intensity} intensity) × {weight_kg}kg × {duration_min:.0f}min",
    }


def estimate_yoga(details: dict, weight_kg: float) -> dict:
    level = details.get("level", "medium").lower()
    duration_min = details.get("duration_min", 60)

    met = MET_VALUES["yoga"].get(level, MET_VALUES["yoga"]["default"])
    calories = met * weight_kg * (duration_min / 60)

    return {
        "activity": "yoga",
        "level": level,
        "duration_min": duration_min,
        "met": met,
        "estimated_calories": round(calories),
        "method": "MET estimation",
        "note": f"Based on MET={met} ({level} yoga) × {weight_kg}kg × {duration_min}min",
    }


def estimate_indoor_cycling(details: dict, weight_kg: float) -> dict:
    duration_min = details.get("duration_min", 60)
    intensity = details.get("intensity", "moderate").lower()

    met = MET_VALUES["indoor_cycling"].get(intensity, MET_VALUES["indoor_cycling"]["default"])
    calories = met * weight_kg * (duration_min / 60)

    return {
        "activity": "indoor_cycling",
        "intensity": intensity,
        "duration_min": duration_min,
        "met": met,
        "estimated_calories": round(calories),
        "method": "MET estimation",
        "note": f"Based on MET={met} ({intensity} intensity) × {weight_kg}kg × {duration_min}min",
    }


def estimate_calories(activity_type: str, details: dict, weight_kg: float) -> dict:
    activity_type = activity_type.lower().replace(" ", "_")

    if activity_type == "weightlifting":
        return estimate_weightlifting(details, weight_kg)
    elif activity_type == "yoga":
        return estimate_yoga(details, weight_kg)
    elif activity_type in ("indoor_cycling", "cycling"):
        return estimate_indoor_cycling(details, weight_kg)
    else:
        # Generic fallback using moderate MET
        duration_min = details.get("duration_min", 60)
        met = 5.0
        calories = met * weight_kg * (duration_min / 60)
        return {
            "activity": activity_type,
            "duration_min": duration_min,
            "met": met,
            "estimated_calories": round(calories),
            "method": "MET estimation (generic fallback)",
            "note": f"Unknown activity type — used generic MET={met}",
        }


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({
            "error": "Usage: estimate_calories.py '<activity_type>' '<details_json>' <weight_kg>"
        }))
        sys.exit(1)

    activity = sys.argv[1]
    try:
        details = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid details JSON: {e}"}))
        sys.exit(1)

    try:
        weight = float(sys.argv[3])
    except ValueError:
        print(json.dumps({"error": f"Invalid weight: {sys.argv[3]}"}))
        sys.exit(1)

    result = estimate_calories(activity, details, weight)
    print(json.dumps(result, indent=2))
