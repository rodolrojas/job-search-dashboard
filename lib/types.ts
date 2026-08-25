export type JobStatus = 'available' | 'applied' | 'rejected';

export interface Job {
  id: string;
  rank?: number;
  role: string;
  company: string;
  location: string;
  posted?: string;
  posted_evidence?: string;
  score: number;
  score_breakdown?: Record<string, number>;
  salary: string;
  employment_type: string;
  offer_url?: string;
  contact_email?: string;
  recruiter_or_careers_url?: string;
  suggested_resume: string;
  strategic_note?: string;
  live_check?: string;
  is_new: boolean;
  status: JobStatus;
}

export interface DashboardData {
  run: {
    date: string;
    timezone?: string;
    source_file: string;
  };
  summary: {
    distinct_candidates_reviewed: number;
    passed_all_filters: number;
    rejected_or_unverifiable: number;
    rejection_breakdown?: Record<string, number>;
  };
  jobs: Job[];
  top_three: Array<{ rank: number; company: string; reason: string }>;
  comparison: {
    added: Array<string | { role?: string; reason?: string }>;
    retained: Array<string | { role?: string; reason?: string }>;
    dropped: Array<string | { role?: string; reason?: string }>;
  };
  issues: string[];
  blocked_sources: Array<{ site: string; details: string }>;
  resume_variants: Array<{ key: string; label: string; headline: string; pdf: string }>;
}

export interface JobFilters {
  query: string;
  minScore: number;
  company: string;
  location: string;
  status: 'all' | JobStatus;
  sort: 'score_desc' | 'date_desc' | 'company_asc' | 'role_asc';
}

export interface CoverLetterResult {
  content: string;
  mode: 'codex' | 'local' | 'preview';
  warning?: string;
  filename: string;
  saved_to?: string;
}

export type AgentRunStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface AgentEvent {
  phase: string;
  message: string;
  details?: Record<string, unknown>;
  created_at: string;
}

export interface AgentRun {
  id: string;
  status: AgentRunStatus;
  phase: string;
  message: string;
  created_at: string;
  updated_at: string;
  events: AgentEvent[];
  result?: { output_file: string; result_count: number };
  error?: string;
}

export interface AgentInfo {
  configured: boolean;
  provider: string;
  model: string;
  runtime: string;
  runtime_version?: string;
  prompt_file: string;
  workflow: string[];
  guardrails: string[];
  latest_run?: AgentRun;
}
