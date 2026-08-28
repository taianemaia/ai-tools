#!/usr/bin/env python3
"""
Generate an HTML report with charts using matplotlib.
Usage: python3 generate_charts.py '<username>' '<start_date>' '<end_date>'

Outputs a self-contained HTML file to ~/.nutritionist/charts/
"""

import base64
import csv
import io
import json
import sys
from datetime import date, timedelta, datetime
from pathlib import Path

BASE = Path.home() / ".nutritionist"


def check_matplotlib():
    try:
        import matplotlib
        return True
    except ImportError:
        return False


def daterange(start: str, end: str):
    s = datetime.strptime(start, "%Y-%m-%d").date()
    e = datetime.strptime(end, "%Y-%m-%d").date()
    while s <= e:
        yield str(s)
        s += timedelta(days=1)


def months_in_range(start: str, end: str) -> list[str]:
    months = set()
    for d in daterange(start, end):
        months.add(d[:7])
    return sorted(months)


def load_meals(username: str, start: str, end: str) -> dict[str, dict]:
    """Returns daily macro totals keyed by date."""
    daily = {}
    for month in months_in_range(start, end):
        f = BASE / "users" / username / "meals" / f"{month}.csv"
        if not f.exists():
            continue
        with open(f) as fh:
            for row in csv.DictReader(fh):
                d = row.get("date", "")
                if not (start <= d <= end):
                    continue
                if d not in daily:
                    daily[d] = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0}
                for key in daily[d]:
                    try:
                        daily[d][key] = round(daily[d][key] + float(row.get(key, 0) or 0), 1)
                    except (ValueError, TypeError):
                        pass
    return daily


def load_workouts(username: str, start: str, end: str) -> dict[str, dict]:
    """Returns daily workout summary keyed by date."""
    daily = {}
    for month in months_in_range(start, end):
        f = BASE / "users" / username / "workouts" / f"{month}.csv"
        if not f.exists():
            continue
        with open(f) as fh:
            for row in csv.DictReader(fh):
                d = row.get("date", "")
                if not (start <= d <= end):
                    continue
                if d not in daily:
                    daily[d] = {"calories_burned": 0, "has_weightlifting": False, "has_cardio": False}
                act = row.get("activity_type", "")
                if act == "weightlifting":
                    daily[d]["has_weightlifting"] = True
                elif act in ("yoga", "indoor_cycling"):
                    daily[d]["has_cardio"] = True
                try:
                    cal = float(row.get("calories_burned") or 0)
                    daily[d]["calories_burned"] = max(daily[d]["calories_burned"], cal)
                except (ValueError, TypeError):
                    pass
    return daily


def load_profile(username: str) -> dict:
    p = BASE / "users" / username / "profile.json"
    return json.loads(p.read_text()) if p.exists() else {}


