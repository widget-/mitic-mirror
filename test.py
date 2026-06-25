#!/usr/bin/env python3
"""
Tests for the MITIC archive: data integrity, static build, and static mode.
Run with:  python3 test.py
"""

import json
import sqlite3
import subprocess
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "mitic_clean.db"
STATIC_DIR = SCRIPT_DIR / "frontend" / "public" / "data"
FRONTEND_DIR = SCRIPT_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"  ✓ {name}")
    except AssertionError as e:
        failed += 1
        print(f"  ✗ {name}: {e}")
    except Exception as e:
        failed += 1
        print(f"  ✗ {name}: {type(e).__name__}: {e}")

def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"expected {b!r}, got {a!r}" + (f" — {msg}" if msg else ""))

def assert_gt(a, b, msg=""):
    if not (a > b):
        raise AssertionError(f"expected {a} > {b}" + (f" — {msg}" if msg else ""))

def assert_true(v, msg=""):
    if not v:
        raise AssertionError(f"expected truthy" + (f" — {msg}" if msg else ""))

# ─── Data integrity tests ──────────────────────────────

def test_data():
    assert_true(DB_PATH.exists(), f"DB not found at {DB_PATH}")
    assert_gt(DB_PATH.stat().st_size, 1_000_000, "DB too small (<1 MB)")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Check core tables exist
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required = {'players', 'matches', 'tournament_results', 'standings',
                'weekly_results', 'events', 'news', 'users', 'terminology', 'rules',
                'ref_clinic', 'shots', 'videos', 'variations', 'hybrid_seeding'}
    missing = required - tables
    assert_eq(len(missing), 0, f"missing tables: {missing}")

    # Row counts
    counts = {
        'players': (100, 3000),       # players
        'matches': (5000, 50000),      # matches
        'tournament_results': (1000, 50000),  # tournament archive
        'standings': (200, 1000),     # unified standings
    }
    for table, (min_rows, max_rows) in counts.items():
        count = conn.execute(f"SELECT COUNT(*) FROM \"{table}\"").fetchone()[0]
        assert_gt(count, min_rows, f"{table}: {count} rows < {min_rows}")
        if max_rows:
            assert_true(count < max_rows, f"{table}: {count} rows ≥ {max_rows}")

    # Check player table schema
    p_cols = {r[1] for r in conn.execute("PRAGMA table_info(players)")}
    for col in ['name', 'mitic', 'world_rank', 'region', 'location', 'elo']:
        assert_true(col in p_cols, f"missing column: {col}")

    # Players have names
    null_names = conn.execute("SELECT COUNT(*) FROM players WHERE name IS NULL OR name = ''").fetchone()[0]
    assert_eq(null_names, 0, f"{null_names} players with empty names")

    # Match table has key columns
    cm_cols = {r[1] for r in conn.execute("PRAGMA table_info(matches)")}
    for col in ['player1', 'player2', 'winner', 'p1_rating', 'p2_rating', 'date']:
        assert_true(col in cm_cols, f"matches missing column: {col}")

    # Tournament results has player+event+rank
    pea_cols = {r[1] for r in conn.execute("PRAGMA table_info(tournament_results)")}
    for col in ['player', 'event', 'rank']:
        assert_true(col in pea_cols, f"tournament_results missing column: {col}")

    # Standings has player+points+season
    wrh_cols = {r[1] for r in conn.execute("PRAGMA table_info(standings)")}
    for col in ['player', 'points', 'position', 'season']:
        assert_true(col in wrh_cols, f"standings missing column: {col}")

    # Archive metadata — check the clean DB has data
    count_players = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    count_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    assert_gt(count_players, 500, f"too few players: {count_players}")
    assert_gt(count_matches, 5000, f"too few matches: {count_matches}")
    total = count_players + count_matches + sum(
        conn.execute(f"SELECT COUNT(*) FROM \"{t}\"").fetchone()[0]
        for t in required if t not in ('players', 'matches')
    )

    conn.close()
    print(f"    DB size: {DB_PATH.stat().st_size / 1024 / 1024:.0f} MB")
    print(f"    Tables: {len(tables)}")
    print(f"    Total rows: {total}")

# ─── Static build tests ───────────────────────────────

