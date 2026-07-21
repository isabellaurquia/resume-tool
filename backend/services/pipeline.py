"""End-to-end scrape -> dedup -> score -> tailor pipeline."""

import logging
from sqlalchemy.orm import Session

from backend.config import settings, load_profile
from backend.database import SessionLocal
from backend.models import Job
from backend.scrapers.base import JobListing
from backend.scrapers.remoteok import RemoteOKScraper
from backend.scrapers.linkedin import LinkedInScraper
from backend.scrapers.indeed import IndeedScraper
from backend.scrapers.hn import HNScraper
from backend.services.dedup import deduplicate, make_dedup_key
from backend.services.matcher import score_job
from backend.services.tailor import tailor_job
from backend.services.profile import get_resume_text

logger = logging.getLogger("jobpilot.pipeline")

SCRAPERS = [
    RemoteOKScraper(),
    LinkedInScraper(),
    IndeedScraper(),
    HNScraper(),
]


async def run_pipeline() -> dict:
    """Run full scrape+process pipeline. Returns summary stats."""
    profile = load_profile()
    queries = profile.get("search_queries", [])
    locations = profile.get("locations", [])
    primary_location = locations[0] if locations else None

    stats = {"scraped": 0, "new": 0, "scored": 0, "tailored": 0, "errors": []}

    all_listings: list[JobListing] = []
    for scraper in SCRAPERS:
        try:
            listings = await scraper.scrape(queries, primary_location)
            all_listings.extend(listings)
            logger.info(f"{scraper.name}: found {len(listings)} listings")
        except Exception as e:
            logger.error(f"{scraper.name} failed: {e}")
            stats["errors"].append(f"{scraper.name}: {e}")

    stats["scraped"] = len(all_listings)

    db: Session = SessionLocal()
    try:
        new_listings = deduplicate(all_listings, db)
        stats["new"] = len(new_listings)
        logger.info(f"After dedup: {len(new_listings)} new listings")

        resume_text = get_resume_text(profile)

        for listing in new_listings:
            score, explanation = await score_job(listing, profile)
            stats["scored"] += 1

            job = Job(
                title=listing.title,
                company=listing.company,
                location=listing.location,
                description=listing.description,
                url=listing.url,
                source=listing.source,
                posted_at=listing.posted_at,
                dedup_key=make_dedup_key(listing),
                score=score,
                score_explanation=explanation,
            )

            if score >= settings.score_threshold:
                try:
                    tailored_resume, cover_letter = await tailor_job(
                        resume_text, listing.title, listing.company, listing.description
                    )
                    job.tailored_resume = tailored_resume
                    job.tailored_cover_letter = cover_letter
                    stats["tailored"] += 1
                except Exception as e:
                    logger.error(f"Tailoring failed for {listing.title}: {e}")
                    stats["errors"].append(f"tailor {listing.title}: {e}")

            db.add(job)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Pipeline error: {e}")
        stats["errors"].append(str(e))
    finally:
        db.close()

    logger.info(f"Pipeline complete: {stats}")
    return stats
