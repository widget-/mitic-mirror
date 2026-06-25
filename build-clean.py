#!/usr/bin/env python3
"""
Build clean, normalised views of the raw archive data.

Reads mitic.db, writes mitic_clean.db with properly typed,
consistently named tables that separate global ratings from
regional ranking systems.

Usage:  python3 build-clean.py
"""

import sqlite3
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RAW_DB = SCRIPT_DIR / "mitic.db"
CLEAN_DB = SCRIPT_DIR / "mitic_clean.db"

def open_raw():
    conn = sqlite3.connect(str(RAW_DB))
    conn.row_factory = sqlite3.Row
    return conn

def open_clean():
    db = str(CLEAN_DB)
    if CLEAN_DB.exists():
        CLEAN_DB.unlink()
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def parse_rank(raw):
    """Parse the messy rank column into (numeric_rank, region_prefix, is_world_ranked).
    
    '1'        → (1, None, True)
    'Unranked' → (None, None, False)
    'RU 01'    → (1, 'RU', False)
    'VEN 02'   → (2, 'VEN', False)
    None/''    → (None, None, False)
    """
    if raw is None or raw == '':
        return None, None, False
    s = str(raw).replace('\u00A0', '').strip()
    if s == 'Unranked':
        return None, None, False
    # "RU 01", "VEN 02"
    m = re.match(r'^([A-Z]{2,4})\s+(\d+)$', s)
    if m:
        return int(m.group(2)), m.group(1), False
    # Pure numeric
    if s.isdigit() or (s.startswith('-') and s[1:].isdigit()):
        return int(s), None, True
    return None, None, False

def parse_pct(s):
    """Parse '65%' → 65.0"""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip().rstrip('%')
    try:
        return float(s)
    except (ValueError, TypeError):
        return None

def parse_score(s):
    """Parse '4-2' → (4, 2)"""
    if not s or not isinstance(s, str):
        return None, None
    m = re.match(r'(\d+)\s*-\s*(\d+)', s)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None

def safe_float(v):
    if v is None: return None
    try: return float(v)
    except: return None

def safe_int(v):
    if v is None: return None
    try: return int(float(v))
    except: return None

# ─── Build clean tables ─────────────────────────────────

def build_players(conn_raw, conn_clean):
    rows = conn_raw.execute("SELECT * FROM tx_weekly_regulars").fetchall()
    
    conn_clean.execute("""
        CREATE TABLE players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            nickname TEXT DEFAULT '',
            mitic REAL,
            mitic_traditional REAL,
            elo REAL,
            mitic_rank INTEGER,
            world_rank INTEGER,
            is_world_ranked INTEGER DEFAULT 0,
            region TEXT DEFAULT '',
            region_rank INTEGER,
            region_rank_label TEXT,
            location TEXT DEFAULT '',
            country TEXT DEFAULT '',
            hand TEXT DEFAULT '',
            mallet TEXT DEFAULT '',
            shot_pct REAL,
            defense_pct REAL,
            weekly_level INTEGER,
            player_group TEXT DEFAULT '',
            group_rank INTEGER,  /* rank within their MITIC tier group */
            color_100 TEXT,      /* 100/200/300 club */
            color_200 TEXT,
            color_300 TEXT
        )
    """)
    
    # Pre-sort by MITIC to compute mitic_rank
    all_players = []
    for r in rows:
        d = dict(r)
        numeric_rank, region_label, is_wr = parse_rank(d.get('rank'))
        
        # Parse mitic_ranking from raw text
        mr = d.get('mitic_ranking')
        mitic_rank = safe_int(mr)
        
        all_players.append((
            d['_row_index'],
            d.get('name', '').strip(),
            d.get('nickname', '') or '',
            safe_float(d.get('mitic')),
            safe_float(d.get('mitic_traditional')),
            safe_float(d.get('new_elole')),
            mitic_rank,
            numeric_rank if is_wr else None,
            1 if is_wr or d.get('world_rank') in (1, True, '1', 'True') else 0,
            d.get('region', '') or '',
            numeric_rank if region_label else None,
            region_label,
            d.get('location', '') or '',
            d.get('Country', '') or '',
            d.get('hand', '') or '',
            d.get('mallet', '') or '',
            parse_pct(d.get('shot')),
            parse_pct(d.get('defense')),
            safe_int(d.get('weekly_level')),
            d.get('group', '') or '',
            safe_int(d.get('mitrnk')),
            d.get('100club'),
            d.get('200club'),
            d.get('300club'),
        ))
    
    conn_clean.executemany(
        "INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        all_players
    )
    conn_clean.execute("CREATE INDEX idx_players_mitic ON players(mitic DESC)")
    conn_clean.execute("CREATE INDEX idx_players_region ON players(region)")
    conn_clean.execute("CREATE INDEX idx_players_world_rank ON players(world_rank)")
    print(f"  players: {len(all_players)} rows")

