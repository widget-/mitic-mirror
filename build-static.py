#!/usr/bin/env python3
"""
Build static JSON dumps of all key tables for GitHub Pages deployment.
Run this after archive.py to prepare the frontend data, then build the SPA.
"""

import json
import sqlite3
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "mitic.db"
STATIC_DIR = SCRIPT_DIR / "frontend" / "public" / "data"

# Tables to dump as static JSON
TABLES = {
    "players": {
        "sql": "SELECT * FROM tx_weekly_regulars ORDER BY CAST(rank AS INTEGER) ASC NULLS LAST",
        "index": "_row_index",
    },
    "wrh": {
        "sql": "SELECT * FROM wrh ORDER BY wr ASC NULLS LAST",
    },
    "standings": {
        "sql": "SELECT * FROM c2026_weekly_data ORDER BY points DESC NULLS LAST",
    },
    "weeklies": {
        "sql": "SELECT * FROM weekly_performance ORDER BY _row_index DESC",
    },
    "matches": {
        "sql": "SELECT * FROM challenge_match ORDER BY _row_index DESC",
    },
    "regions": {
        "sql": "SELECT region, COUNT(*) AS count FROM tx_weekly_regulars WHERE region != '' AND region IS NOT NULL GROUP BY region ORDER BY region",
    },
    "terminology": {"sql": "SELECT * FROM terminology ORDER BY _row_index"},
    "rules": {"sql": "SELECT * FROM rules ORDER BY _row_index"},
    "shots": {"sql": "SELECT * FROM shots ORDER BY _row_index"},
    "ref_clinic": {"sql": "SELECT * FROM ref_clinic ORDER BY _row_index"},
    "videos": {"sql": "SELECT * FROM videos ORDER BY _row_index"},
    "news": {"sql": "SELECT * FROM news ORDER BY _row_index"},
    "events": {"sql": "SELECT * FROM events ORDER BY _row_index"},
    "users": {"sql": "SELECT * FROM users ORDER BY _row_index"},
    "variations": {"sql": "SELECT * FROM variations ORDER BY _row_index"},
    "hybrid_seeding": {"sql": "SELECT * FROM hybrid_seeding ORDER BY _row_index"},
    "cartercup_history": {"sql": "SELECT * FROM cartercup_history ORDER BY _row_index"},
    "pea": {"sql": "SELECT * FROM pea ORDER BY _row_index"},
    "breakdown": {"sql": "SELECT * FROM breakdown ORDER BY _row_index"},
    "play_puck": {"sql": "SELECT * FROM play_puck ORDER BY _row_index"},
    "pole_sheet": {"sql": "SELECT * FROM pole_sheet ORDER BY _row_index"},
    "booth": {"sql": "SELECT * FROM booth ORDER BY _row_index"},
    "copy_of_tables": {"sql": "SELECT * FROM copy_of_tables ORDER BY _row_index"},
    "dues": {"sql": "SELECT * FROM dues ORDER BY _row_index"},
    "contact": {"sql": "SELECT * FROM contact ORDER BY _row_index"},
    "weekly_signup": {"sql": "SELECT * FROM weekly_signup ORDER BY _row_index"},
    "weekly_top_4": {"sql": "SELECT * FROM weekly_top_4 ORDER BY _row_index"},
    "last_5": {"sql": "SELECT * FROM last_5 ORDER BY _row_index"},
}

# Special serialisation: convert non-serialisable types
def serialize_row(row, col_names):
    obj = {}
    for i, col in enumerate(col_names):
        val = row[i]
        # Handle bytes, memoryview, etc.
        if isinstance(val, (bytes, memoryview)):
            val = val.hex() if isinstance(val, bytes) else bytes(val).hex()
        # Handle large ints
        if isinstance(val, int) and abs(val) > 2**53:
            val = str(val)
        obj[col] = val
    return obj

def dump_table(table_name, config):
    """Dump a SQLite table to a JSON file."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(config["sql"])
    col_names = [desc[0] for desc in cursor.description]
    rows = [serialize_row(row, col_names) for row in cursor.fetchall()]
    conn.close()

    out_path = STATIC_DIR / f"{table_name}.json"
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(rows, f, default=str)
    print(f"  {table_name:<20} → {len(rows):>6} rows  ({out_path.name})")

def main():
    print("Dumping static JSON from mitic.db...\n")

    # Dump each table
    for name, config in TABLES.items():
        try:
            dump_table(name, config)
        except Exception as e:
            print(f"  {name:<20} ✗ ERROR: {e}")

    # Count total
    total_files = len(list(STATIC_DIR.glob("*.json")))
    total_bytes = sum(f.stat().st_size for f in STATIC_DIR.glob("*.json"))
    print(f"\nWrote {total_files} files ({total_bytes / 1024:.0f} KB) to {STATIC_DIR}")

if __name__ == "__main__":
    main()
