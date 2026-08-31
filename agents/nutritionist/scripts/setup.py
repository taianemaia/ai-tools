#!/usr/bin/env python3
"""
Setup a new user profile and directory structure.
Usage: python3 setup.py '<profile_json>'
"""

import json
import sys
from pathlib import Path
from datetime import date

BASE = Path.home() / ".nutritionist"


def setup_user(profile: dict) -> dict:
    username = profile["name"].lower().replace(" ", "_")
    user_dir = BASE / "users" / username

    for subdir in ["meals", "workouts", "medications", "diets", "insights"]:
        (user_dir / subdir).mkdir(parents=True, exist_ok=True)

    (BASE / "charts").mkdir(parents=True, exist_ok=True)

    profile["username"] = username
    profile["created_at"] = str(date.today())
    profile["updated_at"] = str(date.today())

    profile_path = user_dir / "profile.json"
    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)

    active_user_path = BASE / "active_user.txt"
    if not active_user_path.exists():
        active_user_path.write_text(username)

    return {
        "success": True,
        "username": username,
        "profile_path": str(profile_path),
        "active_user": active_user_path.read_text().strip(),
        "message": f"Profile created for {profile['name']} at {profile_path}",
    }


def get_active_user():
    p = BASE / "active_user.txt"
    if p.exists():
        return p.read_text().strip() or None
    return None


def load_profile(username: str):
    p = BASE / "users" / username / "profile.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: setup.py '<profile_json>'"}))
        sys.exit(1)

    try:
        profile_data = json.loads(sys.argv[1])
        result = setup_user(profile_data)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)
