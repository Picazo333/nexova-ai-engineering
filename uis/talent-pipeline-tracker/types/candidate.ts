export const CANDIDATE_STATUSES = [
  "received",
  "in_progress",
  "selected",
  "discarded",
] as const;

export const CANDIDATE_STAGES = [
  "pending",
  "review",
  "personal_interview",
  "technical_interview",
  "offer_presented",
] as const;

export type CandidateStatus = (typeof CANDIDATE_STATUSES)[number];
export type CandidateStage = (typeof CANDIDATE_STAGES)[number];

export interface Candidate {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  position: string;
  linkedin_url: string | null;
  cv_url: string | null;
  status: string;
  stage: string;
  experience_years: number;
  notes_count: number;
  applied_at: string;
  updated_at: string;
}

export interface CandidateWrite {
  full_name: string;
  email: string;
  phone: string;
  position: string;
  linkedin_url: string | null;
  cv_url: string | null;
  experience_years: number;
}

export interface CandidatePatch {
  status?: string;
  stage?: string;
}

export interface RecordList {
  total: number;
  page: number;
  limit: number;
  data: Candidate[];
}
