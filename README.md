# Craigslist Jobs Parser

This project uses Python, managed with [uv](https://github.com/astral-sh/uv), and uses Scrapy to parse job listings from Craigslist.

To install dependencies with uv:
```sh
uv sync
```

## Usage

All commands should be run from the project root.

### Universal search

The universal spider [`chicago_jobs`](craigslist_jobs/craigslist_jobs/spiders/chicago_jobs.py:1) can be run with optional CLI arguments to customize your search:

**Supported CLI arguments:**

- `keywords`: Comma-separated keywords to match in job titles/descriptions. *(Default: `smm,video,tiktok` if omitted)*
  &nbsp;&nbsp;&nbsp;&nbsp;To scrape **all jobs** (disable keyword filtering), set `keywords=""` (empty string) to enable wildcard/universal mode.
- `max_jobs`: (optional) Limit number of jobs to scrape per run (default: `100`). Use `-a max_jobs=300` to expand or restrict as needed.
- `days`: Only include jobs posted within the last N days. *(Default: `7`)*
- `section`: Craigslist section to scrape. *(Default: `'jjj'`/Jobs)*
- `locations`: Comma-separated locations (loose match, e.g., `"chicago,remote,oak park"`). If omitted, all locations are included.

**Craigslist Section Codes:**

**Jobs (paid positions):**
- `jjj` – All Jobs (general search)
- `mar` – Marketing / Advertising / PR (best for SMM, content, video positions)
- `med` – Media / TV / Radio
- `art` – Art / Design / Creative

**Gigs (freelance/part-time):**
- `ggg` – All Gigs (general search)
- `crg` – Creative gigs (freelance video, content creation) **← BEST for part-time SMM**
- `cpg` – Computer gigs (SMM specialists, social media admins) **← BEST for tech-savvy creators**
- `dmg` – Domestic gigs (rarely relevant)

**Basic usage:**
```sh
uv run scrapy crawl chicago_jobs -O results.json
```
This scrapes the default ("jjj" jobs, last 7 days, keywords: smm/video/tiktok, all locations).

**SMM/Media-focused search:**
```sh
uv run scrapy crawl chicago_jobs -O smm_jobs.json -a section=mar -a keywords="social media,content creator,tiktok,instagram,video editor"
```

**Wildcard (universal/all-jobs) run—no keyword or location filter:**
```sh
uv run scrapy crawl chicago_jobs -O all_jobs.json -a keywords="" -a max_jobs=200
```
This disables keyword filtering and collects all available jobs (up to `max_jobs`), suitable for broad inclusion or debug purposes.

**Custom usage examples:**
- Filter for multiple keywords, in different sections:
  ```sh
  uv run scrapy crawl chicago_jobs -O results.csv -a keywords=designer,web,ui,ux -a section=art
  ```
- Restrict to specific locations, last 3 days:
  ```sh
  uv run scrapy crawl chicago_jobs -O results.json -a days=3 -a locations=chicago,remote
  ```
- Creative gigs search:
  ```sh
  uv run scrapy crawl chicago_jobs -O creative_gigs.json -a section=crg -a keywords="video,photo,content,social media"
  ```

**Notes:**
- Arguments are passed with `-a argument=value`. Comma separation is used for multi-value options.
- Leaving `keywords` empty (`-a keywords=""`) scrapes all jobs—no filtering on title/description.
- The `max_jobs` argument is optional; defaults to 100 if omitted.
- If any argument is omitted, its default is used.
- Supported output formats: `.json` or `.csv` (file extension determines format; both contain all scraped fields).
- Output is saved to the specified file (e.g., `results.json` or `results.csv`) in the project root.
- Output result breadth depends on keyword/locations arguments:
  &nbsp;&nbsp;&nbsp;&nbsp;• *Strict/filtered*: with keywords or locations
  &nbsp;&nbsp;&nbsp;&nbsp;• *Wildcard/broad*: with empty `keywords` and/or `locations` (all jobs, maximal content)

**Output:**
- Each record contains: `title`, `job_url`, `posted_date`, `location`, `short_description`.
- The output file is structured as either standard JSON or CSV rows with these fields. Use CSV for spreadsheet import, JSON for further programmatic processing.

---

### Azalia SMM/Media Search

**🎯 Optimized script for daily SMM/media job monitoring in Chicago.**

#### Quick Daily Check (Recommended):
```sh
uv run python azalia_search.py
```
**Default settings (perfect for 18-year-old student):**
- **Focus:** Chicago city only (no suburbs/remote distractions)
- **Sections:** Creative gigs (crg), Computer gigs (cpg), Marketing (mar)
- **Period:** Last 7 days
- **Keywords:** SMM + part-time focused terms
- **Speed:** 50 jobs max per section for quick scanning

#### Super Quick Monitor Mode:
```sh
uv run python azalia_search.py --monitor
```
**Monitor mode features:**
- ⚡ **Ultra-fast:** Only today's jobs, 30 max per section
- 🎯 **Focused:** Only crg + cpg sections (most active for part-time)
- 🤫 **Quiet:** Minimal output, just results count
- 📁 **Auto-named:** Saves to `monitor_jobs.json`

Perfect for **daily morning routine** or **automated checks**.

#### Advanced Usage:

**Weekly comprehensive scan:**
```sh
uv run python azalia_search.py --days 7 --max_jobs 100 --sections "crg,cpg,mar,med"
```

**Part-time focused search:**
```sh
uv run python azalia_search.py --keywords "part-time,intern,freelance,student,social media,content creator,tiktok,instagram" --days 3
```

**Include suburbs when needed:**
```sh
uv run python azalia_search.py --locations "chicago,naperville,evanston,remote" --days 14
```

**CSV output for analysis:**
```sh
uv run python azalia_search.py --csv --output weekly_opportunities.csv --days 7
```

**Silent background monitoring:**
```sh
uv run python azalia_search.py --quiet --days 1 --output today_jobs.json
```

#### Command-line Options:
- `--keywords, -k`: Search terms (default: comprehensive SMM + part-time terms)
- `--sections, -s`: Craigslist sections (default: crg,cpg,mar)
- `--days, -d`: Days back to search (default: 7)
- `--locations, -l`: Locations to include (default: chicago only)
- `--max_jobs, -m`: Max jobs per section (default: 50)
- `--output, -o`: Output filename (default: daily_smm_jobs.json)
- `--csv`: Output in CSV format
- `--quiet, -q`: Minimal output
- `--monitor`: Ultra-fast mode for daily checks

#### Key Features:
- 🚀 **Fast by default**: Optimized for quick daily monitoring
- 🎯 **Part-time focused**: Targets student-friendly opportunities
- 📍 **Chicago-centric**: No suburban noise unless requested
- 📊 **Smart preview**: Shows latest 3 jobs in terminal
- 🔄 **Auto-sorted**: Newest jobs first
- ✨ **Clean output**: Beautiful formatting and emojis

#### Perfect for:
- **Daily job hunting routine** for 18-year-old students
- **Quick morning checks** before classes
- **Automated monitoring** scripts
- **Part-time opportunity tracking**

The script outputs comprehensive job listings suitable for part-time SMM/video/media work, with no special setup required.
