#!/usr/bin/env python3
"""
MITIC Ratings Scraper

Fetches air hockey player ratings from airhockeyrank.com (Glide app)
and stores them in a SQLite database.

Usage:
  python3 scraper.py              # Fetch data and store in SQLite
  python3 scraper.py --db PATH    # Use custom database path
"""

import json
import os
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).parent
DEFAULT_DB = SCRIPT_DIR / "mitic.db"

def fetch_snapshot():
    """Run the Puppeteer script to get decoded snapshot JSON."""
    script_path = SCRIPT_DIR / "scrape-snapshot.mjs"
    result = subprocess.run(
        ["node", str(script_path)],
        capture_output=True, text=True, timeout=60,
        cwd=str(SCRIPT_DIR)
    )
    if result.returncode != 0:
        err = result.stderr.strip()
        raise RuntimeError(f"Scraper failed: {err}")
    return json.loads(result.stdout)

def parse_players(snapshot):
    """Extract player data from the snapshot."""
    tables = snapshot.get("data", {})
    players_raw = tables.get("TX Weekly Regulars", [])
    
    players = []
    for p in players_raw:
        d = p.get("data", {})
        name = d.get("name", "").strip()
        if not name:
            continue
        
        mitic = _parse_float(d.get("mitic"))
        mitic_traditional = _parse_float(d.get("mitic traditional"))
        new_elo = _parse_float(d.get("New ElolE"))
        rank = _parse_int(d.get("rank"))
        
        defense_raw = d.get("defense %", "")
        defense_pct = _parse_float(defense_raw.rstrip('%')) if isinstance(defense_raw, str) and defense_raw else _parse_float(defense_raw)
        weekly_level = _parse_int(d.get("weekly level"))
        
        players.append({
            "name": name,
            "nickname": d.get("nickname", "") or "",
            "mitic": mitic,
            "mitic_traditional": mitic_traditional,
            "new_elo": new_elo,
            "rank": rank,
            "location": d.get("location", "") or "",
            "region": d.get("region", "") or "",
            "country": d.get("Country", "") or "",
            "hand": d.get("hand", "") or "",
            "mallet": d.get("mallet", "") or "",
            "shot": d.get("shot", "") or "",
            "defense_pct": defense_pct,
            "weekly_level": weekly_level,
            "world_rank": bool(d.get("world rank")),
            "player_group": d.get("group", "") or "",
            "mitic_ranking": d.get("Mitic Ranking") or "",
        })
    
    return players

def _parse_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def _parse_int(val):
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

def init_db(db_path):
    """Create the SQLite database and table if not exists."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            nickname TEXT DEFAULT '',
            mitic REAL,
            mitic_traditional REAL,
            new_elo REAL,
            rank INTEGER,
            location TEXT DEFAULT '',
            region TEXT DEFAULT '',
            country TEXT DEFAULT '',
            hand TEXT DEFAULT '',
            mallet TEXT DEFAULT '',
            shot TEXT DEFAULT '',
            defense_pct REAL,
            weekly_level INTEGER,
            world_rank INTEGER DEFAULT 0,
            player_group TEXT DEFAULT '',
            mitic_ranking TEXT DEFAULT '',
            scraped_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scrape_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    return conn

def store_players(conn, players):
    """Store player data in the database."""
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("DELETE FROM players")
    
    for p in players:
        cursor.execute("""
            INSERT INTO players (
                name, nickname, mitic, mitic_traditional, new_elo, rank,
                location, region, country, hand, mallet, shot,
                defense_pct, weekly_level, world_rank, player_group,
                mitic_ranking, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["name"], p["nickname"], p["mitic"], p["mitic_traditional"],
            p["new_elo"], p["rank"], p["location"], p["region"],
            p["country"], p["hand"], p["mallet"], p["shot"],
            p["defense_pct"], p["weekly_level"], int(p["world_rank"]),
            p["player_group"], p["mitic_ranking"], now
        ))
    
    cursor.execute("REPLACE INTO scrape_meta (key, value) VALUES (?, ?)",
                   ("last_scraped", now))
    cursor.execute("REPLACE INTO scrape_meta (key, value) VALUES (?, ?)",
                   ("player_count", str(len(players))))
    
    conn.commit()
    return len(players)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scrape MITIC ratings from airhockeyrank.com")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")
    args = parser.parse_args()
    
    db_path = Path(args.db)
    print(f"Fetching MITIC ratings from airhockeyrank.com...")
    
    snapshot = fetch_snapshot()
    version = snapshot.get("version")
    print(f"Snapshot version: {version}")
    
    players = parse_players(snapshot)
    print(f"Parsed {len(players)} players")
    
    conn = init_db(db_path)
    count = store_players(conn, players)
    conn.close()
    
    print(f"Stored {count} players in {db_path}")

if __name__ == "__main__":
    main()
