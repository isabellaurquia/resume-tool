from __future__ import annotations

import asyncio
from typing import Optional
import httpx
from backend.scrapers.base import BaseScraper, JobListing


class RemoteOKScraper(BaseScraper):
    name = "remoteok"
    API_URL = "https://remoteok.com/api"

    async def scrape(self, queries: list[str], location: Optional[str] = None) -> list[JobListing]:
        jobs: list[JobListing] = []
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(
                self.API_URL,
                headers={"User-Agent": "JobPilot/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()

        # First item is a metadata/legal notice object
        listings = data[1:] if len(data) > 1 else data

        query_terms = {q.lower() for query in queries for q in query.split()}
        for item in listings:
            text = f"{item.get('position', '')} {item.get('description', '')} {' '.join(item.get('tags', []))}".lower()
            if not any(term in text for term in query_terms):
                continue

            jobs.append(
                JobListing(
                    title=item.get("position", ""),
                    company=item.get("company", ""),
                    location="Remote",
                    description=item.get("description", ""),
                    url=f"https://remoteok.com/remote-jobs/{item.get('slug', item.get('id', ''))}",
                    source=self.name,
                    posted_at=item.get("date", ""),
                    salary=item.get("salary_min", ""),
                )
            )
            await asyncio.sleep(0)  # yield to event loop

        return jobs
