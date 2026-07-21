"""Score job listings for fit against the user's profile using GPT-4o-mini."""
from __future__ import annotations

import json
from openai import AsyncOpenAI

from backend.config import settings
from backend.scrapers.base import JobListing

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


SCORING_PROMPT = """\
You are a job-fit scoring assistant. Given a candidate profile and a job listing,
score the fit from 0 to 100 and provide a one-sentence explanation.

Candidate profile:
{profile_summary}

Target roles: {target_roles}
Key skills: {skills}
Location preference: {locations}
Experience level: {experience_level}

Job listing:
Title: {title}
Company: {company}
Location: {location}
Description (first 1500 chars): {description}

Respond with ONLY valid JSON: {{"score": <int 0-100>, "explanation": "<one sentence>"}}
"""


async def score_job(listing: JobListing, profile: dict) -> tuple[float, str]:
    if not settings.openai_api_key:
        return 50.0, "No OpenAI key — default score assigned"

    prompt = SCORING_PROMPT.format(
        profile_summary=profile.get("background_summary", ""),
        target_roles=", ".join(profile.get("target_roles", [])),
        skills=", ".join(profile.get("skills", [])),
        locations=", ".join(profile.get("locations", [])),
        experience_level=profile.get("experience_level", "mid"),
        title=listing.title,
        company=listing.company,
        location=listing.location,
        description=listing.description[:1500],
    )

    try:
        client = _get_client()
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150,
        )
        raw = resp.choices[0].message.content.strip()
        data = json.loads(raw)
        return float(data["score"]), data.get("explanation", "")
    except Exception as e:
        return 0.0, f"Scoring failed: {e}"
