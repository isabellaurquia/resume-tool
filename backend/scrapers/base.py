from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Optional


@dataclass
class JobListing:
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    posted_at: str = ""
    salary: str = ""
    extras: dict = field(default_factory=dict)


class BaseScraper(ABC):
    name: str = "base"

    @abstractmethod
    async def scrape(self, queries: list[str], location: Optional[str] = None) -> list[JobListing]:
        ...