def build_matches(conn_raw, conn_clean):
    rows = conn_raw.execute("SELECT * FROM challenge_match").fetchall()
    
    conn_clean.execute("""
        CREATE TABLE matches (
            id INTEGER PRIMARY KEY,
            player1 TEXT NOT NULL,
            player2 TEXT NOT NULL,
            p1_rating REAL,
            p2_rating REAL,
            winner TEXT,
            date TEXT,
            location TEXT,
            venue TEXT,
            set1_p1 INTEGER,
            set1_p2 INTEGER,
            set2_p1 INTEGER,
            set2_p2 INTEGER,
            set3_p1 INTEGER,
            set3_p2 INTEGER,
            total_p1 INTEGER,
            total_p2 INTEGER,
            referee TEXT,
            puck_color TEXT,
            format TEXT,
            p1_win_prob REAL,
            p2_win_prob REAL
        )
    """)
    
    records = []
    for r in rows:
        d = dict(r)
        p1 = (d.get('player_1') or '').strip()
        p2 = (d.get('player_2') or '').strip()
        if not p1 or not p2:
            continue
        s1_1, s1_2 = parse_score(d.get('set_1'))
        s2_1, s2_2 = parse_score(d.get('set_2'))
        s3_1, s3_2 = parse_score(d.get('set_3'))
        tot_1, tot_2 = parse_score(d.get('column9'))
        
        records.append((
            d['_row_index'],
            d.get('player_1', ''),
            d.get('player_2', ''),
            safe_float(d.get('p1_rating')),
            safe_float(d.get('p2_rating')),
            d.get('winner', ''),
            d.get('column1'),  # ISO date
            d.get('location', ''),
            d.get('location', ''),  # venue — same as location for now
            s1_1, s1_2, s2_1, s2_2, s3_1, s3_2,
            tot_1, tot_2,
            d.get('ref', ''),
            d.get('puck_color', ''),
            d.get('kvc', '') or d.get('KVC', ''),
            safe_float(d.get('percentage_p1_win')),
            safe_float(d.get('percentage_p2_win')),
        ))
    
    conn_clean.executemany(
        "INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        records
    )
    conn_clean.execute("CREATE INDEX idx_matches_player1 ON matches(player1)")
    conn_clean.execute("CREATE INDEX idx_matches_player2 ON matches(player2)")
    print(f"  matches: {len(records)} rows")

def build_tournament_results(conn_raw, conn_clean):
    rows = conn_raw.execute("SELECT * FROM pea").fetchall()
    
    conn_clean.execute("""
        CREATE TABLE tournament_results (
            id INTEGER PRIMARY KEY,
            player TEXT NOT NULL,
            event TEXT,
            date TEXT,
            rank INTEGER,
            avg_rank REAL
        )
    """)
    
    records = []
    for r in rows:
        d = dict(r)
        player = (d.get('player') or '').strip()
        if not player:
            continue
        records.append((
            d['_row_index'],
            player,
            d.get('event', ''),
            d.get('date', ''),
            safe_int(d.get('rank')),
            safe_float(d.get('avgrank')),
        ))
    
    conn_clean.executemany(
        "INSERT INTO tournament_results VALUES (?,?,?,?,?,?)",
        records
    )
    conn_clean.execute("CREATE INDEX idx_tournament_player ON tournament_results(player)")
    print(f"  tournament_results: {len(records)} rows")

def build_standings(conn_raw, conn_clean):
    """Unify WRH + 2026 weekly into one table with a season column."""
    conn_clean.execute("""
        CREATE TABLE standings (
            id INTEGER PRIMARY KEY,
            player TEXT NOT NULL,
            season TEXT NOT NULL,
            position INTEGER,
            level INTEGER,
            points REAL,
            played INTEGER,
            wins_1st INTEGER,
            second_2nd INTEGER,
            third_3rd INTEGER,
            fourth_4th INTEGER,
            win_pct REAL,
            top4_pct REAL
        )
    """)
    
    # WRH
    wrh_rows = conn_raw.execute("SELECT * FROM wrh").fetchall()
    wrh_records = []
    for r in wrh_rows:
        d = dict(r)
        wrh_records.append((
            d['_row_index'],
            d.get('player_name', ''),
            'WRH',
            safe_int(d.get('wr')),
            safe_int(d.get('level')),
            safe_float(d.get('points')),
            safe_int(d.get('played')),
            safe_int(d.get('c1st')),
            safe_int(d.get('c2nd')),
            safe_int(d.get('c3rd')),
            safe_int(d.get('c4th')),
            safe_float(d.get('win')),
            safe_float(d.get('top_4')),
        ))
    
    # 2026 Weekly
    wk_rows = conn_raw.execute("SELECT * FROM c2026_weekly_data").fetchall()
    wk_records = []
    for r in wk_rows:
        d = dict(r)
        wk_records.append((
            d['_row_index'] + 10000,  # avoid ID collision
            d.get('player_name', ''),
            '2026',
            None,  # no explicit position
            safe_int(d.get('level')),
            safe_float(d.get('points')),
            safe_int(d.get('played')),
            safe_int(d.get('c1st')),
            safe_int(d.get('c2nd')),
            safe_int(d.get('c3rd')),
            safe_int(d.get('c4th')),
            safe_float(d.get('win')),
            safe_float(d.get('top_4')),
        ))
    
    conn_clean.executemany(
        "INSERT INTO standings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        wrh_records + wk_records
    )
    conn_clean.execute("CREATE INDEX idx_standings_player ON standings(player)")
    print(f"  standings: {len(wrh_records)}+{len(wk_records)} rows")

