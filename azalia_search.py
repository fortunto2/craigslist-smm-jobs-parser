#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azalia SMM/Media Job Search Script
----------------------------------
- Search Chicago SMM/media jobs in relevant Craigslist sections
- Supports multiple sections: mar (Marketing), med (Media), art (Art/Design), crg (Creative gigs), cpg (Computer gigs)
- Focused on Chicago city only by default (no suburbs or remote)
- Optimized for quick monitoring and daily job checks
"""

import sys
import os
import argparse
import json
import tempfile
import subprocess
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description="Azalia SMM/Media: Chicago Craigslist Jobs search for SMM/video/media positions"
    )
    parser.add_argument(
        "--keywords",
        "-k",
        type=str,
        default="social media,content creator,tiktok,instagram,video editor,videographer,reels,short-form video,UGC creator,digital marketing,smm,content,marketing,creative,design,photo,part-time,intern,freelance",
        help="Comma-separated keywords for job search (default: comprehensive SMM/media + part-time terms)",
    )
    parser.add_argument(
        "--sections",
        "-s",
        type=str,
        default="crg,cpg,mar",
        help="Comma-separated Craigslist sections to search (default: crg,cpg,mar - most relevant for part-time)",
    )
    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=7,
        help="Only include jobs posted within this many days (default: 7 for daily monitoring)",
    )
    parser.add_argument(
        "--locations",
        "-l",
        type=str,
        default="chicago",
        help="Comma-separated locations to include (default: chicago only - no suburbs or remote)",
    )
    parser.add_argument(
        "--max_jobs",
        "-m",
        type=int,
        default=50,
        help="Maximum number of jobs to collect per section (default: 50 for quick monitoring)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="daily_smm_jobs.json",
        help="Output JSON file name (default: daily_smm_jobs.json)",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Output in CSV format instead of JSON",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Minimal output - only show final results count",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Monitor mode: optimized settings for daily job checking (7 days, chicago only, top sections)",
    )
    return parser.parse_args()


def run_spider_for_section(section, keywords, days, locations, max_jobs, quiet=False):
    """Run spider for a specific section and return results"""
    import shlex
    import uuid

    temp_results_path = os.path.join(
        tempfile.gettempdir(), f"smm_search_{section}_{uuid.uuid4().hex}.json"
    )

    spider_cmd = [
        "uv"
        if os.path.exists("uv.lock") or os.path.exists("pyproject.toml")
        else sys.executable,
    ]
    if spider_cmd[0] == "uv":
        spider_cmd += [
            "run",
            "scrapy",
            "crawl",
            "chicago_jobs",
            "-O",
            temp_results_path,
            "-a",
            f"section={section}",
            "-a",
            f"days={days}",
            "-a",
            f"keywords={keywords}",
            "-a",
            f"locations={locations}",
            "-a",
            f"max_jobs={max_jobs}",
        ]
    else:
        spider_cmd += [
            "-m",
            "scrapy",
            "crawl",
            "chicago_jobs",
            "-O",
            temp_results_path,
            "-a",
            f"section={section}",
            "-a",
            f"days={days}",
            "-a",
            f"keywords={keywords}",
            "-a",
            f"locations={locations}",
            "-a",
            f"max_jobs={max_jobs}",
        ]

    if not quiet:
        print(f"[SMM Search] Scanning section '{section}'...")

    try:
        result = subprocess.run(
            spider_cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd="craigslist_jobs",
        )
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"[SMM Search] Section '{section}' failed: {e.stderr[:100]}...")
        return []

    try:
        with open(temp_results_path, "r", encoding="utf-8") as f:
            jobs = json.load(f)
            if not quiet:
                print(f"[SMM Search] Section '{section}': {len(jobs)} jobs")
            return jobs
    except Exception as e:
        if not quiet:
            print(f"[SMM Search] Failed to load results for section '{section}': {e}")
        return []
    finally:
        # Clean up temp file
        if os.path.exists(temp_results_path):
            os.remove(temp_results_path)


def main():
    args = parse_args()

    # Monitor mode overrides some settings for optimal daily checking
    if args.monitor:
        args.days = 1  # Only today's jobs
        args.max_jobs = 30  # Faster scan
        args.sections = "crg,cpg"  # Most active sections for part-time
        args.locations = "chicago"
        args.quiet = True
        if args.output == "daily_smm_jobs.json":
            args.output = "monitor_jobs.json"

    sections = [s.strip() for s in args.sections.split(",") if s.strip()]
    all_jobs = []

    if not args.quiet:
        print(f"🔍 [SMM Search] Monitoring Chicago SMM/media jobs")
        print(f"📅 Period: last {args.days} days")
        print(f"📍 Location: {args.locations}")
        print(f"🎯 Sections: {', '.join(sections)}")
        print(f"🔢 Max per section: {args.max_jobs}")
        print("-" * 50)

    for section in sections:
        jobs = run_spider_for_section(
            section, args.keywords, args.days, args.locations, args.max_jobs, args.quiet
        )
        all_jobs.extend(jobs)

    # Remove duplicates based on job_url
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        if job.get("job_url") not in seen_urls:
            seen_urls.add(job.get("job_url"))
            unique_jobs.append(job)

    # Sort by posted date (newest first)
    try:
        unique_jobs.sort(key=lambda x: x.get("posted_date", ""), reverse=True)
    except:
        pass  # If sorting fails, keep original order

    # Determine output format
    output_file = args.output
    if args.csv:
        if not output_file.endswith(".csv"):
            output_file = output_file.replace(".json", ".csv")

        # Write CSV
        import csv

        if unique_jobs:
            with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
                fieldnames = unique_jobs[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(unique_jobs)
    else:
        # Write JSON
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(unique_jobs, outfile, ensure_ascii=False, indent=2)

    # Summary output
    if args.quiet:
        print(f"{len(unique_jobs)} new jobs found")
    else:
        print("-" * 50)
        print(f"✅ [SMM Search] Complete!")
        print(f"📊 Total unique jobs found: {len(unique_jobs)}")
        print(f"💾 Results saved to: {output_file}")

        if unique_jobs:
            print(f"\n📋 Latest jobs preview:")
            for i, job in enumerate(unique_jobs[:3], 1):
                title = job.get("title", "N/A")[:50]
                location = job.get("location", "N/A").strip()
                print(f"  {i}. {title}... ({location})")

            if len(unique_jobs) > 3:
                print(f"  ... and {len(unique_jobs) - 3} more jobs")

        print(f"\n💡 To see all results: open {output_file}")
        print(f"🔄 For daily monitoring: python azalia_search.py --monitor")


if __name__ == "__main__":
    main()
