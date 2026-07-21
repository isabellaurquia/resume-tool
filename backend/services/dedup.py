import re
import unicodedata

from sqlalchemy.orm import Session

from backend.models import Job
from backend.scrapers.base import JobListing


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    return text


def make_dedup_key(listing: JobListing) -> str:
    return f"{normalize(listing.company)}::{normalize(listing.title)}"


def deduplicate(listings: list[JobListing], db: Session) -> list[JobListing]:
    """Filter out listings we've already stored."""
    new: list[JobListing] = []
    for listing in listings:
        key = make_dedup_key(listing)
        exists = db.query(Job.id).filter(Job.dedup_key == key).first()
        if not exists:
            new.append(listing)
    return new
