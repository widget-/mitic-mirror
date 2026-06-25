<template>
  <div class="app">
    <!-- Sidebar -->
    <aside class="sidebar">
      <h1 @click="page='rankings'" class="logo">🏒 MITIC</h1>
      <nav>
        <div class="nav-group">
          <span class="nav-head">Rankings</span>
          <a :class="{active:page==='rankings'}" @click="page='rankings'">World Rankings</a>
          <a :class="{active:page==='wrh'}" @click="page='wrh';fetchWRH()">World Ranking History</a>
          <a :class="{active:page==='standings'}" @click="page='standings';fetchStandings()">2026 Weekly Standings</a>
        </div>
        <div class="nav-group">
          <span class="nav-head">Matches</span>
          <a :class="{active:page==='matches'}" @click="page='matches';fetchMatches()">All Challenge Matches</a>
          <a :class="{active:page==='weeklies'}" @click="page='weeklies';fetchWeeklies()">Weekly Results</a>
        </div>
        <div class="nav-group">
          <span class="nav-head">Profile</span>
          <a :class="{active:page==='profile'}" v-if="profilePlayer">{{ profilePlayer }}'s Profile</a>
        </div>
        <div class="nav-group">
          <span class="nav-head">Resources</span>
          <a :class="{active:page==='content' && contentTable==='terminology'}" @click="openContent('terminology')">Terminology</a>
          <a :class="{active:page==='content' && contentTable==='rules'}" @click="openContent('rules')">Rules</a>
          <a :class="{active:page==='content' && contentTable==='shots'}" @click="openContent('shots')">Shots Library</a>
          <a :class="{active:page==='content' && contentTable==='ref_clinic'}" @click="openContent('ref_clinic')">Referee Clinic</a>
          <a :class="{active:page==='content' && contentTable==='videos'}" @click="openContent('videos')">Videos</a>
          <a :class="{active:page==='content' && contentTable==='news'}" @click="openContent('news')">News</a>
        </div>
      </nav>
      <div class="meta" v-if="status">{{ status.tables?.length || 0 }} tables &middot; {{ status.meta?.total_rows || '?' }} rows<br><small>{{ status.meta?.archived_at ? new Date(status.meta.archived_at).toLocaleDateString() : '' }}</small></div>
    </aside>

    <main class="content">
      <!-- Rankings Page -->
      <section v-if="page==='rankings'">
        <header><h2>World Rankings</h2><p class="sub">MITIC / ELO ratings &amp; player profiles</p></header>
        <div class="filters">
          <input v-model="rSearch" placeholder="Search name, nickname, location..." @input="debounce(()=>{rPage=1;fetchPlayers()})" />
          <select v-model="rRegion" @change="rPage=1;fetchPlayers()"><option value="">All Regions</option><option v-for="r in regions" :key="r.region" :value="r.region">{{ r.region }} ({{ r.count }})</option></select>
          <select v-model="rSort" @change="rOrder='desc';fetchPlayers()">
            <option value="mitic">MITIC high→low</option>
            <option value="world_rank">World Rank</option>
            <option value="name">Name A–Z</option>
            <option value="mitic_traditional">Traditional MITIC</option>
            <option value="elo">ELO Rating</option>
            <option value="weekly_level">Weekly Level</option>
          </select>
          <span class="result">{{ rTotal }} players</span>
        </div>
        <div class="tbl-wrap"><table>
          <thead><tr><th @click="toggleSort('world_rank')" class="s"># <span class="dir">{{ sortArrow('world_rank') }}</span></th><th @click="toggleSort('name')" class="s">Name <span class="dir">{{ sortArrow('name') }}</span></th><th>Nickname</th><th @click="toggleSort('mitic')" class="s">MITIC <span class="dir">{{ sortArrow('mitic') }}</span></th><th @click="toggleSort('mitic_traditional')" class="s">Trad <span class="dir">{{ sortArrow('mitic_traditional') }}</span></th><th @click="toggleSort('elo')" class="s">ELO <span class="dir">{{ sortArrow('elo') }}</span></th><th>Location</th><th>Region</th><th @click="toggleSort('weekly_level')" class="s">Lvl <span class="dir">{{ sortArrow('weekly_level') }}</span></th></tr></thead>
          <tbody>
            <tr v-for="p in rData" :key="p.id" @click="openProfile(p)" class="clickable" :class="{wr:p.world_rank}">
              <td class="rk">{{ displayRank(p.world_rank) }}</td>
              <td class="nm">{{ p.name }}<span v-if="rankLabel(p.world_rank)" class="rk-label">{{ rankLabel(p.world_rank) }}</span></td>
              <td class="nk">{{ p.nickname || '—' }}</td>
              <td class="mt">{{ p.mitic ?? '—' }}</td>
              <td class="tr">{{ p.mitic_traditional ?? '—' }}</td>
              <td class="el">{{ p.elo ? Math.round(p.elo) : '—' }}</td>
              <td class="lc">{{ p.location || '—' }}</td>
              <td class="rg">{{ p.region || '—' }}</td>
              <td class="lv">{{ p.weekly_level ?? '—' }}</td>
            </tr>
          </tbody>
        </table></div>
        <Pagination :page="rPage" :total="rTotal" :per="50" @change="n=>{rPage=n;fetchPlayers()}" />
      </section>

      <!-- Profile Page -->
      <section v-if="page==='profile' && profileData">
        <header><h2>{{ profileData.name }}</h2><p class="sub">{{ profileData.location }} · {{ profileData.region }} · {{ profileData.hand }}-handed · {{ profileData.mallet }}</p></header>
        <div class="profile-grid">
          <div class="card stats">
            <h3>Ratings</h3>
            <dl><dt>World Rank</dt><dd>{{ displayRank(profileData.world_rank) || 'Unranked' }}<span v-if="rankLabel(profileData.world_rank)" class="rk-label-badge">{{ rankLabel(profileData.world_rank) }}</span></dd>
              <dt>MITIC</dt><dd class="num">{{ profileData.mitic ?? '—' }}</dd>
              <dt>MITIC Traditional</dt><dd class="num">{{ profileData.mitic_traditional ?? '—' }}</dd>
              <dt>ELO (New ElolE)</dt><dd class="num">{{ profileData.elo ? Math.round(profileData.elo) : '—' }}</dd>
              <dt>Weekly Level</dt><dd class="num">{{ profileData.weekly_level ?? '—' }}</dd>
              <dt>Shot %</dt><dd>{{ profileData.shot || '—' }}</dd>
              <dt>Defense %</dt><dd>{{ profileData.defense_pct != null ? profileData.defense_pct + '%' : '—' }}</dd>
            </dl>
          </div>
          <div class="card standings" v-if="profileStandings?.wrh || profileStandings?.weekly">
            <h3>Standings</h3>
            <dl v-if="profileStandings.wrh"><dt>WRH Rank</dt><dd>{{ profileStandings.wrh.wr || '—' }}</dd>
              <dt>WRH Points</dt><dd class="num">{{ profileStandings.wrh.points ?? '—' }}</dd>
              <dt>WRH Level</dt><dd>{{ profileStandings.wrh.level || '—' }}</dd></dl>
            <dl v-if="profileStandings.weekly"><dt>2026 Points</dt><dd class="num">{{ profileStandings.weekly.points ?? '—' }}</dd>
              <dt>2026 Level</dt><dd>{{ profileStandings.weekly.level || '—' }}</dd>
              <dt>Tournaments Played</dt><dd>{{ profileStandings.weekly.played || '—' }}</dd></dl>
          </div>
          <div class="card matches">
            <h3>Recent Challenge Matches</h3>
            <div v-if="profileMatches.length===0" class="empty">No matches recorded</div>
            <table v-else class="compact">
              <thead><tr><th>Opponent</th><th>Rating</th><th>Result</th><th>Score</th><th>Location</th></tr></thead>
              <tbody>
                <tr v-for="m in profileMatches" :key="m.id">
                  <td>{{ m.player1 === profileData.name ? m.player2 : m.player1 }}</td>
                  <td class="num">{{ m.player1 === profileData.name ? m.p1_rating : m.p2_rating }}</td>
                  <td :class="m.winner === profileData.name ? 'win' : 'loss'">{{ m.winner === profileData.name ? 'W' : 'L' }}</td>
                  <td>{{ m.total_p1 != null ? m.total_p1 + '-' + m.total_p2 : m.set1_p1 != null ? m.set1_p1 + '-' + m.set1_p2 : '—' }}</td>
                  <td class="loc">{{ m.location || '—' }}</td>
                </tr>
              </tbody>
            </table>
            <button v-if="profileMatchTotal > profileMatches.length" class="more" @click="loadMoreMatches()">Show more ({{ profileMatchTotal - profileMatches.length }} left)</button>
          </div>
          <div class="card tournaments">
            <h3>Tournament History</h3>
            <div v-if="profileTournaments.length===0" class="empty">No tournament data</div>
            <table v-else class="compact">
              <thead><tr><th>Event</th><th>Date</th><th>Rank</th></tr></thead>
              <tbody>
                <tr v-for="t in profileTournaments" :key="t.id">
                  <td>{{ t.event }}</td><td>{{ t.date }}</td><td class="num">{{ t.rank }}</td>
                </tr>
              </tbody>
            </table>
            <button v-if="profileTournTotal > profileTournaments.length" class="more" @click="loadMoreTournaments()">Show more ({{ profileTournTotal - profileTournaments.length }} left)</button>
          </div>
        </div>
        <button class="back" @click="page='rankings'">← Back to Rankings</button>
      </section>

      <!-- WRH Page -->
      <section v-if="page==='wrh'">
        <header><h2>World Ranking History</h2><p class="sub">Season points — 1st: 1pt · 2nd: 0.5pt · 3rd: 0.25pt · 4th: 0.1pt</p></header>
        <div class="tbl-wrap"><table>
          <thead><tr><th>WR</th><th>Player</th><th>Level</th><th>Points</th><th>Played</th><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th><th>Win %</th><th>Top 4 %</th></tr></thead>
          <tbody>
            <tr v-for="r in wrhData" :key="r.id" @click="findAndOpenProfile(r.player)" class="clickable">
              <td class="rk">{{ r.position ?? '—' }}</td>
              <td class="nm">{{ r.player }}</td>
              <td>{{ r.level || '—' }}</td>
              <td class="num">{{ r.points ?? '—' }}</td>
              <td>{{ r.played || '—' }}</td>
              <td class="num">{{ r.wins_1st || '—' }}</td>
              <td class="num">{{ r.second_2nd || '—' }}</td>
              <td class="num">{{ r.third_3rd || '—' }}</td>
              <td class="num">{{ r.fourth_4th || '—' }}</td>
              <td class="num">{{ r.win_pct != null ? (r.win_pct*100).toFixed(0) + '%' : '—' }}</td>
              <td class="num">{{ r.top4_pct != null ? (r.top4_pct*100).toFixed(0) + '%' : '—' }}</td>
            </tr>
          </tbody>
        </table></div>
        <Pagination :page="wrhPage" :total="wrhTotal" :per="100" @change="n=>{wrhPage=n;fetchWRH()}" />
      </section>

      <!-- 2026 Standings Page -->
      <section v-if="page==='standings'">
        <header><h2>2026 Weekly Standings</h2><p class="sub">Points: 1st=1pt · 2nd=0.5pt · 3rd=0.25pt · 4th=0.1pt</p></header>
        <div class="tbl-wrap"><table>
          <thead><tr><th>#</th><th>Player</th><th>Level</th><th>Points</th><th>Played</th><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th><th>Win %</th><th>Top 4 %</th></tr></thead>
          <tbody>
            <tr v-for="(r,i) in standingsData" :key="r.id" @click="findAndOpenProfile(r.player)" class="clickable">
              <td class="rk">{{ (standingsPage-1)*100 + i + 1 }}</td>
              <td class="nm">{{ r.player }}</td>
              <td>{{ r.level || '—' }}</td>
              <td class="num">{{ r.points ?? '—' }}</td>
              <td>{{ r.played || '—' }}</td>
              <td class="num">{{ r.wins_1st || '—' }}</td>
              <td class="num">{{ r.second_2nd || '—' }}</td>
              <td class="num">{{ r.third_3rd || '—' }}</td>
              <td class="num">{{ r.fourth_4th || '—' }}</td>
              <td class="num">{{ r.win_pct != null ? (r.win_pct*100).toFixed(0)+'%' : '—' }}</td>
              <td class="num">{{ r.top4_pct != null ? (r.top4_pct*100).toFixed(0)+'%' : '—' }}</td>
            </tr>
          </tbody>
        </table></div>
        <Pagination :page="standingsPage" :total="standingsTotal" :per="100" @change="n=>{standingsPage=n;fetchStandings()}" />
      </section>

      <!-- Challenge Matches Page -->
      <section v-if="page==='matches'">
        <header><h2>Challenge Matches</h2><p class="sub">{{ matchTotal }} reported games</p></header>
        <div class="filters">
          <input v-model="mSearch" placeholder="Search player name..." @input="debounce(()=>{mPage=1;fetchMatches()})" />
          <span class="result">{{ matchTotal }} matches</span>
        </div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Player 1</th><th>Rating</th><th>vs</th><th>Player 2</th><th>Rating</th><th>Winner</th><th>Score</th><th>Location</th><th>Date</th></tr></thead>
          <tbody>
            <tr v-for="m in matchData" :key="m.id" class="clickable" @click="findAndOpenProfile(m.winner)">
              <td class="nm">{{ m.player1 }}</td><td class="num">{{ m.p1_rating ?? '—' }}</td>
              <td>vs</td>
              <td class="nm">{{ m.player2 }}</td><td class="num">{{ m.p2_rating ?? '—' }}</td>
              <td class="win">{{ m.winner }}</td>
              <td>{{ m.total_p1 != null ? m.total_p1 + '-' + m.total_p2 : m.set1_p1 != null ? m.set1_p1 + '-' + m.set1_p2 : '—' }}</td>
              <td class="loc">{{ m.location || '—' }}</td>
              <td class="loc">{{ m.date ? new Date(m.date).toLocaleDateString() : '—' }}</td>
            </tr>
          </tbody>
        </table></div>
        <Pagination :page="mPage" :total="matchTotal" :per="100" @change="n=>{mPage=n;fetchMatches()}" />
      </section>

      <!-- Weekly Results Page -->
      <section v-if="page==='weeklies'">
        <header><h2>Weekly Results</h2><p class="sub">Houston 7-6 Friday weeklies</p></header>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Date</th><th>Players</th><th>Winner Lvl</th><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th><th>5-6</th><th>7-8</th><th>9-12</th><th>13-16</th></tr></thead>
          <tbody>
            <tr v-for="w in weeklyData" :key="w.id">
              <td>{{ w.date || '—' }}</td>
              <td>{{ w.player_count || '—' }}</td>
              <td>{{ w.winner_level || '—' }}</td>
              <td class="nm">{{ w.first || '—' }}</td>
              <td class="nm">{{ w.second || '—' }}</td>
              <td class="nm">{{ w.third || '—' }}</td>
              <td class="nm">{{ w.fourth || '—' }}</td>
              <td>{{ [w.c5_6, w.c5_6_a].filter(Boolean).join(', ') || '—' }}</td>
              <td>{{ [w.c7_8, w.c7_8_a].filter(Boolean).join(', ') || '—' }}</td>
              <td>{{ [w.c9_12, w.c9_12_a, w.c9_12_b, w.c9_12_c].filter(Boolean).join(', ') || '—' }}</td>
              <td>{{ [w.c13_16, w.c13_16_a, w.c13_16_b].filter(Boolean).join(', ') || '—' }}</td>
            </tr>
          </tbody>
        </table></div>
        <Pagination :page="weeklyPage" :total="weeklyTotal" :per="50" @change="n=>{weeklyPage=n;fetchWeeklies()}" />
      </section>

      <!-- Content Page -->
      <section v-if="page==='content'">
        <header><h2>{{ contentTitle }}</h2></header>
        <div class="content-body" v-for="item in contentData" :key="item.id || item._row_index">
          <div v-if="contentTable==='terminology'" class="term-card">
            <h3>{{ item.name }}</h3>
            <p>{{ item.definition }}</p>
            <a v-if="item.link" :href="item.link" target="_blank">Learn more →</a>
          </div>
          <div v-else-if="contentTable==='rules'" class="rule-card">
            <h3>{{ item.name }}</h3>
            <p>{{ item.details }}</p>
            <a v-if="item.link" :href="item.link" target="_blank">Download →</a>
          </div>
          <div v-else-if="contentTable==='shots'" class="shot-card">
            <h3>{{ item.name }}</h3>
            <p v-if="item.desc_1">{{ item.desc_1 }}</p>
            <p v-if="item.desc_2">{{ item.desc_2 }}</p>
          </div>
          <div v-else-if="contentTable==='ref_clinic'" class="ref-card">
            <h3>{{ item.title }}</h3>
            <p class="pre">{{ item.text }}</p>
            <a v-if="item.video" :href="item.video" target="_blank">Watch video →</a>
          </div>
          <div v-else-if="contentTable==='videos'" class="video-card">
            <h3>{{ item.name }}</h3>
            <p>{{ item.desc }}</p>
            <a v-if="item.link" :href="item.link" target="_blank">Watch →</a>
          </div>
          <div v-else-if="contentTable==='news'" class="news-card">
            <h3>{{ item.title }}</h3>
            <p class="date">{{ item.date }}</p>
            <p>{{ item.details }}</p>
          </div>
          <div v-else class="card">
            <pre>{{ item }}</pre>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
