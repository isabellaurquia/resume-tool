"""Hacker News 'Who is Hiring?' thread scraper.

Fetches the latest monthly hiring thread from HN and parses top-level
comments for job postings matching the search queries.
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from backend.scrapers.base import BaseScraper, JobListing

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


class HNScraper(BaseScraper):
    name = "hn"

    async def scrape(self, queries: list[str], location: Optional[str] = None) -> list[JobListing]:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            thread_id = await self._find_latest_thread(client)
            if not thread_id:
                return []
            return await self._parse_thread(client, thread_id, queries)

    async def _find_latest_thread(self, client: httpx.AsyncClient) -> Optional[int]:
        params = {
            "query": "Ask HN: Who is hiring?",
            "tags": "story,author_whoishiring",
            "hitsPerPage": 1,
        }
        try:
            resp = await client.get(HN_SEARCH_URL, params=params)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
            return int(hits[0]["objectID"]) if hits else None
        except Exception:
            return None

    async def _parse_thread(
        self, client: httpx.AsyncClient, thread_id: int, queries: list[str]
    ) -> list[JobListing]:
        try:
            resp = await client.get(HN_ITEM_URL.format(thread_id))
            resp.raise_for_status()
            thread = resp.json()
        except Exception:
            return []

        child_ids = thread.get("kids", [])[:100]
        jobs: list[JobListing] = []
        query_terms = {q.lower() for query in queries for q in query.split()}

        for cid in child_ids:
            try:
                resp = await client.get(HN_ITEM_URL.format(cid))
                comment = resp.json()
            except Exception:
                continue

            text = comment.get("text", "")
            if not text:
                continue

            plain = BeautifulSoup(text, "html.parser").get_text(" ")
            if not any(term in plain.lower() for term in query_terms):
                continue

            first_line = plain.split("\n")[0].strip()
            company_match = re.match(r"^([^|]+)", first_line)
            company = company_match.group(1).strip() if company_match else "Unknown"

            loc = ""
            loc_match = re.search(r"\b(remote|onsite|hybrid)\b", first_line, re.IGNORECASE)
            if loc_match:
                loc = loc_match.group(0).capitalize()

            jobs.append(
                JobListing(
                    title=first_line[:120],
                    company=company,
                    location=loc,
                    description=plain,
                    url=f"https://news.ycombinator.com/item?id={cid}",
                    source=self.name,
                )
            )
            await asyncio.sleep(0.1)

        return jobs
