# Airhockeyrank.com — Technical Analysis

## Platform

The site is built with **Glide** (glideapps.com), a no-code platform. Specifically the newer "Glide Pages" engine (not the classic Glide). Evidence:

- Webpack bundle named `glide` (`this.webpackJsonpglide`)
- `window.glideEnv = "prod"`
- URL pattern: `/api/container/playerFunctionCritical/getAppSnapshot` etc.
- `glide-page-metadata` Firebase Cloud Function used for page metadata

## Hosting

Entirely on **Firebase / Google Cloud Platform**:

| Layer | Service |
|---|---|
| Frontend static files | Google Cloud Storage (served via Firebase Hosting) |
| Real-time data | Firestore (`glide-prod` database) |
| Images / uploads | Firebase Storage |
| Backend API | Cloud Functions (proxied through Fly.io) |
| Custom domain | Glide's custom domain feature → GCS bucket |
| PWA | Workbox-based service worker |

## Frontend

- **React SPA** (Glide-generated output, heavily chunked — 70+ JS files)
- **Webpack** bundled, **Styled Components** for CSS
- **Workbox** service worker with precaching + runtime caching
- **PWA** with app icon, splash screen, offline support

## Observability & Analytics

| Tool | Use |
|---|---|
| Google Analytics (G-405XNRW6Y6) | Page views, events |
| Honeycomb (`api.honeycomb.io`) | Backend tracing |
| Intercom | In-app chat support |
| Datadog RUM | Configured but likely inactive for published app |

## Data Layer

The app has **62 tables** in its schema. Most sync from **Google Sheets** (the sheet IDs are embedded in the app snapshot), with some using **Glide Big Tables** for high-volume data.

### Key Tables

| Table | Rows | Description |
|---|---|---|
| **TX Weekly Regulars** | 1,998 | Main player database — MITIC ratings, ELO, profiles |
| **Challenge Match** | 15,127 | Individual match results (feeds ELO calculation) |
| **PEA** | 6,235 | Tournament performance data |
| **Users** | 583 | App user accounts |
| **News** | 520 | News feed items |
| **Events** | 256 | Tournament/event records |
| **2026 Weekly Data** | 184 | Current year weekly stats |
| **WRH** | 185 | World ranking history |
| **Weekly Performance** | 110 | Weekly tournament breakdowns |
| **Hybrid Seeding** | 386 | Tournament seeding data |
| Various regional tables | — | Texas, Houston, Arizona, Idaho, Chicago, etc. |

### Main Table: "TX Weekly Regulars" (~50 columns)

| Column | Description |
|---|---|
| `name` | Player full name |
| `nickname` | Player nickname |
| `mitic` | MITIC rating (current system) |
| `mitic traditional` | Legacy MITIC rating |
| `New ElolE` | Elo-based rating |
| `rank` | World ranking position |
| `location` | City, State |
| `region` | Region code |
| `Country` | Country flag reference |
| `hand` | Left / Right handed |
| `mallet` | Mallet type / brand |
| `shot` | Shot percentage |
| `defense %` | Defense percentage |
| `weekly level` | Weekly skill tier |
| `world rank` | Boolean — is world-ranked |
| `group` | Player group (regular / rookie / etc.) |
| `Mitic Ranking` | Computed rank within MITIC |
| `profilepic` | Profile image URL |

### Regions (4)

| Code | Players | Description |
|---|---|---|
| AMR | 1,967 | Americas |
| RU | 24 | Russia |
| VEN | 6 | Venezuela |
| EU | 1 | Europe |

## Authentication

- **Public app** with optional sign-in ("public-email-pin" method)
- Anonymous users get a device ID stored in `localStorage` (`glide-device-id`)
- Supports Google Sign-In
- Plan: **Business 2023** (paid tier)

## Data Flow

1. Data originates in **Google Sheets** (or Glide Big Tables)
2. Glide syncs it into **Firestore** (its internal data layer)
3. When a user visits the site, these API calls are made:

| Endpoint | Purpose |
|---|---|
| `getAppEminence` | Check plan permissions / feature flags |
| `getAppSnapshot` | Returns a **signed GCS URL** to a 45 MB base64-encoded JSON snapshot |
| `ensureDataLiveliness` | Triggers data refresh if stale |
| `getQuotaStateForApp` | Usage / rate-limit info |
| `runIntegrations` | Runs connected plugin integrations |

4. The browser downloads the snapshot from the signed GCS URL, **decodes the base64**, and renders everything client-side
5. Real-time updates come through a **Firestore Listen** WebSocket channel

The signed snapshot URLs expire, so you can't bookmark them — must go through the Glide API each time.

## What is MITIC?

MITIC is a custom rating/ranking system for air hockey players (analogous to ELO but air-hockey-specific). The DB carries two parallel systems:

- **MITIC** — the current/modern rating
- **MITIC traditional** — legacy rating
- **New ElolE** — their own ELO implementation

The system is fed by weekly tournament results and challenge matches (15k+ match records). It tracks performances across multiple regional circuits (Texas weekly tournaments, Houston weeklies, Arizona events, Venezuelan tournaments, Russian events) plus major championships (Worlds, USAA, Carter Cup).

## App Metadata

| Field | Value |
|---|---|
| App ID | `lSodCWNYYaS4Z0uAwjuZ` |
| Quota ID | `KX4yq3OhBgQbu1sxWX9q` |
| Published | 2026-06-17 |
| Plan | Business 2023 (~$249/yr equivalent) |
| Editors | 25 |
| Total rows | 25,959 |
| Public users | Up to 10,000 |
| File storage | 5 GB used |
