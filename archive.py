#!/usr/bin/env python3
"""
Full MITIC Archive — dumps ALL tables from the Glide snapshot into SQLite.

Usage:
  python3 archive.py                     # Fetch + store everything
  python3 archive.py --db /path/to/db    # Custom DB path
  python3 archive.py --snapshot file.json # Use existing snapshot
"""

import json
import base64
import os
import subprocess
import sqlite3
import sys
import re
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).parent
DEFAULT_DB = SCRIPT_DIR / "mitic.db"

# Tables to skip (no real data, or internal Glide refs)
SKIP_TABLES = {'WAHSA'}  # empty table

# Column renames for readability
COLUMN_RENAMES = {
    '\U0001f512 Row ID': '_row_id',
    '\U0001f512 Row ID B': '_row_id',
    '\U0001f512Row ID': '_row_id',
    '\U0001f512 Row ID\n': '_row_id',
    'RowID': '_row_id',
    'Link to PEA': '_pea_id',
}

def fetch_snapshot():
    """Run Puppeteer to get the decoded snapshot JSON."""
    script_path = SCRIPT_DIR / "scrape-snapshot.mjs"
    result = subprocess.run(
        ["node", str(script_path)],
        capture_output=True, text=True, timeout=60,
        cwd=str(SCRIPT_DIR)
    )
    if result.returncode != 0:
        raise RuntimeError(f"Scraper failed: {result.stderr}")
    return json.loads(result.stdout)

def load_snapshot(path=None):
    """Load snapshot from file or fetch fresh."""
    if path:
        print(f"Loading snapshot from {path}")
        raw = open(path).read()
        return json.loads(raw)
    print("Fetching snapshot from airhockeyrank.com...")
    return fetch_snapshot()

def clean_value(v):
    """Flatten a Glide value to something SQLite-safe."""
    if v is None:
        return None
    if isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, dict):
        # Glide date/time object
        if 'kind' in v:
            kind = v.get('kind')
            if kind in ('glide-date-time', 'glide-date'):
                return v.get('repr') or v.get('value')
            if kind == 'glide-image':
                return v.get('uri') or str(v.get('value', ''))
            return v.get('repr') or str(v)
        # Glide $ref array — skip, these are internal references
        if '$ref' in v:
            return None
        # fallback
        return str(v)
    if isinstance(v, list):
        return json.dumps(v)
    return str(v)

def sanitize_column_name(name):
    """Turn a Glide column name into a safe SQLite identifier."""
    # Check renames first
    if name in COLUMN_RENAMES:
        return COLUMN_RENAMES[name]
    # Strip special chars, replace spaces
    safe = re.sub(r'[^\w]', '_', name)
    safe = re.sub(r'_+', '_', safe).strip('_')
    # Handle empty / all-digits names
    if not safe or safe.isdigit():
        safe = f"col_{safe}" if safe else "unnamed"
    if safe[0].isdigit():
        safe = f"c{safe}"
    return safe.lower()

def infer_type(values):
    """Infer SQLite type from a sample of values."""
    has_int = has_float = has_text = False
    for v in values:
        if v is None:
            continue
        if isinstance(v, bool):
            continue
        if isinstance(v, int):
            has_int = True
        elif isinstance(v, float):
            has_float = True
        elif isinstance(v, str):
            has_text = True
    
    if has_float:
        return 'REAL'
    if has_int and not has_text:
        return 'INTEGER'
    return 'TEXT'

