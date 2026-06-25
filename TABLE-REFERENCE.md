# MITIC Archive — Table Reference

Complete documentation of all 31 tables archived from airhockeyrank.com.

## How tables map

The original Glide app had 62 tables in its schema, but only 31 actually contain data. The rest are empty schemas that were never used. Table names were sanitised during archival (spaces → underscores, lowercase), and hashed Glide column IDs (`7f5258906b9be1c26357da2cc516fc4b`) were preserved as-is since their meaning isn't recoverable.

---

## Core Player Data

### `tx_weekly_regulars` — 1,998 rows

The master player database. Every player who has ever participated in a ranked weekly tournament, with their ratings and stats.

| Column | Description |
|---|---|
| `name` | Player full name |
| `nickname` | Nickname / alias |
| `rank` | Current world ranking position (1 = top) |
| `mitic` | MITIC rating (current system) |
| `mitic_traditional` | Legacy MITIC rating |
| `new_elole` | Elo-based rating |
| `location` | City, State |
| `region` | Region code (AMR / RU / VEN / EU) |
| `country` | Two-letter country code |
| `hand` | Left / Right handed |
| `mallet` | Mallet type / brand (e.g. HighTop) |
| `shot` | Shot percentage (e.g. "65%") |
| `defense` | Defense percentage (e.g. "58.50%") |
| `weekly_level` | Weekly skill tier (1–7+) |
| `world_rank` | Boolean — 1 if world-ranked |
| `group` | Player group: "regular", "rookie", etc. |
| `mitic_ranking` | Computed rank by MITIC score |
| `mitrnk` | Alternate MITIC rank |
| `w_rank` | Legacy world rank number |
| `doubles_rank` | Doubles team rank |
| `doubles_team` | Doubles team name |
| `carter_cup_team` | Carter Cup team affiliation |
| `usaa_vote` | USAA voting status (Senior, etc.) |
| `usaa_sort` | USAA ranking sort order |
| `usaa_last_meetings` | Last USAA events attended |
| `usaa_last_moves` | Last ranking movements |
| `chi_rank` | Chicago regional rank |
| `texas_rank` | Texas regional rank |
| `arizona_rank` | Arizona regional rank |
| `idaho_rank` | Idaho regional rank |
| `cali_rank` | California regional rank |
| `houston_city_rank` | Houston city rank |
| `mw_rank` | Midwest regional rank |
| `chicago_level` | Chicago skill level |
| `idaho_level` | Idaho skill level |
| `idaho_elo` | Idaho-format Elo rating |
| `espn_rank` | ESPN rankings position |
| `espn_doubles_rank` | ESPN doubles rank |
| `espn_doubles_team_name` | ESPN doubles team name |
| `lns_2019` | Last name sort (2019 system) |
| `alphabetical` | Name formatted for sorting (e.g. "Cummings, Colin") |
| `old_ranks` | Previous ranking positions |
| `old_rank_2025` | Rank at start of 2025 |
| `old_rank_2023` | Rank at start of 2023 |
| `history` | Player history / bio text |
| `halloffame` | Hall of Fame status |
| `hofyear` | Year inducted into HoF |
| `retired` | Whether player is retired |
| `deceased` | Whether player is deceased |
| `activevsinactive` | Whether currently active |
| `interview` | Video interview link |
| `interview_tim` | Alternate interview link |
| `profilepic` | Profile image URL |
| `pic_2` | Secondary image URL |
| `pic_3` | Tertiary image URL |
| `country_flag` | Country flag image URL |
| `local_flag` | Regional flag image URL |
| `start_date` | When the player started competing |
| `days_playing` | How long they've played |
| `points_spot` | Points pot / spot (unknown metric) |
| `fn1` | Unknown boolean flag |
| `100club` | 100 Club membership |
| `200club` | 200 Club membership |
| `300club` | 300 Club membership |
| `column11` | "56+" — age or experience category? |
| `column50` | Unknown numeric field |
| `column51` | Unknown numeric field |
| `column54` | Unknown text field |
| `column61` | Unknown text field |
| `column76` | Unknown text field |
| `c45de0c466b11ea667a1da9822c195b4d` | Unknown rating value (e.g. "2167.3541") |
| Doubles tournament columns | `c2021_doubles_team`, `c2021_doubles_rank`, `c2021_doubles_order`, `c2022_doubles_team`, `c2022_doubles_rank`, `c2023_doubles_team`, `c2023_doubles_rank`, `c2023_doubles_finish`, `c2024_doubles_finish`, `c2024_doubles_finish_a`, `c2024_doubles_link`, `c2024_doubles_sort`, `c2025_doubles_link`, `c2025_doubles_sort`, `c2025_doubles_sort_a` |
| Women's tournament columns | `c2023_womens_order`, `c2024_womens_finish`, `c2024_womens_sort`, `c2025_womens_finish`, `c2025_womens_sort` |
| Various | `lmu_1` through `lmu_7`, `lmu_date`, `vs`, `ext_links`, `ext_link_desc`, `rating_notes`, `notes`, `alt_name`, `officer_type`, `usaa_officer`, `usaa_dues`, `nc_finish`, `houston_city_finish` |

