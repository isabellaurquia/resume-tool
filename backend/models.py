from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum as SAEnum
import enum

from backend.database import Base


class JobStatus(str, enum.Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEW = "interview"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, default="")
    description = Column(Text, default="")
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)
    posted_at = Column(String, default="")
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    dedup_key = Column(String, unique=True, index=True)

    score = Column(Float, default=0.0)
    score_explanation = Column(Text, default="")

    tailored_resume = Column(Text, default="")
    tailored_cover_letter = Column(Text, default="")

    status = Column(SAEnum(JobStatus), default=JobStatus.NEW)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
