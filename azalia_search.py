#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azalia SMM/Media Job Search Script
----------------------------------
- Search Chicago SMM/media jobs in relevant Craigslist sections
- Supports multiple sections: mar (Marketing), med (Media), art (Art/Design), crg (Creative gigs), cpg (Computer gigs)
- Includes Chicago suburbs and remote positions
- Filters for part-time, freelance, and creative positions
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
        default="social media,content creator,tiktok,instagram,video editor,videographer,reels,short-form video,UGC creator,digital marketing,smm,content,marketing,creative,design,photo",
        help="Comma-separated keywords for job search (default: SMM/media related terms)",
    )
    parser.add_argument(
        "--sections",
        "-s",
        type=str,
        default="mar,med,art,crg,cpg",
        help="Comma-separated Craigslist sections to search (default: mar,med,art,crg,cpg)",
    )
    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=30,
        help="Only include jobs posted within this many days (default: 30)",
    )
    parser.add_argument(
        "--locations",
        "-l",
        type=str,
        default="chicago,naperville,arlington heights,oak park,evanston,forest park,remote",
        help="Comma-separated locations to include (default: Chicago + major suburbs + remote)",
    )
    parser.add_argument(
        "--max_jobs",
        "-m",
        type=int,
        default=200,
        help="Maximum number of jobs to collect per section (default: 200)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="azalia_smm_jobs.json",
        help="Output JSON file name (default: azalia_smm_jobs.json)",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Output in CSV format instead of JSON",
    )
    return parser.parse_args()


def run_spider_for_section(section, keywords, days, locations, max_jobs):
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

    print(
        f"[SMM Search] Running spider for section '{section}': {' '.join(shlex.quote(x) for x in spider_cmd)}"
    )
    try:
        result = subprocess.run(
            spider_cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd="craigslist_jobs",
        )
    except subprocess.CalledProcessError as e:
        print(
            f"[SMM Search] Spider failed for section '{section}':\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        )
        return []

    try:
        with open(temp_results_path, "r", encoding="utf-8") as f:
            jobs = json.load(f)
            print(f"[SMM Search] Section '{section}': found {len(jobs)} jobs")
            return jobs
    except Exception as e:
        print(f"[SMM Search] Failed to load results for section '{section}': {e}")
        return []
    finally:
        # Clean up temp file
        if os.path.exists(temp_results_path):
            os.remove(temp_results_path)


def main():
    args = parse_args()

    sections = [s.strip() for s in args.sections.split(",") if s.strip()]
    all_jobs = []

    print(f"[SMM Search] Searching in sections: {', '.join(sections)}")
    print(f"[SMM Search] Keywords: {args.keywords}")
    print(f"[SMM Search] Locations: {args.locations}")
    print(f"[SMM Search] Days: {args.days}")
    print(f"[SMM Search] Max jobs per section: {args.max_jobs}")

    for section in sections:
        jobs = run_spider_for_section(
            section, args.keywords, args.days, args.locations, args.max_jobs
        )
        all_jobs.extend(jobs)

    # Remove duplicates based on job_url
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        if job.get("job_url") not in seen_urls:
            seen_urls.add(job.get("job_url"))
            unique_jobs.append(job)

    print(f"[SMM Search] Total unique jobs found: {len(unique_jobs)}")

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
        print(f"[SMM Search] Results saved to {output_file} (CSV format)")
    else:
        # Write JSON
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(unique_jobs, outfile, ensure_ascii=False, indent=2)
        print(f"[SMM Search] Results saved to {output_file} (JSON format)")


if __name__ == "__main__":
    main()
