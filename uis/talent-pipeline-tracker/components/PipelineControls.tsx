"use client";

import { useRef, useState } from "react";
import { useTracker } from "@/hooks/useTracker";
import { createRequestGuard } from "@/lib/guard";
import { toErrorMessage } from "@/lib/errors";
import { labelStage, labelStatus, stageOptions, statusOptions } from "@/lib/labels";
import type { Candidate } from "@/types/candidate";

export function PipelineControls({
  candidate,
  onUpdated,
}: {
  candidate: Candidate;
  onUpdated: (candidate: Candidate) => void;
}) {
  const api = useTracker();
  const guardRef = useRef(createRequestGuard());
  const [draft, setDraft] = useState<{ id: string; status: string; stage: string } | null>(null);
  const status = draft?.id === candidate.id ? draft.status : candidate.status;
  const stage = draft?.id === candidate.id ? draft.stage : candidate.stage;
  const [pending, setPending] = useState<"status" | "stage" | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function update(field: "status" | "stage", value: string) {
    const requestId = guardRef.current.next();
    const recordId = candidate.id;
    setDraft({
      id: recordId,
      status: field === "status" ? value : status,
      stage: field === "stage" ? value : stage,
    });
    setPending(field);
    setError(null);
    setMessage(null);
    try {
      const updated = await api.patchRecord(recordId, { [field]: value });
      if (!guardRef.current.isCurrent(requestId) || updated.id !== recordId) return;
      onUpdated(updated);
      setMessage(field === "status" ? "Estado actualizado." : "Etapa actualizada.");
    } catch (cause) {
      if (!guardRef.current.isCurrent(requestId)) return;
      setDraft(null);
      setError(toErrorMessage(cause));
    } finally {
      if (guardRef.current.isCurrent(requestId)) setPending(null);
    }
  }

  return (
    <section className="pipeline" aria-label="Actualizar estado y etapa">
      <label className="field" htmlFor="patch-status">
        <span>Estado</span>
        <select
          id="patch-status"
          value={status}
          disabled={pending !== null}
          aria-busy={pending === "status"}
          onChange={(event) => void update("status", event.target.value)}
        >
          {statusOptions(status).map((value) => (
            <option key={value} value={value}>
              {labelStatus(value)}
            </option>
          ))}
        </select>
      </label>
      <label className="field" htmlFor="patch-stage">
        <span>Etapa</span>
        <select
          id="patch-stage"
          value={stage}
          disabled={pending !== null}
          aria-busy={pending === "stage"}
          onChange={(event) => void update("stage", event.target.value)}
        >
          {stageOptions(stage).map((value) => (
            <option key={value} value={value}>
              {labelStage(value)}
            </option>
          ))}
        </select>
      </label>
      {pending ? (
        <p className="feedback feedback-status" role="status">
          {pending === "status" ? "Guardando el estado…" : "Guardando la etapa…"}
        </p>
      ) : null}
      {message ? (
        <p className="feedback feedback-success" role="status">
          {message}
        </p>
      ) : null}
      {error ? (
        <p className="feedback feedback-error" role="alert">
          {error}
        </p>
      ) : null}
    </section>
  );
}
