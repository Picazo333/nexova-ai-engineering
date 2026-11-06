import type { Candidate } from "@/types/candidate";

export interface CandidateQuery {
  status: string;
  stage: string;
  q: string;
}

export function emptyQuery(): CandidateQuery {
  return { status: "", stage: "", q: "" };
}

export function foldText(value: string): string {
  return value.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();
}

export function filterCandidates(records: Candidate[], query: CandidateQuery): Candidate[] {
  const status = query.status.trim();
  const stage = query.stage.trim();
  const text = foldText(query.q.trim());

  return records.filter((record) => {
    if (status && record.status !== status) return false;
    if (stage && record.stage !== stage) return false;
    if (!text) return true;
    return (
      foldText(record.full_name).includes(text) || foldText(record.email).includes(text)
    );
  });
}

export function hasActiveQuery(query: CandidateQuery): boolean {
  return Boolean(query.status || query.stage || query.q.trim());
}