def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def generate_charts(username: str, start: str, end: str) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    profile = load_profile(username)
    meal_daily = load_meals(username, start, end)
    workout_daily = load_workouts(username, start, end)

    # Build TDEE targets
    weight = float(profile.get("weight_kg", 70))
    height = float(profile.get("height_cm", 170))
    age = int(profile.get("age", 30))
    sex = profile.get("sex", "male")
    activity = profile.get("activity_level", "moderately_active")
    goal = (profile.get("goals", ["maintenance"]) or ["maintenance"])[0]

    bmr = (10 * weight + 6.25 * height - 5 * age + (5 if sex == "male" else -161))
    mult = {"sedentary": 1.2, "lightly_active": 1.375, "moderately_active": 1.55, "very_active": 1.725}
    tdee = bmr * mult.get(activity, 1.55)
    goal_adj = {"hypertrophy": 300, "fat_loss": -400, "maintenance": 0, "endurance": 200}
    target_cal = tdee + goal_adj.get(goal, 0)
    protein_targets = {"hypertrophy": 2.0, "fat_loss": 2.2, "maintenance": 1.6, "endurance": 1.4}
    target_protein = weight * protein_targets.get(goal, 1.6)

    all_dates = list(daterange(start, end))
    date_objs = [datetime.strptime(d, "%Y-%m-%d") for d in all_dates]

    def get_val(d, src, key, default=0):
        return float(src.get(d, {}).get(key, default) or default)

    calories = [get_val(d, meal_daily, "calories") for d in all_dates]
    protein = [get_val(d, meal_daily, "protein_g") for d in all_dates]
    carbs = [get_val(d, meal_daily, "carbs_g") for d in all_dates]
    fat = [get_val(d, meal_daily, "fat_g") for d in all_dates]
    fiber = [get_val(d, meal_daily, "fiber_g") for d in all_dates]
    burned = [get_val(d, workout_daily, "calories_burned") for d in all_dates]
    has_lift = [workout_daily.get(d, {}).get("has_weightlifting", False) for d in all_dates]
    has_cardio = [workout_daily.get(d, {}).get("has_cardio", False) for d in all_dates]

    # Color palette
    C = {"protein": "#4A90D9", "carbs": "#F5A623", "fat": "#D0021B",
         "fiber": "#7ED321", "calories": "#9013FE", "target": "#B8B8B8",
         "burned": "#FF6B35", "lift": "#2ECC71", "cardio": "#3498DB"}

    charts_b64 = {}

    # ── Chart 1: Calories vs Target ──
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(date_objs, calories, color=C["calories"], linewidth=2, marker="o", markersize=3, label="Calories consumed")
    ax.axhline(target_cal, color=C["target"], linestyle="--", linewidth=1.5, label=f"Target ({target_cal:.0f} kcal)")
    ax.fill_between(date_objs, calories, target_cal,
                    where=[c < target_cal for c in calories], alpha=0.1, color=C["calories"])
    ax.set_title("Daily Calorie Intake vs Target", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel("kcal")
    ax.legend(fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    charts_b64["calories"] = fig_to_base64(fig)
    plt.close(fig)

    # ── Chart 2: Macro Stacked Bar ──
    fig, ax = plt.subplots(figsize=(10, 4))
    bar_w = max(0.6, 5 / len(all_dates))
    x = range(len(all_dates))
    ax.bar(x, protein, bar_w, label="Protein", color=C["protein"])
    ax.bar(x, carbs, bar_w, bottom=protein, label="Carbs", color=C["carbs"])
    bottom_fat = [p + c for p, c in zip(protein, carbs)]
    ax.bar(x, fat, bar_w, bottom=bottom_fat, label="Fat", color=C["fat"])
    ax.set_title("Daily Macronutrients (g)", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel("grams")
    ax.set_xticks(list(x)[::max(1, len(all_dates) // 10)])
    ax.set_xticklabels([all_dates[i][5:] for i in range(len(all_dates))][::max(1, len(all_dates) // 10)], rotation=45)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    charts_b64["macros"] = fig_to_base64(fig)
    plt.close(fig)

    # ── Chart 3: Protein vs Target ──
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.bar(range(len(all_dates)), protein,
           color=[C["protein"] if p >= target_protein * 0.9 else "#FFB3B3" for p in protein],
           width=0.7)
    ax.axhline(target_protein, color=C["target"], linestyle="--", linewidth=1.5,
               label=f"Target ({target_protein:.0f}g)")
    ax.set_title("Daily Protein Intake vs Target", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel("grams")
    ax.set_xticks(list(range(len(all_dates)))[::max(1, len(all_dates) // 10)])
    ax.set_xticklabels([all_dates[i][5:] for i in range(len(all_dates))][::max(1, len(all_dates) // 10)], rotation=45)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    charts_b64["protein"] = fig_to_base64(fig)
    plt.close(fig)

    # ── Chart 4: Workout Activity Heatmap-style ──
    fig, ax = plt.subplots(figsize=(10, 2))
    for i, d in enumerate(all_dates):
        lift = has_lift[i]
        cardio = has_cardio[i]
        if lift and cardio:
            color = "#2ECC71"
        elif lift:
            color = "#3498DB"
        elif cardio:
            color = "#F39C12"
        else:
            color = "#ECECEC"
        ax.bar(i, 1, color=color, width=0.9, edgecolor="white", linewidth=0.5)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2ECC71", label="Lift + Cardio"),
        Patch(facecolor="#3498DB", label="Weightlifting"),
        Patch(facecolor="#F39C12", label="Cardio"),
        Patch(facecolor="#ECECEC", label="Rest day"),
    ]
    ax.legend(handles=legend_elements, fontsize=8, loc="upper right", ncol=4)
    ax.set_title("Workout Activity by Day", fontsize=13, fontweight="bold", pad=10)
    ax.set_yticks([])
    ax.set_xticks(list(range(len(all_dates)))[::max(1, len(all_dates) // 10)])
    ax.set_xticklabels([all_dates[i][5:] for i in range(len(all_dates))][::max(1, len(all_dates) // 10)], rotation=45)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    charts_b64["workouts"] = fig_to_base64(fig)
    plt.close(fig)

    # ── Chart 5: Calories Burned ──
    if any(b > 0 for b in burned):
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.bar(range(len(all_dates)), burned, color=C["burned"], width=0.7)
        ax.set_title("Calories Burned per Day (Workouts)", fontsize=13, fontweight="bold", pad=10)
        ax.set_ylabel("kcal")
        ax.set_xticks(list(range(len(all_dates)))[::max(1, len(all_dates) // 10)])
        ax.set_xticklabels([all_dates[i][5:] for i in range(len(all_dates))][::max(1, len(all_dates) // 10)], rotation=45)
        ax.grid(axis="y", alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        charts_b64["burned"] = fig_to_base64(fig)
        plt.close(fig)

    return charts_b64


def build_html(username: str, start: str, end: str, charts: dict) -> str:
    name = username.replace("_", " ").title()
    generated = str(date.today())

    def chart_block(key: str, title: str) -> str:
        if key not in charts:
            return ""
        return f"""
        <div class="chart-card">
            <img src="data:image/png;base64,{charts[key]}" alt="{title}" />
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nutritionist Report — {name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #F7F8FA; color: #1A1A2E; margin: 0; padding: 20px; }}
  .header {{ background: #1A1A2E; color: white; padding: 24px 32px; border-radius: 12px;
             margin-bottom: 24px; }}
  .header h1 {{ margin: 0 0 4px 0; font-size: 1.6rem; }}
  .header p {{ margin: 0; opacity: 0.7; font-size: 0.9rem; }}
  .chart-card {{ background: white; border-radius: 12px; padding: 16px;
                 margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
  .chart-card img {{ width: 100%; height: auto; }}
  .footer {{ text-align: center; opacity: 0.4; font-size: 0.8rem; margin-top: 32px; }}
</style>
</head>
<body>
<div class="header">
  <h1>Health Report — {name}</h1>
  <p>{start} to {end} &nbsp;·&nbsp; Generated {generated}</p>
</div>
{chart_block("calories", "Calorie Intake vs Target")}
{chart_block("macros", "Daily Macronutrients")}
{chart_block("protein", "Protein Intake vs Target")}
{chart_block("workouts", "Workout Activity")}
{chart_block("burned", "Calories Burned")}
<div class="footer">Generated by Personal Nutritionist · All data is local</div>
</body>
</html>"""


if __name__ == "__main__":
    if len(sys.argv) < 4:
        today = str(date.today())
        week_ago = str(date.today() - timedelta(days=7))
        print(json.dumps({"error": "Usage: generate_charts.py '<username>' '<start>' '<end>'",
                          "example": f"generate_charts.py 'taiane' '{week_ago}' '{today}'"}))
        sys.exit(1)

    username = sys.argv[1]
    start = sys.argv[2]
    end = sys.argv[3]

    if not check_matplotlib():
        print(json.dumps({
            "success": False,
            "error": "matplotlib is not installed. Run: pip install matplotlib",
        }))
        sys.exit(1)

    charts = generate_charts(username, start, end)
    html = build_html(username, start, end, charts)

    out_dir = BASE / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)

    period_label = f"{start}_to_{end}"
    out_path = out_dir / f"{username}-{period_label}.html"
    out_path.write_text(html)

    print(json.dumps({
        "success": True,
        "output": str(out_path),
        "charts_generated": list(charts.keys()),
        "open_command": f"open '{out_path}'",
    }, indent=2))
