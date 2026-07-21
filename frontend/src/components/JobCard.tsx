import React from "react";
import { Job } from "../types";

interface Props {
  job: Job;
  onClick: () => void;
}

function scoreClass(score: number): string {
  if (score >= 75) return "high";
  if (score >= 50) return "med";
  return "low";
}

export default function JobCard({ job, onClick }: Props) {
  return (
    <div className="job-card" onClick={onClick}>
      <div className="job-card-header">
        <div>
          <div className="job-card-title">{job.title}</div>
          <div className="job-card-company">{job.company}</div>
        </div>
        <span className={`badge badge-score ${scoreClass(job.score)}`}>
          {Math.round(job.score)}
        </span>
      </div>
      <div className="job-card-meta">
        <span className="badge badge-source">{job.source}</span>
        {job.location && (
          <span className="badge badge-location">{job.location}</span>
        )}
        <span className="badge badge-status">{job.status}</span>
        {job.tailored_resume && (
          <span className="badge badge-score">tailored</span>
        )}
      </div>
    </div>
  );
}
