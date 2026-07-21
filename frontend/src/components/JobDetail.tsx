import React, { useState } from "react";
import { Job } from "../types";
import { updateJobStatus, updateTailoredDocs } from "../api";

interface Props {
  job: Job;
  onClose: () => void;
  onUpdate: (job: Job) => void;
}

const STATUSES = ["new", "reviewed", "applied", "rejected", "interview"];

export default function JobDetail({ job, onClose, onUpdate }: Props) {
  const [resume, setResume] = useState(job.tailored_resume);
  const [cover, setCover] = useState(job.tailored_cover_letter);
  const [saving, setSaving] = useState(false);
  const [tab, setTab] = useState<"resume" | "cover" | "description">("resume");

  async function handleStatusChange(status: string) {
    const updated = await updateJobStatus(job.id, status);
    onUpdate(updated);
  }

  async function handleSave() {
    setSaving(true);
    try {
      const updated = await updateTailoredDocs(job.id, {
        tailored_resume: resume,
        tailored_cover_letter: cover,
      });
      onUpdate(updated);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="detail-overlay" onClick={onClose}>
      <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
        <div className="detail-header">
          <div>
            <div className="detail-title">{job.title}</div>
            <div className="detail-company">
              {job.company}
              {job.location ? ` · ${job.location}` : ""}
            </div>
          </div>
          <button className="detail-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="detail-actions">
          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="apply-btn"
            >
              Apply
            </a>
          )}
          <select
            className="status-select"
            value={job.status}
            onChange={(e) => handleStatusChange(e.target.value)}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {job.score_explanation && (
          <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: 8 }}>
            Score {Math.round(job.score)}/100 — {job.score_explanation}
          </div>
        )}

        <div className="filter-bar" style={{ marginBottom: 0 }}>
          {(["resume", "cover", "description"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                background: tab === t ? "var(--accent)" : "var(--surface)",
                color: tab === t ? "#fff" : "var(--text-secondary)",
                border: "1px solid var(--border)",
                padding: "6px 14px",
                borderRadius: "var(--radius)",
                fontSize: "0.78rem",
                fontWeight: 600,
              }}
            >
              {t === "resume"
                ? "Tailored Resume"
                : t === "cover"
                  ? "Cover Letter"
                  : "Job Description"}
            </button>
          ))}
        </div>

        <div className="detail-section">
          {tab === "resume" && (
            <>
              <h3>Tailored Resume</h3>
              <textarea
                value={resume}
                onChange={(e) => setResume(e.target.value)}
                placeholder="No tailored resume yet — run the pipeline with a valid OpenAI key to generate one."
              />
            </>
          )}
          {tab === "cover" && (
            <>
              <h3>Cover Letter</h3>
              <textarea
                value={cover}
                onChange={(e) => setCover(e.target.value)}
                placeholder="No cover letter yet."
              />
            </>
          )}
          {tab === "description" && (
            <>
              <h3>Job Description</h3>
              <div className="content">
                {job.description || "No description available."}
              </div>
            </>
          )}
        </div>

        {(tab === "resume" || tab === "cover") && (
          <button className="save-btn" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save Changes"}
          </button>
        )}
      </div>
    </div>
  );
}
