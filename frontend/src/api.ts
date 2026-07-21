import { Job, Stats, PipelineStats } from "./types";

const BASE = "/api";

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export async function fetchJobs(params: {
  status?: string;
  source?: string;
  min_score?: number;
  sort?: string;
}): Promise<Job[]> {
  const qs = new URLSearchParams();
  if (params.status) qs.set("status", params.status);
  if (params.source) qs.set("source", params.source);
  if (params.min_score !== undefined) qs.set("min_score", String(params.min_score));
  if (params.sort) qs.set("sort", params.sort);
  return request<Job[]>(`/jobs?${qs}`);
}

export async function fetchJob(id: number): Promise<Job> {
  return request<Job>(`/jobs/${id}`);
}

export async function updateJobStatus(id: number, status: string): Promise<Job> {
  return request<Job>(`/jobs/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export async function updateTailoredDocs(
  id: number,
  data: { tailored_resume?: string; tailored_cover_letter?: string }
): Promise<Job> {
  return request<Job>(`/jobs/${id}/tailored`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function triggerScrape(): Promise<PipelineStats> {
  return request<PipelineStats>("/scrape", { method: "POST" });
}

export async function fetchStats(): Promise<Stats> {
  return request<Stats>("/stats");
}