### `users` — 583 rows

App user accounts — players who signed in to the Glide app.

| Column | Description |
|---|---|
| `name` | Display name |
| `email` | Email address |
| `cell` | Phone number |
| `image` | Profile image URL |
| `location` | Geocoordinates (lat, lng) |
| `hand` | Left / Right handed |
| `mallet` | Mallet type |
| `nickname` | Nickname |
| `surname` | Last name |
| `age` | Age |
| `gender` | Gender (M / F) |
| `bio` | Biography text |
| `administrator` | Admin role ("admin" or null) |
| `misc_access` | Misc permissions ("quickaccess") |
| `weekly_level` | Weekly skill level |
| `chicago_level` | Chicago skill level |
| `regulars` | Whether a regular attendee |
| `booth` | Booth duty assignment |
| `late_reg` / `l2reg` | Late registration flags |
| `vote` | Voting eligibility |
| `usaa` | USAA member |
| `ahpa` | AHPA member |
| `fav_table` | Favourite table type |
| `fav_mallet` | Favourite mallet |
| `fav_puck` | Favourite puck colour |
| `fav_puck_tape` | Favourite tape setup |
| `string` | String preference |
| `c76_poll` | Poll response for table preference |

---

## Match Data

### `challenge_match` — 15,127 rows

Individual challenge matches — the core match result database used to compute ELO/MITIC ratings. Covers 2020 to present.

| Column | Description |
|---|---|
| `player_1` | Challenger name |
| `p1_rank` | Challenger rank at time of match |
| `p1_rating` | Challenger rating at time of match |
| `player_2` | Opponent name |
| `p2_rank` | Opponent rank at time of match |
| `p2_rating` | Opponent rating at time of match |
| `winner` | Name of the winning player |
| `set_1` | Set 1 score (e.g. "4-2" = P1 won 4 games to 2) |
| `set_2` | Set 2 score |
| `set_3` | Set 3 score |
| `set_4` | Set 4 score |
| `set_5` | Set 5 score |
| `set_6` | Set 6 score |
| `set_7` | Set 7 score |
| `column9` | Total game count (e.g. "12-4") |
| `kvc` | "Best of" format (e.g. "3 out of 5 sets") |
| `ref` | Referee name |
| `puck_color` | Puck colour used |
| `location` | Venue name |
| `column1` | Match date (ISO 8601) |
| `column7` | Photo/image URL |
| `archive` | Whether the match is archived |
| `email` | Anonymous user email of reporter |
| `old_math` | Whether computed under old system |
| `percentage_p1_win` | Win probability for P1 (Elo-based) |
| `percentage_p2_win` | Win probability for P2 |
| `percentage_p2_winbk` | Duplicate win probability (backup) |
| `other_location` | Numeric value tied to venue (maybe 0-1 indicator) |
| `player` | Internal Glide array ref (P1 + P2) |

Hashed columns (e.g. `c7f5258906b9be1c26357da2cc516fc4b`) are individual games within sets, e.g. set 1 game 1 score "7-3". The pattern suggests up to 7 games per set, and the hashed IDs are auto-generated Glide column IDs for repeated computed/input columns.

### `last_5` — 5 rows

Most recent 5 challenge matches. Same schema as `challenge_match` but limited to very recent entries, possibly a summary view.

---

## Tournament / Event History

### `pea` (Player Event Archive) — 6,235 rows

Historical tournament results going back to **1973**. Every tournament finish for every player.