def test_static_build():
    assert_true(STATIC_DIR.exists(), f"static data dir not found at {STATIC_DIR}")

    required_json = {
        'players.json', 'matches.json', 'tournament_results.json', 'standings.json',
        'weeklies.json', 'regions.json', 'terminology.json', 'rules.json',
        'shots.json', 'ref_clinic.json', 'videos.json', 'news.json',
        'events.json', 'users.json', 'hybrid_seeding.json',
    }
    present = set(f.name for f in STATIC_DIR.iterdir() if f.suffix == '.json')
    missing = required_json - present
    assert_eq(len(missing), 0, f"missing JSON files: {missing}")

    # Validate each required file is valid JSON with data
    for fname in required_json:
        path = STATIC_DIR / fname
        assert_gt(path.stat().st_size, 50, f"{fname} too small")
        with open(path) as f:
            data = json.load(f)
        assert_true(isinstance(data, list), f"{fname}: root not a list")
        assert_gt(len(data), 0, f"{fname}: empty array")

    # Check specific expected counts
    players = json.load(open(STATIC_DIR / 'players.json'))
    matches = json.load(open(STATIC_DIR / 'matches.json'))
    peas = json.load(open(STATIC_DIR / 'tournament_results.json'))
    regions = json.load(open(STATIC_DIR / 'regions.json'))

    assert_gt(len(players), 500, f"only {len(players)} players")
    assert_gt(len(matches), 5000, f"only {len(matches)} matches")
    assert_gt(len(peas), 1000, f"only {len(peas)} tournament results")
    assert_gt(len(regions), 2, f"only {len(regions)} regions")

    # Check file sizes
    for fname in ['players.json', 'matches.json', 'tournament_results.json']:
        size = (STATIC_DIR / fname).stat().st_size
        print(f"    {fname}: {size / 1024:.0f} KB ({len(json.load(open(STATIC_DIR / fname)))} rows)")

    # Gzip sizes should be reasonable
    import gzip
    for fname in ['matches.json', 'players.json']:
        with open(STATIC_DIR / fname, 'rb') as f:
            gz = len(gzip.compress(f.read()))
        print(f"    {fname} gzip: {gz / 1024:.0f} KB")

# ─── Frontend build test ──────────────────────────────

def test_frontend_build():
    # Check that the built dist exists
    assert_true(DIST_DIR.exists(), f"dist dir not found at {DIST_DIR}")
    assert_true((DIST_DIR / "index.html").exists(), "dist/index.html missing")

    html = (DIST_DIR / "index.html").read_text()
    assert_true('div id="app"' in html, "index.html missing app mount point")
    assert_true('assets/index-' in html, "index.html missing asset references")

    js_files = list(DIST_DIR.glob("assets/*.js"))
    css_files = list(DIST_DIR.glob("assets/*.css"))
    assert_gt(len(js_files), 0, "no JS bundles in dist")
    assert_gt(len(css_files), 0, "no CSS bundles in dist")

    # Also verify data files were copied to dist
    dist_data = DIST_DIR / "data"
    assert_true(dist_data.exists(), "dist/data/ directory missing — Vite didn't copy public/")
    assert_true((dist_data / "players.json").exists(), "dist/data/players.json missing")

    # Verify dist file sizes are OK
    dist_size = sum(f.stat().st_size for f in DIST_DIR.rglob('*') if f.is_file())
    print(f"    Dist size: {dist_size / 1024 / 1024:.0f} MB")
    print(f"    JS bundle: {sum(f.stat().st_size for f in js_files) / 1024:.0f} KB")
    print(f"    Data files: {sum(f.stat().st_size for f in dist_data.rglob('*')) / 1024 / 1024:.0f} MB")

# ─── Static mode test (no API server) ─────────────────

def test_static_mode():
    """Start a plain HTTP server on the dist and verify the frontend's data fallback works."""
    import http.server
    import socketserver
    import threading
    import time
    import urllib.request
    import socket

    # Find a free port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()

    os.chdir(str(DIST_DIR))

    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(('', port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)

    try:
        # Index loads
        resp = urllib.request.urlopen(f'http://localhost:{port}/')
        html = resp.read().decode()
        assert_true('div id="app"' in html, "index.html from static server")

        # Static data loads
        resp = urllib.request.urlopen(f'http://localhost:{port}/data/regions.json')
        regions = json.loads(resp.read())
        assert_gt(len(regions), 2, f"regions from static server: {regions}")

        # /api/* returns 404 (simulating GitHub Pages)
        try:
            resp = urllib.request.urlopen(f'http://localhost:{port}/api/status')
            assert_eq(resp.status, 404, f"expected 404 for /api/status, got {resp.status}")
        except urllib.error.HTTPError as e:
            assert_eq(e.code, 404, f"expected 404 for /api/status, got {e.code}")

        # Big files are reachable
        resp = urllib.request.urlopen(f'http://localhost:{port}/data/players.json')
        data = json.loads(resp.read())
        assert_gt(len(data), 500, f"players from static server: {len(data)}")

        # Known players exist
        names = {p['name'] for p in data if p.get('name')}
        assert_true('Colin Cummings' in names, "known player missing from data")
        assert_true('Jacob Munoz' in names, "known player missing from data")

        print(f"    Static server on :{port} — all endpoints OK")

    finally:
        httpd.shutdown()
    os.chdir(str(SCRIPT_DIR))

# ─── Run all ──────────────────────────────────────────

if __name__ == '__main__':
    print("MITIC Archive Tests\n")

    print("1. Data integrity")
    test("Database exists and has tables", test_data)

    print("\n2. Static build")
    test("Static JSON files are valid and complete", test_static_build)

    print("\n3. Frontend build")
    test("Vite build produces valid output", test_frontend_build)

    print("\n4. Static mode (no API server)")
    test("Static server fallback works correctly", test_static_mode)

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        print("SOME TESTS FAILED — fix before deploying")
        sys.exit(1)
    else:
        print("All tests passed!")