def build_weekly_results(conn_raw, conn_clean):
    rows = conn_raw.execute("SELECT * FROM weekly_performance").fetchall()
    
    conn_clean.execute("""
        CREATE TABLE weekly_results (
            id INTEGER PRIMARY KEY,
            date TEXT,
            player_count INTEGER,
            winner_level INTEGER,
            first TEXT,
            second TEXT,
            third TEXT,
            fourth TEXT,
            places_5_8 TEXT,
            places_9_16 TEXT
        )
    """)
    
    def merge(*vals):
        return ', '.join(v for v in vals if v)
    
    records = []
    for r in rows:
        d = dict(r)
        records.append((
            d['_row_index'],
            d.get('c7_6_friday', ''),
            safe_int(d.get('player_count')),
            safe_int(d.get('winner_level')),
            d.get('c1st', ''),
            d.get('c2nd', ''),
            d.get('c3rd', ''),
            d.get('c4th', ''),
            merge(d.get('c5_6',''), d.get('c5_6_a',''), d.get('c7_8',''), d.get('c7_8_a','')),
            merge(d.get('c9_12',''), d.get('c9_12_a',''), d.get('c9_12_b',''), d.get('c9_12_c',''),
                   d.get('c13_16',''), d.get('c13_16_a',''), d.get('c13_16_b','')),
        ))
    
    conn_clean.executemany(
        "INSERT INTO weekly_results VALUES (?,?,?,?,?,?,?,?,?,?)",
        records
    )
    print(f"  weekly_results: {len(records)} rows")

def build_content_tables(conn_raw, conn_clean):
    """Copy content tables as-is (they're already clean)."""
    for table, clean_name in [
        ('terminology', 'terminology'),
        ('rules', 'rules'),
        ('shots', 'shots'),
        ('ref_clinic', 'ref_clinic'),
        ('videos', 'videos'),
        ('news', 'news'),
        ('events', 'events'),
        ('users', 'users'),
        ('variations', 'variations'),
        ('hybrid_seeding', 'hybrid_seeding'),
    ]:
        c = conn_raw.execute(f"SELECT * FROM \"{table}\"")
        rows = c.fetchall()
        if not rows:
            print(f"  {clean_name}: empty")
            continue
        col_names = [desc[0] for desc in c.description]
        # Create table
        quoted_cols = ', '.join(f'"{c}"' for c in col_names)
        cols_def = ', '.join(f'"{c}" TEXT' for c in col_names)
        conn_clean.execute(f'CREATE TABLE {clean_name} ({cols_def})')
        placeholders = ', '.join(['?'] * len(col_names))
        conn_clean.executemany(
            f'INSERT INTO {clean_name} ({quoted_cols}) VALUES ({placeholders})',
            [tuple(str(r[c]) if r[c] is not None else None for c in col_names) for r in rows]
        )
        print(f"  {clean_name}: {len(rows)} rows")

# ─── Main ──────────────────────────────────────────────

def main():
    print("Building clean database...\n")
    
    conn_raw = open_raw()
    conn_clean = open_clean()
    
    build_players(conn_raw, conn_clean)
    build_matches(conn_raw, conn_clean)
    build_tournament_results(conn_raw, conn_clean)
    build_standings(conn_raw, conn_clean)
    build_weekly_results(conn_raw, conn_clean)
    build_content_tables(conn_raw, conn_clean)
    
    conn_raw.close()
    conn_clean.commit()
    conn_clean.close()
    
    size = CLEAN_DB.stat().st_size
    print(f"\nWrote {size / 1024 / 1024:.0f} MB to {CLEAN_DB.name}")

if __name__ == '__main__':
    main()
