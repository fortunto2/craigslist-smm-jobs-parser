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
    def __init__(
        self,
        keywords=None,
        days=None,
        section=None,
        locations=None,
        max_jobs=None,
        *args,
        **kwargs,
    ):
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
            self.max_jobs = int(max_jobs) if max_jobs not in (None, "") else 100
        except Exception:
            self.max_jobs = 100

        self.start_urls = [f"https://chicago.craigslist.org/search/{self.section}"]

        self.logger.info(
            f"Spider started with: keywords={self.keywords}, days={self.days}, section={self.section}, locations={self.locations}, max_jobs={self.max_jobs}"
        )

    def parse(self, response):
        """
        Parse the main job search page, extract job listings,
        send requests to their detail pages to fetch full descriptions,
        and handle pagination.

        Improved based on GoTrained tutorial recommendations.
        """
        # Check if we got blocked or encountered an error
        if "blocked" in response.text.lower() or response.status != 200:
            self.logger.error(f"Possibly blocked or error response: {response.status}")
            return

        # Multiple selector strategies for robustness (GoTrained approach)
        job_rows = self._extract_job_rows(response)

        if not job_rows:
            self.logger.warning("No job rows found. Page structure may have changed.")
            # Debug: save the page for inspection
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            return

        self.logger.info(f"Found {len(job_rows)} jobs on current page.")

        # Slice job rows by self.max_jobs if set and >0, otherwise include all
        if self.max_jobs is not None and int(self.max_jobs) > 0:
            row_iter = job_rows[: int(self.max_jobs)]
        else:
            row_iter = job_rows

        for job in row_iter:
            job_data = self._extract_job_basic_info(job)
            if job_data and job_data["url"]:
                yield scrapy.Request(
                    job_data["url"],
                    callback=self.parse_job_detail,
                    meta=job_data,
                    errback=self.handle_error,
                )

        # Pagination: Follow next page if present (multiple selector strategies)
        next_page = self._find_next_page(response)
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(
                next_page, callback=self.parse, errback=self.handle_error
            )

    def _extract_job_rows(self, response):
        """Extract job rows using multiple selector strategies for robustness"""
        # Strategy 1: Modern Craigslist structure
        job_rows = response.css("li.cl-static-search-result")
        if job_rows:
            self.logger.debug("Using cl-static-search-result selector")
            return job_rows

        # Strategy 2: Alternative structure (from GoTrained tutorial)
        job_rows = response.css("li.result-row")
        if job_rows:
            self.logger.debug("Using result-row selector")
            return job_rows

        # Strategy 3: Generic list items with data-pid (backup)
        job_rows = response.css("li[data-pid]")
        if job_rows:
            self.logger.debug("Using data-pid selector")
            return job_rows

        # Strategy 4: XPath fallback
        job_rows = response.xpath("//li[contains(@class, 'result')]")
        if job_rows:
            self.logger.debug("Using XPath result selector")
            return job_rows

        return []

    def _extract_job_basic_info(self, job):
        """Extract basic job information using multiple selector strategies"""
        # Strategy 1: Modern structure
        title = (
            job.css("div.title a::text").get() or job.css("a.cl-app-anchor::text").get()
        )
        url = (
            job.css("div.title a::attr(href)").get()
            or job.css("a.cl-app-anchor::attr(href)").get()
        )
        location_raw = (
            job.css("div.details > div.location::text").get()
            or job.css("div.result-meta .result-hood::text").get()
        )

        # Strategy 2: Alternative structure (GoTrained tutorial style)
        if not title:
            title = job.css("a.result-title::text").get()
        if not url:
            url = job.css("a.result-title::attr(href)").get()
        if not location_raw:
            location_raw = job.css(".result-hood::text").get()

        # Clean up location
        location_clean = (location_raw or "").strip(" ()") if location_raw else ""
        if not location_clean or not location_clean.strip():
            location = "N/A"
        elif "remote" in location_clean.lower():
            location = "remote"
        else:
            location = location_clean

        # Make URL absolute if relative
        if url and url.startswith("/"):
            url = "https://chicago.craigslist.org" + url

        return {
            "title": title or "",
            "url": url,
            "location": location,
            "posted_date": None,
        }

    def _find_next_page(self, response):
        """Find next page using multiple selector strategies"""
        # Strategy 1: Modern next button
        next_page = response.css("a.button.next::attr(href)").get()
        if next_page:
            return next_page

        # Strategy 2: Alternative next link
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            return next_page

        # Strategy 3: XPath approach
        next_page = response.xpath(
            "//a[contains(text(), 'next') or contains(@class, 'next')]/@href"
        ).get()
        if next_page:
            return next_page

        return None

    def handle_error(self, failure):
        """Handle request errors gracefully"""
        self.logger.error(f"Request failed: {failure.request.url} - {failure.value}")

    def parse_job_detail(self, response):
        """
        Parse the detail page for each job listing to get the full description,
        filter by keywords and post date,
        and yield result dicts for matching jobs only.

        Enhanced based on GoTrained tutorial recommendations.
        """
        # Check if we got blocked or error
        if "blocked" in response.text.lower() or response.status != 200:
            self.logger.warning(f"Blocked or error on detail page: {response.url}")
            return

        title = (
            response.meta["title"]
            or response.css("span#titletextonly::text").get()
            or response.css("h1.postingtitle::text").get()
            or ""
        )

        job_url = response.meta["url"] or response.url
        location = response.meta["location"]

        # Multiple strategies for date extraction
        posted_date_raw = self._extract_posted_date(response)

        # Multiple strategies for description extraction (GoTrained approach)
        description = self._extract_description(response)

        # Create short description
        short_description = (
            description[:200].rsplit(" ", 1)[0]
            if len(description) > 200
            else description
        )

        # Override location if "remote" appears in description
        if location not in ("remote", "N/A"):
            if "remote" in description.lower():
                location = "remote"

        # Keyword filtering: If self.keywords nonempty, filter; else, do not filter by keyword
        text_to_search = f"{title} {description}".lower()
        if self.keywords:  # Only filter if there are actual keywords
            if not any(kw in text_to_search for kw in self.keywords):
                self.logger.debug(f"Job filtered out by keywords: {title}")
                return

        # Date filtering: Craigslist date is ISO 8601; only yield if within N days
        job_is_recent = self._is_job_recent(posted_date_raw)
        if not job_is_recent:
            self.logger.debug(f"Job filtered out by date: {title}")
            return

        # Location filtering: yield only if allowed or no locations filtering set
        if self.locations:
            location_lc = (location or "").lower()
            if not any(allowed in location_lc for allowed in self.locations):
                self.logger.debug(f"Job filtered out by location: {title} ({location})")
                return

        self.logger.info(f"Scraped job: {title}")
        yield {
            "title": title,
            "job_url": job_url,
            "posted_date": posted_date_raw,
            "location": location,
            "short_description": short_description,
        }

    def _extract_posted_date(self, response):
        """Extract posted date using multiple strategies"""
        # Strategy 1: Standard time element
        posted_date = response.css("time::attr(datetime)").get()
        if posted_date:
            return posted_date

        # Strategy 2: Date in posting details
        posted_date = response.css(".postinginfos time::attr(datetime)").get()
        if posted_date:
            return posted_date

        # Strategy 3: Text extraction from posting info
        date_text = response.css(".postinginfos .date::text").get()
        if date_text:
            return date_text

        return None

    def _extract_description(self, response):
        """Extract job description using multiple strategies"""
        # Strategy 1: Modern structure
        description = response.css("#postingbody").xpath("normalize-space()").get()
        if description:
            return re.sub(r"^QR Code Link to This Post\s*", "", description).strip()

        # Strategy 2: Alternative structure
        description = response.css(".userbody ::text").getall()
        if description:
            description = " ".join(description).strip()
            return re.sub(r"^QR Code Link to This Post\s*", "", description).strip()

        # Strategy 3: Generic body content
        description = response.css("body ::text").getall()
        if description:
            # Filter out navigation and other non-content text
            filtered_text = []
            for text in description:
                text = text.strip()
                if (
                    text
                    and len(text) > 10
                    and not any(
                        x in text.lower()
                        for x in ["craigslist", "navigation", "menu", "search"]
                    )
                ):
                    filtered_text.append(text)

            if filtered_text:
                return " ".join(
                    filtered_text[:10]
                )  # Limit to first 10 meaningful text blocks

        return ""

    def _is_job_recent(self, posted_date_raw):
        """Check if job is within the specified number of days"""
        if not posted_date_raw:
            return True  # If no date, assume it's recent

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
                return job_post_dt >= cutoff
        except Exception as e:
            self.logger.warning(f"Date parsing error: {e}")
            return True  # If can't parse date, assume it's recent

        return True
