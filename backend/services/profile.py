"""Load user profile and extract resume text from PDF if available."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from backend.config import PROJECT_ROOT, load_profile


def get_resume_text(profile: Optional[dict] = None) -> str:
    if profile is None:
        profile = load_profile()

    # Prefer explicit resume_text in profile.yaml
    text = profile.get("resume_text", "").strip()
    if text and not text.startswith("Paste your full resume"):
        return text

    # Fall back to parsing resume.pdf
    pdf_path = PROJECT_ROOT / "resume.pdf"
    if pdf_path.exists():
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n\n".join(pages).strip()
        except Exception:
            pass

    return text


def get_profile_with_resume() -> dict:
    profile = load_profile()
    profile["_resume_text"] = get_resume_text(profile)
    return profile
