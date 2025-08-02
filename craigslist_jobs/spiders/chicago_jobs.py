import scrapy
import re
from datetime import datetime, timedelta

# To export scraped jobs, use Scrapy's built-in feed export:
#   uv run scrapy crawl chicago_jobs -O results.json
# or:
#   uv run scrapy crawl chicago_jobs -O results.csv
# (Supported formats: JSON, CSV. See Scrapy docs for more.)


class ChicagoJobsSpider(scrapy.Spider):
    name = "chicago_jobs"
    allowed_domains = ["chicago.craigslist.org"]

    # Scrapy will call __init__ with spider_args set by -a.
    def __init__(self, keywords=None, days=None, section=None, locations=None, max_jobs=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Universal parameters via CLI
        if keywords is not None:
            self.keywords = [
                k.strip().lower() for k in keywords.split(",") if k.strip()
            ]
        else:
            self.keywords = ["smm", "video", "tiktok"]

        if days is not None:
            try:
                self.days = int(days)
            except Exception:
                self.days = 7
        else:
            self.days = 7

        self.section = section if section else "jjj"

        # Parse locations argument (new)
        if locations is not None:
            self.locations = [
                loc.strip().lower() for loc in locations.split(",") if loc.strip()
            ]
            if not self.locations:
                self.locations = None
        else:
            self.locations = None

        # Parse max_jobs argument (new)
        try:
            self.max_jobs = int(max_jobs) if max_jobs not in (None, "") else 10
        except Exception:
            self.max_jobs = 10

        self.start_urls = [f"https://chicago.craigslist.org/search/{self.section}"]

        self.logger.info(
            f"Spider started with: keywords={self.keywords}, days={self.days}, section={self.section}, locations={self.locations}, max_jobs={self.max_jobs}"
        )

    def parse(self, response):
        """
        Parse the main job search page, extract job listings,
        send requests to their detail pages to fetch full descriptions,
        and handle pagination.
        """
        # Select all job listings in the search results
        # DEBUG: Write raw response HTML to file on first page only for inspection
        with open("jobs_search.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        # SELECTORS FOR NEW CRAIGSLIST STATIC LISTINGS
        job_rows = response.css("li.cl-static-search-result")
        self.logger.info(f"Found {len(job_rows)} jobs on jobs page (STATIC SELECTOR).")
        # Slice job rows by self.max_jobs if set and >0, otherwise include all
        if self.max_jobs is not None and int(self.max_jobs) > 0:
            row_iter = job_rows[: int(self.max_jobs)]
        else:
            row_iter = job_rows
        for job in row_iter:
            title = job.css("div.title::text").get("") or job.attrib.get("title", "")
            url = job.css("a::attr(href)").get("")
            location_raw = job.css("div.details > div.location::text").get("")
            location_clean = (location_raw or "").strip(" ()") if location_raw else ""

            # Enhanced location extraction: default to "N/A" if missing, detect remote
            if not location_clean or not location_clean.strip():
                location = "N/A"
            elif "remote" in location_clean.lower():
                location = "remote"
            else:
                location = location_clean

            if url:
                yield scrapy.Request(
                    url,
                    callback=self.parse_job_detail,
                    meta={
                        "title": title,
                        "job_url": url,
                        "posted_date": None,
                        "location": location,
                    },
                )

        # Pagination: Follow next page if present
        next_page = response.css("a.button.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_job_detail(self, response):
        """
        Parse the detail page for each job listing to get the full description,
        filter by keywords and post date,
        and yield result dicts for matching jobs only.
        """
        title = (
            response.meta["title"]
            or response.css("span#titletextonly::text").get()
            or ""
        )
        job_url = response.meta["job_url"]
        posted_date_raw = (
            response.meta["posted_date"] or response.css("time::attr(datetime)").get()
        )
        location = response.meta["location"]
        # If remote in description but not detected in location, correct for "remote"
        description = (
            response.css("#postingbody").xpath("normalize-space()").get() or ""
        )
        description = re.sub(r"^QR Code Link to This Post\s*", "", description).strip()
        short_description = (
            description[:200].rsplit(" ", 1)[0]
            if len(description) > 200
            else description
        )

        # Optionally override location if "remote" appears in description
        if location not in ("remote", "N/A"):
            if "remote" in description.lower():
                location = "remote"

        text_to_search = f"{title} {description}".lower()
        # If self.keywords nonempty, filter; else, do not filter by keyword
        if self.keywords:  # Only filter if there are actual keywords
            if not any(kw in text_to_search for kw in self.keywords):
                return

        # Date filtering: Craigslist date is ISO 8601; only yield if within N days
        job_is_recent = False
        posted_date = posted_date_raw
        try:
            if posted_date_raw:
                job_post_dt = datetime.strptime(
                    posted_date_raw[:19], "%Y-%m-%dT%H:%M:%S"
                )
                now_dt = (
                    datetime.now(job_post_dt.tzinfo)
                    if job_post_dt.tzinfo
                    else datetime.now()
                )
                cutoff = now_dt - timedelta(days=self.days)
                if job_post_dt >= cutoff:
                    job_is_recent = True
        except Exception:
            job_is_recent = True

        if not job_is_recent:
            return

        # Location filtering: yield only if allowed or no locations filtering set
        if self.locations:
            # If location is N/A, only match if "n/a" is in filter list (for explicit allowance)
            location_lc = (location or "").lower()
            if not any(allowed in location_lc for allowed in self.locations):
                return

        yield {
            "title": title,
            "job_url": job_url,
            "posted_date": posted_date,
            "location": location,
            "short_description": short_description,
        }
