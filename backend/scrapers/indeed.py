"""Indeed job scraper via HTML parsing.

Searches Indeed's job listing pages and extracts results. Includes polite
delays and rotating user-agent strings.
"""
from __future__ import annotations

import asyncio
import random
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from backend.scrapers.base import BaseScraper, JobListing

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]


class IndeedScraper(BaseScraper):
    name = "indeed"
    BASE_URL = "https://www.indeed.com/jobs"

    async def scrape(self, queries: list[str], location: Optional[str] = None) -> list[JobListing]:
        jobs: list[JobListing] = []
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            for query in queries:
                params = {"q": query, "sort": "date"}
                if location and location.lower() != "remote":
                    params["l"] = location
                elif location and location.lower() == "remote":
                    params["remotejob"] = "032b3046-06a3-4876-8dfd-474eb5e7ed11"

                headers = {"User-Agent": random.choice(USER_AGENTS)}
                try:
                    resp = await client.get(self.BASE_URL, params=params, headers=headers)
                    resp.raise_for_status()
                except Exception:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.job_seen_beacon") or soup.select("div.jobsearch-ResultsList > div")

                for card in cards:
                    title_el = card.select_one("h2.jobTitle a, h2.jobTitle span")
                    company_el = card.select_one("[data-testid='company-name'], span.companyName")
                    location_el = card.select_one("[data-testid='text-location'], div.companyLocation")
                    link_el = card.select_one("h2.jobTitle a")

                    if not title_el:
                        continue

                    job_url = ""
                    if link_el and link_el.get("href"):
                        href = link_el["href"]
                        job_url = href if href.startswith("http") else f"https://www.indeed.com{href}"

                    jobs.append(
                        JobListing(
                            title=title_el.get_text(strip=True),
                            company=company_el.get_text(strip=True) if company_el else "",
                            location=location_el.get_text(strip=True) if location_el else "",
                            description="",
                            url=job_url,
                            source=self.name,
                        )
                    )

                await asyncio.sleep(random.uniform(2, 4))

        return jobs
