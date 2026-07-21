"""Tailor resume and cover letter for a specific job using GPT-4o."""
from __future__ import annotations

from openai import AsyncOpenAI
from backend.config import settings

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


RESUME_PROMPT = """\
You are a professional resume writer. Given the candidate's base resume and a job description,
produce a tailored resume in clean Markdown format. Emphasize the most relevant experience,
skills, and accomplishments for this specific role. Keep the same factual content — do NOT
fabricate experience — but reorder, rephrase, and highlight what matters most for this job.

Base resume:
{resume_text}

Job listing:
Title: {title}
Company: {company}
Description: {description}

Output the tailored resume in Markdown. Do not include any preamble or explanation.
"""

COVER_LETTER_PROMPT = """\
You are a professional cover letter writer. Given the candidate's background and a job description,
write a compelling cover letter (3-4 paragraphs, under 350 words). Be specific about why this
candidate is a strong fit for THIS role at THIS company. Sound human and authentic, not generic.

Candidate background:
{resume_text}

Job listing:
Title: {title}
Company: {company}
Description: {description}

Output the cover letter in plain text. Do not include any preamble or explanation.
"""


async def tailor_resume(resume_text: str, title: str, company: str, description: str) -> str:
    if not settings.openai_api_key:
        return "OpenAI API key not configured — cannot generate tailored resume."
    try:
        client = _get_client()
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": RESUME_PROMPT.format(
                        resume_text=resume_text,
                        title=title,
                        company=company,
                        description=description[:3000],
                    ),
                }
            ],
            temperature=0.4,
            max_tokens=2000,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Resume tailoring failed: {e}"


async def tailor_cover_letter(resume_text: str, title: str, company: str, description: str) -> str:
    if not settings.openai_api_key:
        return "OpenAI API key not configured — cannot generate cover letter."
    try:
        client = _get_client()
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": COVER_LETTER_PROMPT.format(
                        resume_text=resume_text,
                        title=title,
                        company=company,
                        description=description[:3000],
                    ),
                }
            ],
            temperature=0.5,
            max_tokens=1000,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Cover letter generation failed: {e}"


async def tailor_job(resume_text: str, title: str, company: str, description: str) -> tuple[str, str]:
    resume = await tailor_resume(resume_text, title, company, description)
    cover = await tailor_cover_letter(resume_text, title, company, description)
    return resume, cover
