#!/usr/bin/env python3
"""
Fetch nutritional info from USDA FoodData Central, with local cache.
Usage: python3 fetch_nutrition.py "<food_name>" <grams>

Cache: ~/.nutritionist/food_cache.json — stores per-100g macros keyed by
normalized food name. Cache is checked before any USDA API call.

Returns JSON with macros scaled to the given quantity.
API key: get a free one at https://fdc.nal.usda.gov/api-guide
Set env var: USDA_API_KEY or add it to ~/.nutritionist/config.json
"""

import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Optional
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError

BASE_URL = "https://api.nal.usda.gov/fdc/v1"
CACHE_PATH = Path.home() / ".nutritionist" / "food_cache.json"

NUTRIENT_MAP = {
    "Energy": "calories",
    "Protein": "protein_g",
    "Carbohydrate, by difference": "carbs_g",
    "Total lipid (fat)": "fat_g",
    "Fiber, total dietary": "fiber_g",
    "Sugars, total including NLEA": "sugar_g",
    "Sodium, Na": "sodium_mg",
}


# ── Cache helpers ────────────────────────────────────────────────────────────

def normalize_key(name: str) -> str:
    """Lowercase + strip for consistent cache keys."""
    return name.lower().strip()


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_cache(cache: dict) -> None:
    """Write cache to disk. Non-fatal on failure."""
    try:
        CACHE_PATH.write_text(json.dumps(cache, indent=2))
    except OSError:
        pass


def cache_lookup(food_name: str, grams: float, cache: dict) -> Optional[dict]:
    """Return scaled result from cache, or None on miss."""
    key = normalize_key(food_name)
    entry = cache.get(key)
    if not entry:
        return None
    macros_scaled = scale_macros(entry["per_100g"], grams)
    return {
        "found": True,
        "fdc_id": entry.get("fdc_id"),
        "food_name": entry["food_name"],
        "query": food_name,
        "grams": grams,
        "estimated": entry.get("estimated", False),
        "source": f"cache:{entry.get('source', 'local')}",
        "per_100g": entry["per_100g"],
        **macros_scaled,
    }


def cache_write(food_name: str, canonical_name: str, fdc_id, source: str,
                macros_per100: dict, cache: dict,
                estimated: bool = False) -> None:
    """Insert or overwrite a cache entry and persist."""
    key = normalize_key(food_name)
    cache[key] = {
        "food_name": canonical_name,
        "fdc_id": fdc_id,
        "source": source,
        "per_100g": macros_per100,
        "estimated": estimated,
        "added": str(date.today()),
    }
    save_cache(cache)


# ── USDA helpers ─────────────────────────────────────────────────────────────

def get_api_key() -> str:
    key = os.environ.get("USDA_API_KEY", "")
    if not key:
        config_path = Path.home() / ".nutritionist" / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            key = config.get("usda_api_key", "")
    return key or "DEMO_KEY"


def search_food(query: str, api_key: str, top: int = 3) -> list[dict]:
    params = urlencode({
        "query": query,
        "api_key": api_key,
        "pageSize": top,
        "dataType": "Foundation,SR Legacy,Survey (FNDDS)",
    })
    url = f"{BASE_URL}/foods/search?{params}"
    try:
        with urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("foods", [])
    except URLError as e:
        raise RuntimeError(f"USDA API request failed: {e}")


def extract_macros(food: dict) -> dict:
    macros = {v: 0.0 for v in NUTRIENT_MAP.values()}
    for nutrient in food.get("foodNutrients", []):
        name = nutrient.get("nutrientName", "")
        if name in NUTRIENT_MAP:
            macros[NUTRIENT_MAP[name]] = round(float(nutrient.get("value", 0)), 2)
    return macros


def scale_macros(macros: dict, grams: float) -> dict:
    factor = grams / 100.0
    return {k: round(v * factor, 1) for k, v in macros.items()}


# ── Main fetch (cache-first) ──────────────────────────────────────────────────

def fetch_nutrition(food_name: str, grams: float) -> dict:
    cache = load_cache()

    # 1. Cache hit → return immediately, no network call
    cached = cache_lookup(food_name, grams, cache)
    if cached:
        return cached

    # 2. Cache miss → call USDA
    api_key = get_api_key()
    foods = search_food(food_name, api_key)

    if not foods:
        return {
            "found": False,
            "food_name": food_name,
            "grams": grams,
            "estimated": True,
            "error": f"No results found for '{food_name}' in USDA database",
        }

    best = foods[0]
    fdc_id = best.get("fdcId")
    canonical = best.get("description", food_name)
    macros_per100 = extract_macros(best)
    source = f"USDA:{fdc_id}"

    # 3. Populate cache for next time
    cache_write(food_name, canonical, fdc_id, source, macros_per100, cache)

    macros_scaled = scale_macros(macros_per100, grams)
    return {
        "found": True,
        "fdc_id": fdc_id,
        "food_name": canonical,
        "query": food_name,
        "grams": grams,
        "estimated": False,
        "source": source,
        "per_100g": macros_per100,
        **macros_scaled,
    }


if __name__ == "__main__":
    # ── Subcommand: add  (manual cache seed / override) ──────────────────────
    # Usage: fetch_nutrition.py add "<food_name>" <cal> <protein> <carbs> <fat> <fiber>
    if len(sys.argv) >= 2 and sys.argv[1] == "add":
        if len(sys.argv) < 8:
            print(json.dumps({"error":
                "Usage: fetch_nutrition.py add '<food_name>' <cal> <protein_g> "
                "<carbs_g> <fat_g> <fiber_g>"}))
            sys.exit(1)
        name = sys.argv[2]
        try:
            cal, prot, carbs, fat, fiber = (float(x) for x in sys.argv[3:8])
        except ValueError as exc:
            print(json.dumps({"error": f"Invalid number: {exc}"}))
            sys.exit(1)
        macros = {
            "calories": cal, "protein_g": prot, "carbs_g": carbs,
            "fat_g": fat, "fiber_g": fiber, "sugar_g": 0.0, "sodium_mg": 0.0,
        }
        c = load_cache()
        cache_write(name, name, None, "manual", macros, c, estimated=True)
        print(json.dumps({"success": True, "cached": name, "per_100g": macros}))
        sys.exit(0)

    # ── Subcommand: lookup  (inspect cache entry) ─────────────────────────────
    # Usage: fetch_nutrition.py lookup "<food_name>"
    if len(sys.argv) >= 2 and sys.argv[1] == "lookup":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: fetch_nutrition.py lookup '<food_name>'"}))
            sys.exit(1)
        c = load_cache()
        key = normalize_key(sys.argv[2])
        entry = c.get(key)
        if entry:
            print(json.dumps({"found": True, "key": key, **entry}, indent=2))
        else:
            print(json.dumps({"found": False, "key": key}))
        sys.exit(0)

    # ── Default: fetch by name + grams ───────────────────────────────────────
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: fetch_nutrition.py '<food_name>' <grams>",
            "example": "fetch_nutrition.py 'chicken breast' 150"
        }))
        sys.exit(1)

    food_name = sys.argv[1]
    try:
        grams = float(sys.argv[2])
    except ValueError:
        print(json.dumps({"error": f"Invalid grams value: {sys.argv[2]}"}))
        sys.exit(1)

    try:
        result = fetch_nutrition(food_name, grams)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            "found": False, "error": str(e),
            "food_name": food_name, "grams": grams,
        }))
        sys.exit(1)
