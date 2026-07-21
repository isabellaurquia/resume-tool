from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import BaseModel

from backend.config import settings
from backend.database import get_db, init_db
from backend.models import Job, JobStatus
from backend.services.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("jobpilot")

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.add_job(
        run_pipeline,
        "interval",
        hours=settings.scrape_interval_hours,
        id="scrape_pipeline",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started — scraping every {settings.scrape_interval_hours}h")
    yield
    scheduler.shutdown()


app = FastAPI(title="JobPilot", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemas ---


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    posted_at: str
    score: float
    score_explanation: str
    tailored_resume: str
    tailored_cover_letter: str
    status: str
    scraped_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_job(cls, job: Job) -> "JobOut":
        return cls(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            description=job.description or "",
            url=job.url,
            source=job.source,
            posted_at=job.posted_at or "",
            score=job.score or 0.0,
            score_explanation=job.score_explanation or "",
            tailored_resume=job.tailored_resume or "",
            tailored_cover_letter=job.tailored_cover_letter or "",
            status=job.status.value if job.status else "new",
            scraped_at=job.scraped_at.isoformat() if job.scraped_at else "",
            updated_at=job.updated_at.isoformat() if job.updated_at else "",
        )


class StatusUpdate(BaseModel):
    status: str


class TailoredDocsUpdate(BaseModel):
    tailored_resume: Optional[str] = None
    tailored_cover_letter: Optional[str] = None


class PipelineStats(BaseModel):
    scraped: int
    new: int
    scored: int
    tailored: int
    errors: list[str]


# --- Endpoints ---


@app.get("/api/jobs", response_model=list[JobOut])
def list_jobs(
    status: Optional[str] = None,
    source: Optional[str] = None,
    min_score: float = Query(default=0, ge=0, le=100),
    sort: str = Query(default="score", pattern="^(score|scraped_at|updated_at)$"),
    db: Session = Depends(get_db),
):
    q = db.query(Job)
    if status:
        q = q.filter(Job.status == status)
    if source:
        q = q.filter(Job.source == source)
    q = q.filter(Job.score >= min_score)

    order_col = getattr(Job, sort, Job.score)
    q = q.order_by(order_col.desc())

    jobs = q.limit(200).all()
    return [JobOut.from_job(j) for j in jobs]


@app.get("/api/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut.from_job(job)


@app.patch("/api/jobs/{job_id}/status", response_model=JobOut)
def update_status(job_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    try:
        job.status = JobStatus(body.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")
    db.commit()
    db.refresh(job)
    return JobOut.from_job(job)


@app.patch("/api/jobs/{job_id}/tailored", response_model=JobOut)
def update_tailored_docs(job_id: int, body: TailoredDocsUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if body.tailored_resume is not None:
        job.tailored_resume = body.tailored_resume
    if body.tailored_cover_letter is not None:
        job.tailored_cover_letter = body.tailored_cover_letter
    db.commit()
    db.refresh(job)
    return JobOut.from_job(job)


@app.post("/api/scrape", response_model=PipelineStats)
async def trigger_scrape():
    stats = await run_pipeline()
    return PipelineStats(**stats)


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Job).count()
    by_status = {}
    for status in JobStatus:
        by_status[status.value] = db.query(Job).filter(Job.status == status).count()
    sources = db.query(Job.source).distinct().all()
    return {
        "total": total,
        "by_status": by_status,
        "sources": [s[0] for s in sources],
    }