| Column | Description |
|---|---|
| `event` | Tournament name (e.g. "1973 Valley Forge", "2023 Worlds") |
| `date` | Tournament date |
| `player` | Player name |
| `rank` | Finishing position (1 = winner) |
| `avgrank` | Average rank across all events |

### `events` — 256 rows

Tournament event calendar — primarily Houston Weekly tournaments from 2020 onward, plus special events.

| Column | Description |
|---|---|
| `title` | Event name (e.g. "Houston Weekly 8/14/2020") |
| `date` | Event date/time |
| `location` | Venue code (e.g. "7-6") |
| `address` | Street address |
| `description` | Event description text |
| `misc` | Additional info ("Win Cash! Beginners play free!...") |
| `cell` | Contact phone |
| `image` / `image2` | Event images |
| `sent_sms` | Text of SMS notification sent |
| `archive` | Whether the event is archived |

### `weekly_performance` — 110 rows

Weekly tournament bracket results — who finished where each week.

| Column | Description |
|---|---|
| `c7_6_friday` | Week date (e.g. "3-Jan") |
| `player_count` | Number of participants |
| `winner_level` | Skill level of the winner |
| `c1st` | 1st place finisher name |
| `c2nd` | 2nd place |
| `c3rd` | 3rd place |
| `c4th` | 4th place |
| `c5_6` / `c5_6_a` | 5th–6th place finishers |
| `c7_8` / `c7_8_a` | 7th–8th place |
| `c9_12` / `c9_12_a` / `c9_12_b` / `c9_12_c` | 9th–12th place |
| `c13_16` / `c13_16_a` / `c13_16_b` / `c13_16_c` | 13th–16th place |
| `c17_24` through `c17_24_g` | 17th–24th place |
| `c25_32` through `c25_32_d` | 25th–32nd place |

### `2026_weekly_data` (table: `c2026_weekly_data`) — 184 rows

Current season (2026) points standings for the weekly circuit.

**Points system:**

| Place | Points |
|---|---|
| 1st | 1.0 |
| 2nd | 0.5 |
| 3rd | 0.25 |
| 4th | 0.10 |

These are the per-tournament awards. The total `points` column appears to be a cumulative sum of (1st_count × 1.0 + 2nd_count × 0.5 + 3rd_count × 0.25 + 4th_count × 0.10). The `points_needed` column tracks how many more points a player needs to advance to the next level. The `c0edce5...` column appears to be a derived metric — possibly points per tournament or a normalised score.

| Column | Description |
|---|---|
| `player_name` | Player name |
| `level` | Skill level |
| `points` | Total season points |
| `c1st` | Number of 1st place finishes |
| `c2nd` | Number of 2nd place finishes |
| `c3rd` | Number of 3rd place finishes |
| `c4th` | Number of 4th place finishes |
| `played` | Number of tournaments played |
| `win` | Win percentage |
| `top_4` | Top-4 finish percentage |
| `toc_seed` | Tournament of Champions seed |
| `first_weekly` | Year of first weekly tournament |
| `total_weeklys` | Total weekly tournaments attended |
| `levels` | Levels achieved |
| `points_needed` | Points needed for next level |
| `first` / `second` / `third` / `fourth` | Points awarded for each placing |

### `wrh` (World Ranking History) — 185 rows

Season-long points-based world rankings — the "WRH" system.

**Points system:** Same as the weekly circuit — 1.0 for 1st, 0.5 for 2nd, 0.25 for 3rd, 0.10 for 4th. The column labels `c1st_a` etc. spell this out explicitly ("1 Point", ".5 points", ".25 points", ".10 points"). The `c0edce5...` column is likely a normalised or per-event score.

| Column | Description |
|---|---|
| `player_name` | Player name (last, first format) |
| `wr` | World ranking position |
| `level` | Skill level |
| `points` | Total points this season |
| `played` | Tournaments played |
| `c1st` | 1st place finishes |
| `c2nd` | 2nd place finishes |
| `c3rd` | 3rd place finishes |
| `c4th` | 4th place finishes |
| `win` | Win percentage |
| `top_4` | Top-4 finish percentage |
| `total_weekly_s` | Total weekly tournaments ever |
| `first_weekly` | Year of first weekly |
| `level_a` | Alternate level computation |
| `points_needed` | Points to next level |
| `c1st_a` / `c2nd_a` / `c3rd_a` / `c4th_a` | Points awarded per placing |
| `column1` | Numeric sort order |

