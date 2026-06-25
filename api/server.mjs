#!/usr/bin/env node
// api/server.mjs — MITIC Archive API
import express from 'express';
import cors from 'cors';
import Database from 'better-sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DB_PATH = join(__dirname, '..', 'mitic.db');

function db() {
  const d = new Database(DB_PATH, { readonly: true });
  d.pragma('journal_mode = WAL');
  return d;
}

const app = express();
app.use(cors());
app.use(express.json());

// ─── Status ──────────────────────────────────────────────
app.get('/api/status', (req, res) => {
  try {
    const d = db();
    const meta = {};
    try { for (const r of d.prepare("SELECT key, value FROM _archive_meta").iterate()) meta[r.key] = r.value; } catch {}
    const tables = d.prepare("SELECT name FROM sqlite_master WHERE type='table' AND SUBSTR(name,1,1)!='_' ORDER BY name").all()
      .map(r => { const c = d.prepare(`SELECT COUNT(*) AS c FROM "${r.name}"`).get().c; return { name: r.name, rows: c }; });
    d.close();
    res.json({ ok: true, meta, tables });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Generic table query ─────────────────────────────────
app.get('/api/tables/:table', (req, res) => {
  try {
    const d = db();
    const t = req.params.table.replace(/[^a-zA-Z0-9_]/g, '');
    if (!d.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?").get(t))
      return res.status(404).json({ ok: false, error: 'not found' });
    const { sort, order, limit = 100, offset = 0 } = req.query;
    const cols = d.prepare(`PRAGMA table_info("${t}")`).all().map(c => c.name);
    let sc = '_row_index', sd = 'ASC';
    if (sort && cols.includes(sort.replace(/[^a-zA-Z0-9_]/g, ''))) { sc = sort.replace(/[^a-zA-Z0-9_]/g, ''); sd = order === 'asc' ? 'ASC' : 'DESC'; }
    const total = d.prepare(`SELECT COUNT(*) AS c FROM "${t}"`).get().c;
    const data = d.prepare(`SELECT * FROM "${t}" ORDER BY "${sc}" ${sd} NULLS LAST LIMIT ? OFFSET ?`).all(parseInt(limit), parseInt(offset));
    d.close();
    res.json({ total, offset: +offset, limit: +limit, data });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Rankings (players) ──────────────────────────────────
app.get('/api/players', (req, res) => {
  try {
    const d = db();
    const tbl = d.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='tx_weekly_regulars'").get()?.name;
    if (!tbl) return res.json({ total: 0, data: [] });
    const { sort = 'mitic', order = 'desc', limit = 100, offset = 0, search, region, min_mitic, max_mitic } = req.query;
    const allowed = ['mitic','mitic_traditional','new_elo','rank','name','weekly_level','defense_pct'];
    const sc = allowed.includes(sort) ? sort : 'mitic';
    const sd = order === 'asc' ? 'ASC' : 'DESC';
    const w = [], p = [];
    if (search) { w.push("(name LIKE ? OR nickname LIKE ? OR location LIKE ?)"); const q = `%${search}%`; p.push(q,q,q); }
    if (region) { w.push("region = ?"); p.push(region); }
    if (min_mitic) { w.push("mitic >= ?"); p.push(parseFloat(min_mitic)); }
    if (max_mitic) { w.push("mitic <= ?"); p.push(parseFloat(max_mitic)); }
    const wc = w.length ? 'WHERE ' + w.join(' AND ') : '';
    const total = d.prepare(`SELECT COUNT(*) AS c FROM "${tbl}" ${wc}`).get(...p).c;
    const data = d.prepare(`SELECT * FROM "${tbl}" ${wc} ORDER BY "${sc}" ${sd} NULLS LAST LIMIT ? OFFSET ?`).all(...p, +limit, +offset);
    d.close();
    res.json({ total, offset: +offset, limit: +limit, data });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Player matches ──────────────────────────────────────
app.get('/api/players/:id/matches', (req, res) => {
  try {
    const d = db();
    const player = d.prepare("SELECT name FROM tx_weekly_regulars WHERE _row_index = ?").get(+req.params.id);
    if (!player) return res.status(404).json({ ok: false, error: 'player not found' });
    const { limit = 50, offset = 0 } = req.query;
    const name = player.name;
    const total = d.prepare("SELECT COUNT(*) AS c FROM challenge_match WHERE player_1 = ? OR player_2 = ?").get(name, name).c;
    const data = d.prepare("SELECT * FROM challenge_match WHERE player_1 = ? OR player_2 = ? ORDER BY _row_index DESC LIMIT ? OFFSET ?").all(name, name, +limit, +offset);
    d.close();
    res.json({ total, offset: +offset, limit: +limit, player: name, data });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Player tournament history ───────────────────────────
app.get('/api/players/:id/tournaments', (req, res) => {
  try {
    const d = db();
    const player = d.prepare("SELECT name FROM tx_weekly_regulars WHERE _row_index = ?").get(+req.params.id);
    if (!player) return res.status(404).json({ ok: false, error: 'player not found' });
    const { limit = 100, offset = 0 } = req.query;
    const total = d.prepare("SELECT COUNT(*) AS c FROM pea WHERE player = ?").get(player.name).c;
    const data = d.prepare("SELECT * FROM pea WHERE player = ? ORDER BY date DESC LIMIT ? OFFSET ?").all(player.name, +limit, +offset);
    d.close();
    res.json({ total, offset: +offset, limit: +limit, player: player.name, data });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Player WRH / weekly standings ──────────────────────
app.get('/api/players/:id/standings', (req, res) => {
  try {
    const d = db();
    const player = d.prepare("SELECT name FROM tx_weekly_regulars WHERE _row_index = ?").get(+req.params.id);
    if (!player) return res.status(404).json({ ok: false, error: 'player not found' });
    const name = player.name;
    const parts = name.split(' ');
    const alt = parts.length >= 2 ? `${parts[parts.length-1]}, ${parts.slice(0,-1).join(' ')}` : name;
    const wrh = d.prepare("SELECT * FROM wrh WHERE player_name = ? OR player_name = ?").get(name, alt);
    const weekly = d.prepare("SELECT * FROM c2026_weekly_data WHERE player_name = ? OR player_name = ?").get(name, alt);
    d.close();
    res.json({ player: name, wrh, weekly });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Single player (profile) ─────────────────────────────
app.get('/api/players/:id', (req, res) => {
  try {
    const d = db();
    const tbl = d.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='tx_weekly_regulars'").get()?.name;
    if (!tbl) return res.status(404).json({ ok: false, error: 'no players table' });
    const player = d.prepare(`SELECT * FROM "${tbl}" WHERE _row_index = ?`).get(+req.params.id);
    if (!player) return res.status(404).json({ ok: false, error: 'not found' });
    d.close();
    res.json(player);
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Regions ─────────────────────────────────────────────
app.get('/api/regions', (req, res) => {
  try {
    const d = db();
    const data = d.prepare("SELECT region, COUNT(*) AS count FROM tx_weekly_regulars WHERE region != '' AND region IS NOT NULL GROUP BY region ORDER BY region").all();
    d.close();
    res.json(data);
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Weekly results ──────────────────────────────────────
app.get('/api/weeklies', (req, res) => {
  try {
    const d = db();
    const { limit = 50, offset = 0 } = req.query;
    const total = d.prepare("SELECT COUNT(*) AS c FROM weekly_performance").get().c;
    const data = d.prepare("SELECT * FROM weekly_performance ORDER BY _row_index DESC LIMIT ? OFFSET ?").all(+limit, +offset);
    d.close();
    res.json({ total, offset: +offset, limit: +limit, data });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Weekly standings ────────────────────────────────────
app.get('/api/standings', (req, res) => {
  try {
    const d = db();
    const { year = '2026', limit = 100, offset = 0 } = req.query;
    // c2026_weekly_data has the current season
    const data = d.prepare("SELECT * FROM c2026_weekly_data ORDER BY points DESC NULLS LAST LIMIT ? OFFSET ?").all(+limit, +offset);
    const total = d.prepare("SELECT COUNT(*) AS c FROM c2026_weekly_data").get().c;
    d.close();
    res.json({ total, offset: +offset, limit: +limit, year, data });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── WRH (historical world ranking) ──────────────────────
app.get('/api/wrh', (req, res) => {
  try {
    const d = db();
    const { limit = 100, offset = 0 } = req.query;
    const total = d.prepare("SELECT COUNT(*) AS c FROM wrh").get().c;
    const data = d.prepare("SELECT * FROM wrh ORDER BY wr ASC NULLS LAST LIMIT ? OFFSET ?").all(+limit, +offset);
    d.close();
    res.json({ total, offset: +offset, limit: +limit, data });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── Content tables ──────────────────────────────────────
app.get('/api/content/:table', (req, res) => {
  const allowed = ['terminology','ref_clinic','rules','shots','videos','news','breakdown','play_puck','pole_sheet'];
  const t = req.params.table.replace(/[^a-zA-Z0-9_]/g, '');
  if (!allowed.includes(t)) return res.status(404).json({ ok: false, error: 'not found' });
  try {
    const d = db();
    const data = d.prepare(`SELECT * FROM "${t}" ORDER BY _row_index`).all();
    const total = data.length;
    d.close();
    res.json({ total, data });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

// ─── SPA ─────────────────────────────────────────────────
const frontendDist = join(__dirname, '..', 'frontend', 'dist');
app.use(express.static(frontendDist));
app.use((req, res, next) => {
  if (req.method === 'GET' && !req.path.startsWith('/api'))
    res.sendFile(join(frontendDist, 'index.html'), err => { if (err) next(); });
  else next();
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`MITIC Archive API on http://localhost:${PORT}`));
