import React, { useEffect, useState, useCallback } from "react";
import { Job, Stats, PipelineStats } from "./types";
import { fetchJobs, fetchStats, triggerScrape } from "./api";
import FilterBar from "./components/FilterBar";
import JobCard from "./components/JobCard";
import JobDetail from "./components/JobDetail";

export default function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [scraping, setScraping] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const [status, setStatus] = useState("");
  const [source, setSource] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [sort, setSort] = useState("score");

  const loadJobs = useCallback(async () => {
    try {
      const data = await fetchJobs({ status, source, min_score: minScore, sort });
      setJobs(data);
    } catch {
      showToast("Failed to load jobs");
    }
  }, [status, source, minScore, sort]);

  const loadStats = useCallback(async () => {
    try {
      setStats(await fetchStats());
    } catch {}
  }, []);

  useEffect(() => {
    loadJobs();
    loadStats();
  }, [loadJobs, loadStats]);

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  }

  async function handleScrape() {
    setScraping(true);
    showToast("Scraping started — this may take a minute...");
    try {
      const result: PipelineStats = await triggerScrape();
      showToast(
        `Done! Scraped ${result.scraped}, ${result.new} new, ${result.tailored} tailored.` +
          (result.errors.length ? ` (${result.errors.length} errors)` : "")
      );
      await loadJobs();
      await loadStats();
    } catch {
      showToast("Scrape failed — check the backend logs.");
    } finally {
      setScraping(false);
    }
  }

  function handleJobUpdate(updated: Job) {
    setJobs((prev) => prev.map((j) => (j.id === updated.id ? updated : j)));
    setSelectedJob(updated);
  }

  return (
    <div className="app">
      <header className="header">
        <h1>JobPilot</h1>
        <div className="header-stats">
          {stats && (
            <>
              <span>{stats.total} jobs</span>
              <span>{stats.by_status?.new ?? 0} new</span>
              <span>{stats.by_status?.applied ?? 0} applied</span>
            </>
          )}
        </div>
        <button
          className="scrape-btn"
          onClick={handleScrape}
          disabled={scraping}
        >
          {scraping ? "Scraping..." : "Scrape Now"}
        </button>
      </header>

      <FilterBar
        status={status}
        source={source}
        minScore={minScore}
        sort={sort}
        sources={stats?.sources ?? []}
        onStatusChange={setStatus}
        onSourceChange={setSource}
        onMinScoreChange={setMinScore}
        onSortChange={setSort}
      />

      <div className="job-list">
        {jobs.length === 0 ? (
          <div className="empty-state">
            No jobs yet. Click <strong>Scrape Now</strong> to fetch listings, or
            check your <code>profile.yaml</code> and API keys.
          </div>
        ) : (
          jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onClick={() => setSelectedJob(job)}
            />
          ))
        )}
      </div>

      {selectedJob && (
        <JobDetail
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
          onUpdate={handleJobUpdate}
        />
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
