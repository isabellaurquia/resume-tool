export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  description: string;
  url: string;
  source: string;
  posted_at: string;
  score: number;
  score_explanation: string;
  tailored_resume: string;
  tailored_cover_letter: string;
  status: string;
  scraped_at: string;
  updated_at: string;
}

export interface Stats {
  total: number;
  by_status: Record<string, number>;
  sources: string[];
}

export interface PipelineStats {
  scraped: number;
  new: number;
  scored: number;
  tailored: number;
  errors: string[];
}
