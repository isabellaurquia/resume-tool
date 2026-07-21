"""LinkedIn job scraper using SerpAPI's Google Jobs endpoint.

This avoids touching LinkedIn directly — we search Google Jobs which indexes
LinkedIn postings. Requires a SERPAPI_API_KEY in .env.
"""
from __future__ import annotations

import asyncio
from typing import Optional
import httpx
from backend.scrapers.base import BaseScraper, JobListing
from backend.config import settings


class LinkedInScraper(BaseScraper):
    name = "linkedin"
    SERPAPI_URL = "https://serpapi.com/search.json"

    async def scrape(self, queries: list[str], location: Optional[str] = None) -> list[JobListing]:
        if not settings.serpapi_api_key:
            return []

        jobs: list[JobListing] = []
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            for query in queries:
                params = {
                    "engine": "google_jobs",
                    "q": query,
                    "api_key": settings.serpapi_api_key,
                }
                if location:
                    params["location"] = location

                try:
                    resp = await client.get(self.SERPAPI_URL, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                except Exception:
                    continue

                for result in data.get("jobs_results", []):
                    apply_links = result.get("apply_options", [])
                    url = apply_links[0]["link"] if apply_links else ""
                    if not url:
                        related = result.get("related_links", [])
                        url = related[0]["link"] if related else ""

                    jobs.append(
                        JobListing(
                            title=result.get("title", ""),
                            company=result.get("company_name", ""),
                            location=result.get("location", ""),
                            description=result.get("description", ""),
                            url=url,
                            source=self.name,
                            posted_at=result.get("detected_extensions", {}).get("posted_at", ""),
                        )
                    )

                await asyncio.sleep(1)  # polite delay between queries

        return jobs
