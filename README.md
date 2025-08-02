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
- `crg` – Creative gigs (freelance video, content creation)
- `cpg` – Computer gigs (SMM specialists, social media admins)
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

**Enhanced script specifically designed for SMM/video/media job hunting.**

To search for SMM/media positions across relevant Craigslist sections:

```sh
python azalia_search.py
```

This will search in multiple relevant sections (`mar`, `med`, `art`, `crg`, `cpg`) with SMM/media keywords and include Chicago suburbs.

**Key features:**
- **Multi-section search**: Automatically searches in Marketing (mar), Media (med), Art/Design (art), Creative gigs (crg), and Computer gigs (cpg)
- **Suburb coverage**: Includes Chicago, Naperville, Arlington Heights, Oak Park, Evanston, Forest Park, and remote positions
- **SMM-focused keywords**: Optimized for social media, content creation, and video positions
- **Deduplication**: Removes duplicate postings found across multiple sections
- **Flexible output**: Supports both JSON and CSV formats

**Advanced usage examples:**

**Part-time SMM search (recommended for 18-year-old students):**
```sh
python azalia_search.py --keywords "part-time,social media,content creator,tiktok,instagram,video editor,freelance,intern" --days 30 --max_jobs 150
```

**Creative gigs only:**
```sh
python azalia_search.py --sections "crg,cpg" --keywords "video,content,social media,tiktok,instagram" --days 30
```

**Broad suburbs search:**
```sh
python azalia_search.py --locations "chicago,naperville,arlington heights,oak park,evanston,schaumburg,cicero,remote" --days 30
```

**CSV output for spreadsheet analysis:**
```sh
python azalia_search.py --csv --output smm_opportunities.csv --days 30
```

**Maximal-inclusion (wildcard) run—extract all relevant jobs:**
```sh
python azalia_search.py --keywords "" --max_jobs 500 --days 30
```
- Leaving `--keywords ""` empty disables keyword filtering (universal mode).
- Searches across all specified sections and locations.
- Use `--max_jobs` to control volume (default is 200 per section).

**Command-line options:**
- `--keywords, -k`: Keywords to search for (default: comprehensive SMM/media terms)
- `--sections, -s`: Craigslist sections to search (default: mar,med,art,crg,cpg)
- `--days, -d`: Days back to search (default: 30)
- `--locations, -l`: Locations to include (default: Chicago + suburbs + remote)
- `--max_jobs, -m`: Max jobs per section (default: 200)
- `--output, -o`: Output filename (default: azalia_smm_jobs.json)
- `--csv`: Output in CSV format instead of JSON

The script outputs comprehensive job listings suitable for part-time SMM/video/media work, with no special setup required.