### `cartercup_history` — 6 rows

Carter Cup team competition history.

| Column | Description |
|---|---|
| `dates` | Date range of the competition (e.g. "Dec 92 - Apr 95") |
| `team_name` | Team name (e.g. "The Fabulous Four") |

---

## Seeding & Rankings

### `hybrid_seeding` — 386 rows

Tournament seeding that combines multiple ranking systems.

| Column | Description |
|---|---|
| `player` | Player name |
| `seed` | Tournament seed position |
| `world_ranking` | World ranking used for seeding |
| `new_elole` | Elo rating (stored as image URL in original — probably a Glide display quirk) |
| `levels` | Skill level designation (e.g. "Level 7") |
| `registered` | Whether registered for the tournament |
| `column_7` | Unknown integer |

---

## Weekly Signup & Admin

### `weekly_signup` — 51 rows

Player signups for weekly tournaments.

| Column | Description |
|---|---|
| `name` | Player name |
| `weekly_rank` | Their current rank at signup |
| `weeklytitle` | Which weekly they signed up for |
| `email` | Contact email |
| `cell` | Phone number |
| `date` | Signup date |
| `sms` | Whether SMS was sent |

### `weekly_top_4` — 21 rows

Unknown — appears to be a display config for "Top 4" banners/announcements. Has date/image/ordering fields. The first row has `date = "ALL EVENTS"` and `location = "all upcoming events"`.

### `booth` — 21 rows

Booth/event operations checklist.

| Column | Description |
|---|---|
| `checklist` | Task name (e.g. "Lights") |
| `date` | Task description / instructions |
| `lights` | Boolean — lights checked? |
| `order` | Sort order |
| `notes` | Instructions |
| `active_note` | Whether the note is active |
| `archive_task` | Whether the task is archived |

### `dues` — 16 rows

Membership dues payments.

| Column | Description |
|---|---|
| `first_name` / `last_name` | Member name |
| `email` | Email address |
| `cell` | Phone number |
| `address` | Street address |
| `payment_type` | Payment method (e.g. "paypal") |
| `paid` | Boolean — payment completed |
| `date` | Payment date |
| `notes` | Additional info |

---

## Content

### `news` — 520 rows

News feed articles (the home page of the app).

| Column | Description |
|---|---|
| `title` | Article headline |
| `details` | Article body text |
| `date` | Publication date |
| `image` | Featured image URL |
| `location` | Location tag |
| `archive` | Whether archived |
| `link` / `link_2` / `videolink` | External links |
| `video` / `facebook_vid_link` | Video embeds |
| `players` | Players mentioned |
| `comic` | Comic strip image |
| Various | `deal`, `prompt`, `comments`, `sortby`, `email_link`, `cell`, `address` |

### `videos` — 6 rows

Featured video content.

| Column | Description |
|---|---|
| `name` | Video title |
| `desc` | Description |
| `link` | URL (external) |
| `image` | Thumbnail |
| `date_relation` | Date reference |
| `hidden` | Visibility toggle |
| `order` | Sort order |

### `featured` — 1 row

Featured player spotlight — a single player interview/profile.

| Column | Description |
|---|---|
| `name` | Player name |
| `nickname` | Nickname |
| `rank` | World rank |
| `location` | City, State |
| `hand` / `mallet` | Equipment |
| `shot` | Shot percentage |
| `weekly_level` / `chi` | Level info |
| `interview` through `interview_10` | Multi-part interview text |
| `profilepic` / `altpic` | Images |
| `column8` | Unknown percentage |

### `archive` — 9 rows

Archived player spotlight / interviews (same format as `featured`).

### `rules` — 29 rows

Rule documents and resources.

| Column | Description |
|---|---|
| `name` | Document name (e.g. "Rules", "USAA Rules") |
| `details` | Description |
| `link` / `link2` / `link3` | Document URLs (Google Drive PDFs) |
| `image` | Thumbnail |
| `visible` | Visibility |
| `order` | Sort order |
| `ae_tools` | Unknown flag |

### `shots` — 16 rows

Shot technique library with photos and descriptions.

