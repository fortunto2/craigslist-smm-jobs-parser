# Scrapy settings for craigslist_jobs project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "craigslist_jobs"

SPIDER_MODULES = ["craigslist_jobs.spiders"]
NEWSPIDER_MODULE = "craigslist_jobs.spiders"

ADDONS = {}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# Important: Set a realistic User-Agent to avoid being blocked (from GoTrained tutorial)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
# Reduced to be more respectful to Craigslist servers (GoTrained recommendation)
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2  # Increased from 1 to 2 seconds (GoTrained recommendation)
RANDOMIZE_DOWNLOAD_DELAY = (
    0.5  # 50% of DOWNLOAD_DELAY to 150% (0.5 * DOWNLOAD_DELAY to 1.5 * DOWNLOAD_DELAY)
)

# Auto-throttle to be even more respectful
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False  # Set to True to see throttling stats

# Disable cookies (enabled by default) - often not needed for job scraping
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers to appear more like a real browser
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "craigslist_jobs.middlewares.CraigslistJobsSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "craigslist_jobs.middlewares.CraigslistJobsDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "craigslist_jobs.pipelines.CraigslistJobsPipeline": 300,
# }

# Set custom field order for CSV export (from GoTrained tutorial)
FEED_EXPORT_FIELDS = [
    "title",
    "job_url",
    "posted_date",
    "location",
    "short_description",
]

# Enable and configure HTTP caching (disabled by default)
# Useful for development to avoid re-downloading same pages
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1 hour cache
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [503, 504, 505, 500, 403, 404, 408, 429]

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# Logging settings
LOG_LEVEL = "INFO"  # Change to DEBUG for more verbose output
