#!/usr/bin/python3
import re
import json
import os
import requests
from urllib.parse import unquote

API_URL = "https://cap.secondlife.com/cap/0/d661249b-2b5a-4436-966a-3d3b8d7a574f"
CACHE_FILE = "region_cache.json"


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def resolve_region(region_name: str, cache: dict) -> tuple[int, int]:
    """Regionname -> (region_x, region_y) mit Cache."""
    if region_name in cache:
        x, y = cache[region_name]
        return int(x), int(y)

    params = {"var": "coords", "sim_name": region_name}
    r = requests.get(API_URL, params=params, timeout=10)
    r.raise_for_status()

    # Beispielantwort: var coords = {'x' : 1018, 'y' : 912 };
    m = re.search(r"\{\s*'x'\s*:\s*(\d+)\s*,\s*'y'\s*:\s*(\d+)\s*\}", r.text)
    if not m:
        raise ValueError(f"Unerwartete API-Antwort für Region '{region_name}'")

    region_x = int(m.group(1))
    region_y = int(m.group(2))

    cache[region_name] = [region_x, region_y]
    save_cache(cache)

    return region_x, region_y


def xparse_slurl(url: str) -> dict:
    m = re.search(
        r"^https?://maps\.secondlife\.com/secondlife/([^/]+)/(\d+)/(\d+)/(\d+)\s*$",
        url.strip()
    )
    if not m:
        raise ValueError(f"Ungültige SLURL: {url}")

    region_enc, x, y, z = m.groups()
    return {
        "region": unquote(region_enc),
        "x": int(x),
        "y": int(y),
        "z": int(z),
        "url": url.strip(),
    }

from urllib.parse import unquote, quote
import re

def parse_slurl(url: str) -> dict:
    """
    Akzeptiert:
    http://maps.secondlife.com/secondlife/<REGION>/<X>/<Y>/<Z>

    Gibt zurück:
    region: Klartextname
    url: secondlife:// URL mit escaped Region
    """

    m = re.search(
        r"^https?://maps\.secondlife\.com/secondlife/([^/]+)/(\d+)/(\d+)/(\d+)\s*$",
        url.strip(),
        re.IGNORECASE
    )
    if not m:
        raise ValueError(f"Ungültige SLURL: {url}")

    region_enc, x, y, z = m.groups()

    # Lesbarer Regionsname
    region = unquote(region_enc)

    # Für secondlife:// wieder escapen
    region_escaped = quote(region, safe="")

    slurl_native = f"secondlife://{region_escaped}/{x}/{y}/{z}"

    return {
        "region": region,
        "x": int(x),
        "y": int(y),
        "z": int(z),
        "url": slurl_native,
    }

def compute_grid_pos(region_x: int, region_y: int, x: int, y: int) -> list[float]:
    grid_x = region_x + x / 256.0
    grid_y = region_y + y / 256.0
    return [round(grid_x, 6), round(grid_y, 6)]


def iter_entries(lines):
    """
    Format:
    Name
    URL
    Marker

    Leere Zeilen werden ignoriert.
    """
    cleaned = [ln.strip() for ln in lines if ln.strip()]

    if len(cleaned) % 3 != 0:
        raise ValueError(
            f"Anzahl nicht-leerer Zeilen ({len(cleaned)}) ist kein Vielfaches von 3."
        )

    for i in range(0, len(cleaned), 3):
        yield cleaned[i], cleaned[i + 1], cleaned[i + 2]


def main():
    cache = load_cache()
    results = []

    with open("stations.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    for name, url, marker in iter_entries(lines):
        sl = parse_slurl(url)
        region_x, region_y = resolve_region(sl["region"], cache)
        grid_pos = compute_grid_pos(region_x, region_y, sl["x"], sl["y"])

        results.append({
            "name": name,
            "url": sl["url"],
            "region": sl["region"],
            "marker": marker,
            "grid_pos": grid_pos
        })

    with open("stations.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()

