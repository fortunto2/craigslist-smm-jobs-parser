# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CraigslistJobsItem(scrapy.Item):
    """
    Structured item for Craigslist job data.
    Following GoTrained tutorial recommendations for data organization.
    """

    # Job basic information
    title = scrapy.Field()
    job_url = scrapy.Field()
    posted_date = scrapy.Field()
    location = scrapy.Field()

    # Job content
    short_description = scrapy.Field()
    full_description = scrapy.Field()

    # Additional metadata
    section = scrapy.Field()  # Which Craigslist section (mar, crg, etc.)
    scraped_at = scrapy.Field()  # When the item was scraped

    # Contact information (if available)
    contact_info = scrapy.Field()

    # Job requirements/attributes
    job_type = scrapy.Field()  # full-time, part-time, contract, etc.
    salary_info = scrapy.Field()

    def __str__(self):
        """String representation for debugging"""
        return f"CraigslistJob(title='{self.get('title', 'N/A')}', location='{self.get('location', 'N/A')}')"

    def __repr__(self):
        """Detailed representation for debugging"""
        return f"CraigslistJobsItem({dict(self)})"


class JobFilterItem(scrapy.Item):
    """
    Item for tracking filtering statistics.
    Helps understand what jobs are being filtered out and why.
    """

    total_jobs_found = scrapy.Field()
    jobs_after_keyword_filter = scrapy.Field()
    jobs_after_date_filter = scrapy.Field()
    jobs_after_location_filter = scrapy.Field()
    final_jobs_count = scrapy.Field()

    # Filter criteria used
    keywords_used = scrapy.Field()
    days_filter = scrapy.Field()
    locations_filter = scrapy.Field()
    section_searched = scrapy.Field()

    # Processing metadata
    search_date = scrapy.Field()
    processing_time = scrapy.Field()