const BASE = import.meta.env.BASE_URL || '/';

export default {
  data: () => ({
    page: 'rankings', status: null, regions: [],
    // rankings
    rData: [], rTotal: 0, rPage: 1, rSearch: '', rRegion: '', rSort: 'mitic', rOrder: 'desc',
    // profile
    profileData: null, profilePlayer: null, profileMatches: [], profileMatchTotal: 0,
    profileTournaments: [], profileTournTotal: 0, profileStandings: null, pmPage: 1, ptPage: 1,
    // WRH
    wrhData: [], wrhTotal: 0, wrhPage: 1,
    // standings
    standingsData: [], standingsTotal: 0, standingsPage: 1,
    // matches
    matchData: [], matchTotal: 0, mPage: 1, mSearch: '',
    // weeklies
    weeklyData: [], weeklyTotal: 0, weeklyPage: 1,
    // content
    contentTable: '', contentData: [],
    // debounce
    _timer: null,
    _staticCache: {},
  }),
  computed: {
    contentTitle() { const t = this.contentTable; return { terminology:'Terminology', rules:'Rules', shots:'Shots Library', ref_clinic:'Referee Clinic', videos:'Videos', news:'News' }[t] || t; }
  },
  methods: {
    displayRank(r) {
      if (!r || r === null || r === '') return '—';
      const s = String(r).replace(/\u00A0/g, '').trim();
      if (s === 'Unranked') return '—';
      const parts = s.split(' ');
      if (parts.length === 2 && /^[A-Z]{2,4}$/.test(parts[0]) && /^\d+$/.test(parts[1]))
        return parts[1];
      return s;
    },
    rankLabel(r) {
      if (!r) return null;
      const s = String(r).replace(/\u00A0/g, '').trim();
      const parts = s.split(' ');
      if (parts.length === 2 && /^[A-Z]{2,4}$/.test(parts[0]) && /^\d+$/.test(parts[1]))
        return parts[0];
      return null;
    },
    toggleSort(col) {
      if (this.rSort === col) this.rOrder = this.rOrder === 'desc' ? 'asc' : 'desc';
      else { this.rSort = col; this.rOrder = 'desc'; }
      this.fetchPlayers();
    },
    sortArrow(col) {
      if (this.rSort !== col) return '';
      return this.rOrder === 'desc' ? '▼' : '▲';
    },
    debounce(fn) { clearTimeout(this._timer); this._timer = setTimeout(fn, 250); },
    async api(path) {
      // Try the API first; fall back to static JSON files
      try {
        const r = await fetch(BASE + 'api/' + path.split('?')[0].split('/').slice(1).join('/'));
        if (r.ok && r.status !== 404) return await r.json();
      } catch {}
      // Static fallback: map the path to a JSON file
      return await this._staticQuery(path);
    },
    async _staticQuery(path) {
      const qs = path.includes('?') ? Object.fromEntries(new URLSearchParams(path.split('?')[1])) : {};
      const parts = path.split('?')[0].split('/').filter(Boolean); // e.g. ['players','1','matches']

      // Load a JSON file once, cache it
      const loadJson = async (file) => {
        if (this._staticCache[file]) return this._staticCache[file];
        const r = await fetch(BASE + 'data/' + file + '.json');
        if (!r.ok) return [];
        const data = await r.json();
        this._staticCache[file] = data;
        return data;
      };

      // /api/players/:id/matches
      if (parts[0] === 'players' && parts[2] === 'matches') {
        const all = await loadJson('matches');
        const playerRow = await this._staticQuery(`players/${parts[1]}`);
        const name = playerRow?.name;
        if (!name) return { total: 0, data: [] };
        const filtered = all.filter(m => m.player1 === name || m.player2 === name);
        const o = +qs.offset || 0, l = +qs.limit || 50;
        return { total: filtered.length, data: filtered.slice(o, o + l), player: name };
      }
      // /api/players/:id/tournaments
      if (parts[0] === 'players' && parts[2] === 'tournaments') {
        const all = await loadJson('tournament_results');
        const playerRow = await this._staticQuery(`players/${parts[1]}`);
        const name = playerRow?.name;
        if (!name) return { total: 0, data: [] };
        const filtered = all.filter(t => t.player === name).sort((a, b) => (b.date || '').localeCompare(a.date || ''));
        const o = +qs.offset || 0, l = +qs.limit || 50;
        return { total: filtered.length, data: filtered.slice(o, o + l), player: name };
      }
      // /api/players/:id/standings
      if (parts[0] === 'players' && parts[2] === 'standings') {
        const playerRow = await this._staticQuery(`players/${parts[1]}`);
        const name = playerRow?.name;
        if (!name) return { player: '' };
        const wrh = await loadJson('standings');
        const weekly = await loadJson('standings');
        const parts2 = name.split(' ');
        const alt = parts2.length >= 2 ? `${parts2[parts2.length-1]}, ${parts2.slice(0,-1).join(' ')}` : name;
        return {
          player: name,
          wrh: wrh.find(r => (r.player === name || r.player === alt) && r.season === 'WRH') || null,
          weekly: weekly.find(r => (r.player === name || r.player === alt) && r.season === '2026') || null,
        };
      }
      // /api/players/:id
      if (parts[0] === 'players' && parts.length === 2) {
        const all = await loadJson('players');
        const id = +parts[1];
        return all.find(p => p.id === id) || null;
      }
      // /api/players?...
      if (parts[0] === 'players') {
        let all = await loadJson('players');
        if (qs.search) {
          const q = qs.search.toLowerCase();
          all = all.filter(p => (p.name||'').toLowerCase().includes(q) || (p.nickname||'').toLowerCase().includes(q) || (p.location||'').toLowerCase().includes(q));
        }
        if (qs.region) all = all.filter(p => p.region === qs.region);
        if (qs.min_mitic) all = all.filter(p => +(p.mitic||0) >= +qs.min_mitic);
        if (qs.max_mitic) all = all.filter(p => +(p.mitic||0) <= +qs.max_mitic);
        const sc = qs.sort || 'mitic';
        const sd = qs.order === 'asc' ? 1 : -1;
        all.sort((a, b) => {
          const va = a[sc], vb = b[sc];
          if (va == null) return 1; if (vb == null) return -1;
          return va > vb ? sd : va < vb ? -sd : 0;
        });
        const o = +qs.offset || 0, l = +qs.limit || 100;
        return { total: all.length, data: all.slice(o, o + l), offset: o, limit: l };
      }
      // /api/wrh → standings filtered by season='WRH'
      if (parts[0] === 'wrh') {
        let all = await loadJson('standings');
        all = all.filter(s => s.season === 'WRH');
        const sc = qs.sort || 'position';
        const sd = qs.order === 'asc' ? 1 : -1;
        all.sort((a, b) => {
          const va = a[sc], vb = b[sc];
          if (va == null) return 1; if (vb == null) return -1;
          return va > vb ? sd : va < vb ? -sd : 0;
        });
        const o = +qs.offset || 0, l = +qs.limit || 100;
        return { total: all.length, data: all.slice(o, o + l), offset: o, limit: l };
      }
      // /api/standings → filter by season='2026'
      if (parts[0] === 'standings') {
        const all = await loadJson('standings');
        const filtered = all.filter(s => s.season === '2026');
        filtered.sort((a, b) => (b.points||0) - (a.points||0));
        const o = +qs.offset || 0, l = +qs.limit || 100;
        return { total: filtered.length, data: filtered.slice(o, o + l), offset: o, limit: l };
      }
      // /api/weeklies
      if (parts[0] === 'weeklies') {
        const all = await loadJson('weeklies');
        all.sort((a, b) => (b.id||0) - (a.id||0));
        const o = +qs.offset || 0, l = +qs.limit || 50;
        return { total: all.length, data: all.slice(o, o + l), offset: o, limit: l };
      }
      // /api/tables/:table
      if (parts[0] === 'tables') {
        const all = await loadJson(parts[1]);
        const o = +qs.offset || 0, l = +qs.limit || 100;
        return { total: all.length, data: all.slice(o, o + l), offset: o, limit: l };
      }
      // /api/regions
      if (parts[0] === 'regions') return await loadJson('regions');
      // /api/content/:table
      if (parts[0] === 'content') {
        const data = await loadJson(parts[1]);
        return { total: data.length, data };
      }
      // /api/status
      if (parts[0] === 'status') {
        return { ok: true, meta: { archived_at: new Date().toISOString() }, tables: [] };
      }
      return {};
    },
    async fetchPlayers() {
      const p = new URLSearchParams({ limit: 50, offset: (this.rPage-1)*50, sort: this.rSort, order: this.rOrder });
      if (this.rSearch) p.set('search', this.rSearch);
      if (this.rRegion) p.set('region', this.rRegion);
      const j = await this.api('/players?'+p);
      this.rData = j.data; this.rTotal = j.total;
    },
    async openProfile(p) {
      this.profilePlayer = p.name; this.profileData = p; this.pmPage = 1; this.ptPage = 1;
      this.page = 'profile';
      const [matches, tournaments, standings] = await Promise.all([
        this.api(`/players/${p.id}/matches?limit=20`),
        this.api(`/players/${p.id}/tournaments?limit=20`),
        this.api(`/players/${p.id}/standings`),
      ]);
      this.profileMatches = matches.data || [];
      this.profileMatchTotal = matches.total || 0;
      this.profileTournaments = tournaments.data || [];
      this.profileTournTotal = tournaments.total || 0;
      this.profileStandings = standings;
    },
    async findAndOpenProfile(name) {
      if (!name) return;
      const j = await this.api(`/players?search=${encodeURIComponent(name)}&limit=1`);
      if (j.data?.length) { await this.openProfile(j.data[0]); }
    },
    async loadMoreMatches() {
      const j = await this.api(`/players/${this.profileData.id}/matches?offset=${this.profileMatches.length}&limit=50`);
      this.profileMatches = [...this.profileMatches, ...(j.data||[])];
      this.profileMatchTotal = j.total;
    },
    async loadMoreTournaments() {
      const j = await this.api(`/players/${this.profileData.id}/tournaments?offset=${this.profileTournaments.length}&limit=50`);
      this.profileTournaments = [...this.profileTournaments, ...(j.data||[])];
      this.profileTournTotal = j.total;
    },
    async fetchWRH() {
      const p = new URLSearchParams({ limit: 100, offset: (this.wrhPage-1)*100 });
      const j = await this.api('/wrh?'+p);
      this.wrhData = j.data; this.wrhTotal = j.total;
    },
    async fetchStandings() {
      const p = new URLSearchParams({ limit: 100, offset: (this.standingsPage-1)*100 });
      const j = await this.api('/standings?'+p);
      this.standingsData = j.data; this.standingsTotal = j.total;
    },
    async fetchMatches() {
      const p = new URLSearchParams({ limit: 100, offset: (this.mPage-1)*100 });
      if (this.mSearch) p.set('search', this.mSearch);
      const j = await this.api('/tables/challenge_match?'+p);
      this.matchData = j.data; this.matchTotal = j.total;
    },
    async fetchWeeklies() {
      const p = new URLSearchParams({ limit: 50, offset: (this.weeklyPage-1)*50 });
      const j = await this.api('/weeklies?'+p);
      this.weeklyData = j.data; this.weeklyTotal = j.total;
    },
    async openContent(table) {
      this.contentTable = table;
      this.page = 'content';
      const j = await this.api('/content/'+table);
      this.contentData = j.data || [];
    },
  },
  async mounted() {
    this.status = await this.api('/status');
    this.regions = await this.api('/regions');
    await this.fetchPlayers();
  },
  components: { Pagination: { props: ['page','total','per'], emits: ['change'],
    template: '<div class="pagination"><button :disabled="page<=1" @click="$emit(\'change\',page-1)">←</button><span>{{page}} / {{Math.ceil(total/per)||1}}</span><button :disabled="page>=Math.ceil(total/per)" @click="$emit(\'change\',page+1)">→</button></div>'}}
}
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1117; color: #e1e4e8; }
.app { display: flex; min-height: 100vh; }
.sidebar { width: 240px; background: #161b22; border-right: 1px solid #30363d; padding: 16px; display: flex; flex-direction: column; flex-shrink: 0; overflow-y: auto; }
.sidebar h1 { font-size: 1.2rem; color: #f0c040; cursor: pointer; margin-bottom: 20px; }
nav a { display: block; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; color: #c9d1d9; text-decoration: none; margin: 1px 0; }
nav a:hover { background: #1c2128; }
nav a.active { background: #1c2128; color: #f0c040; }
.nav-group { margin-bottom: 16px; }
.nav-head { display: block; font-size: 0.7rem; color: #6e7681; text-transform: uppercase; letter-spacing: 0.05em; padding: 0 8px; margin-bottom: 4px; }
.meta { margin-top: auto; padding-top: 12px; font-size: 0.75rem; color: #6e7681; }

.content { flex: 1; padding: 24px; overflow-y: auto; max-width: calc(100vw - 240px); }
header { margin-bottom: 16px; }
header h2 { font-size: 1.4rem; color: #f0c040; }
.sub { color: #8b949e; font-size: 0.85rem; }

.filters { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; align-items: center; }
.filters input, .filters select { padding: 7px 10px; border: 1px solid #30363d; border-radius: 6px; background: #161b22; color: #e1e4e8; font-size: 0.85rem; }
.filters input { flex: 1; min-width: 180px; }
.result { color: #6e7681; font-size: 0.8rem; margin-left: auto; }

.tbl-wrap { border: 1px solid #30363d; border-radius: 8px; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
th { background: #161b22; padding: 8px 10px; text-align: left; font-weight: 600; color: #8b949e; border-bottom: 1px solid #30363d; white-space: nowrap; }
th.s { cursor: pointer; user-select: none; }
th.s:hover { color: #f0c040; }
.dir { font-size: 0.6rem; color: #6e7681; }
td { padding: 6px 10px; border-bottom: 1px solid #21262d; white-space: nowrap; }
tr:last-child td { border-bottom: none; }
tr:hover { background: #1c2128; }
.clickable { cursor: pointer; }
.wr { border-left: 3px solid #f0c040; }
.rk { color: #f0c040; font-weight: 700; text-align: center; width: 40px; }
.rk-label { display: inline-block; font-size: 0.65rem; background: #30363d; color: #8b949e; border-radius: 3px; padding: 0 4px; margin-left: 4px; vertical-align: middle; }
.rk-label-badge { display: inline-block; font-size: 0.7rem; background: #30363d; color: #f0c040; border-radius: 4px; padding: 0 5px; margin-left: 6px; vertical-align: middle; }
.nm { font-weight: 600; }
.nk { color: #8b949e; font-size: 0.78rem; }
.mt, .tr, .el, .num { font-family: 'SF Mono', 'Fira Code', monospace; font-weight: 600; color: #58a6ff; }
.tr { color: #bc8cff; }
.el { color: #3fb950; }
.lc, .loc, .rg { color: #8b949e; font-size: 0.78rem; }
.win { color: #3fb950; font-weight: 600; }
.loss { color: #f85149; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 14px; }
.pagination button { padding: 5px 14px; border: 1px solid #30363d; border-radius: 6px; background: #161b22; color: #e1e4e8; cursor: pointer; font-size: 0.85rem; }
.pagination button:hover:not(:disabled) { border-color: #f0c040; }
.pagination button:disabled { opacity: 0.3; cursor: default; }

/* Profile */
.profile-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 16px; margin-bottom: 20px; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; }
.card h3 { font-size: 0.95rem; color: #f0c040; margin-bottom: 10px; }
.card dl { display: grid; grid-template-columns: auto 1fr; gap: 4px 16px; }
.card dt { color: #8b949e; font-size: 0.82rem; }
.card dd { font-size: 0.85rem; }
.empty { color: #6e7681; font-style: italic; font-size: 0.85rem; padding: 10px 0; }
.compact td { padding: 4px 8px; font-size: 0.78rem; }
.more, .back { margin-top: 8px; padding: 6px 14px; border: 1px solid #30363d; border-radius: 6px; background: transparent; color: #58a6ff; cursor: pointer; font-size: 0.8rem; }
.more:hover, .back:hover { border-color: #f0c040; }

/* Content */
.content-body { margin-bottom: 12px; }
.content-body h3 { font-size: 1rem; color: #f0c040; margin-bottom: 4px; }
.content-body p { color: #c9d1d9; font-size: 0.85rem; line-height: 1.5; }
.content-body p.date { color: #6e7681; font-size: 0.78rem; }
.content-body a { color: #58a6ff; font-size: 0.82rem; }
.content-body a:hover { color: #f0c040; }
p.pre { white-space: pre-wrap; }
.term-card, .rule-card, .shot-card, .ref-card, .video-card, .news-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 14px; margin-bottom: 8px; }
</style>