def build_table(conn, table_name, rows):
    """Create or replace a SQLite table from Glide table rows."""
    if not rows:
        return 0
    
    # Gather all column names from all rows
    all_cols = set()
    for r in rows:
        all_cols.update(r.get('data', {}).keys())
    
    # Also get the row ID from the top-level
    base_fields = ['_row_index']
    if rows[0].get('id'):
        base_fields.append('_glide_id')
    
    # Build column map
    col_map = {}
    for raw_name in all_cols:
        safe = sanitize_column_name(raw_name)
        col_map[raw_name] = safe
    
    # Collect sample values for type inference
    col_values = {raw: [] for raw in all_cols}
    for r in rows[:100]:  # sample first 100 rows
        d = r.get('data', {})
        for raw_name in all_cols:
            v = d.get(raw_name)
            col_values[raw_name].append(clean_value(v))
    
    # Build CREATE TABLE
    cols_def = []
    for col in base_fields:
        cols_def.append(f"{col} INTEGER")
    for raw_name in all_cols:
        safe = col_map[raw_name]
        sample = col_values[raw_name]
        typ = infer_type(sample)
        cols_def.append(f'"{safe}" {typ}')
    
    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(cols_def)})'
    
    cursor = conn.cursor()
    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    cursor.execute(create_sql)
    
    # Insert rows
    cols_list = base_fields + [col_map[raw] for raw in all_cols]
    placeholders = ", ".join(["?"] * len(cols_list))
    quoted_cols = ', '.join(f'"{c}"' for c in cols_list)
    insert_sql = f'INSERT INTO "{table_name}" ({quoted_cols}) VALUES ({placeholders})'
    
    count = 0
    for r in rows:
        d = r.get('data', {})
        vals = []
        for col in base_fields:
            if col == '_row_index':
                vals.append(d.get('$rowIndex', r.get('$rowIndex')))
            elif col == '_glide_id':
                vals.append(r.get('id'))
        for raw_name in all_cols:
            v = d.get(raw_name)
            vals.append(clean_value(v))
        try:
            cursor.execute(insert_sql, vals)
            count += 1
        except Exception as e:
            # Skip rows that fail (type mismatches, etc)
            pass
    
    conn.commit()
    
    # Create an index on row_index if it exists
    try:
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_row_index ON "{table_name}" (_row_index)')
    except:
        pass
    
    return count

def archive_all(snapshot, db_path):
    """Archive all tables from the snapshot into SQLite."""
    tables = snapshot.get('data', {})
    version = snapshot.get('version')
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode = WAL")
    
    print(f"Snapshot version: {version}")
    print(f"Total tables in snapshot: {len(tables)}")
    
    results = {}
    for name, rows in tables.items():
        if name in SKIP_TABLES:
            results[name] = ('skipped', 0)
            continue
        if not isinstance(rows, list):
            results[name] = ('not-a-list', 0)
            continue
        
        safe_name = sanitize_column_name(name)
        count = build_table(conn, safe_name, rows)
        results[name] = ('ok', count)
        status = "✓" if count > 0 else "·"
        print(f"  {status} {name:<30} → {count:>6} rows")
    
    # Store metadata
    meta_conn = sqlite3.connect(str(db_path))
    meta_conn.execute("""
        CREATE TABLE IF NOT EXISTS _archive_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    now = datetime.now(timezone.utc).isoformat()
    meta_conn.execute("REPLACE INTO _archive_meta (key, value) VALUES (?, ?)", ("archived_at", now))
    meta_conn.execute("REPLACE INTO _archive_meta (key, value) VALUES (?, ?)", ("snapshot_version", str(version)))
    meta_conn.execute("REPLACE INTO _archive_meta (key, value) VALUES (?, ?)", ("table_count", str(len(tables))))
    total_rows = sum(v[1] for v in results.values())
    meta_conn.execute("REPLACE INTO _archive_meta (key, value) VALUES (?, ?)", ("total_rows", str(total_rows)))
    meta_conn.commit()
    meta_conn.close()
    
    conn.close()
    
    print(f"\nTotal: {total_rows} rows across {len(tables)} tables")
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Archive all MITIC data from airhockeyrank.com")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")
    parser.add_argument("--snapshot", help="Use existing snapshot JSON file instead of fetching")
    args = parser.parse_args()
    
    snapshot = load_snapshot(args.snapshot)
    archive_all(snapshot, Path(args.db))

if __name__ == "__main__":
    main()