| Column | Description |
|---|---|
| `name` | Shot name (e.g. "Cross", "Bank Shot") |
| `desc_1` through `desc_4` | Shot descriptions |
| `pic_1` through `pic_4` | Demonstration photos |
| `column4` / `column7` / `column10` / `desc_l4` | Left-hand variant descriptions |

### `breakdown` — 1 row

Single-page content — a primer on how shots are defined and categorised.

### `terminology` — 34 rows

Air hockey terminology glossary.

| Column | Description |
|---|---|
| `name` | Term (e.g. "Dactylonomy") |
| `definition` | Explanation |
| `link` | External reference link |

### `ref_clinic` — 4 rows

Referee training clinic content.

| Column | Description |
|---|---|
| `title` | Lesson title |
| `text` | Lesson body |
| `video` | Instructional video URL |
| `date` | Publication date |
| `sort` | Order |
| `pic` | Image |
| `fav` | Favourite/featured flag |

### `play_puck` — 9 rows

Puck-in-play phrase translations (very likely related to the air horn / referee commands).

| Column | Description |
|---|---|
| `start` | Start command ("In Play / Play Puck / Puck In") |
| `stop` | Stop command |
| `time_out` | Timeout command |
| `ready` | Ready command |
| `i` through `vii` | Numbers "One" through "Seven" |
| `col_0` | "Zero" |
| `language` | Language (e.g. "English") |
| `column2` | Duplicate start command |

---

## Locations & Equipment

### `aft` (Air Flow Testing) — 2 rows

Air hockey table airflow measurements — detailed per-table airflow readings (many hashed columns, each a measurement point on the table surface).

| Column | Description |
|---|---|
| `location_name` | Venue name (e.g. "Airhockey 7-6") |
| `address` / `city` / `state` / `zip` | Venue address |
| `table_number` | Table number at the venue |
| `name` | Person who submitted the readings |
| `email` | Submitter email |
| `air_flow_perception` | Subjective airflow rating (1-5) |
| `notes` | Notes about the table |
| `image_of_table` | Photo of the table |
| `date_and_time` | When readings were taken |
| Numerous hashed columns | Airflow readings at specific grid points on the table surface (all ~1.0-1.6 range, presumably PSI or similar) |
| Various `col_*hash*` = 0 | Outlet positions with no airflow |

### `variations` — 59 rows

Game format variations — different region/venue rule variants for how air hockey is played.

| Column | Description |
|---|---|
| `size` | Field size (e.g. "sm") |
| `abbreviation` | Region code (e.g. "AL" = Alabama) |
| `locations` | Venue name |
| `kvalue_choices` | Match format (e.g. "4 out of 7 sets") |
| `puck_color` | Puck colour used |
| `hand` | Handedness |
| `mallet` | Mallet type |
| `sanctables` | Sanctioned table type |
| `c66e0b40531df17e400bb052c09bea5c7` | Location name (e.g. "Alabama") |

### `pole_sheet` — 21 rows

Player poll responses — favourite tables, mallets, puck setups.

| Column | Description |
|---|---|
| `c76_poll` | Poll question 76 response (favourite table) |
| `fav_table` | Favourite table type |
| `fav_mallet` | Favourite mallet type |
| `fav_puck` | Favourite puck colour |
| `fav_puck_tape` | Favourite tape arrangement |
| `string` | Whether they use a string |

### `copy_of_tables` — 25 rows

Directory of air hockey table locations (venue listings).

| Column | Description |
|---|---|
| `name` | Venue name |
| `details` | Table specifications |
| `address` | Street address |
| `caption` | Notes |
| `phone` | Contact number |
| `website` | Venue website |

---

## Contact

### `contact` — 7 rows

Contact form submissions.

| Column | Description |
|---|---|
| `first_name` / `last_name` | Name |
| `email` | Email |
| `cell` | Phone |
| `message` | Message text |
| `c7ac5a1ab23d01d181148ba8cc6c45313` | Timestamp (hashed column name) |

---

## Internal / Empty

### `wahsa` — 0 rows

Empty table. Presumably was going to be used for WAHSA (World Air Hockey Shooters Association?) data but never populated.

---

## Column naming notes

Many columns have names like `c7f5258906b9be1c26357da2cc516fc4b` — these are **Glide auto-generated column IDs**. In the original app these had display labels, but those labels are only stored in Glide's schema metadata (which we don't have). The `c` prefix was added by the archive script. Where a meaningful original column name existed, it was preserved.
