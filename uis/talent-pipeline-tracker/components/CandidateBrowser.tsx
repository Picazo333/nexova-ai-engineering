"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useCallback } from "react";
import { CandidateFilters } from "@/components/CandidateFilters";
import { EmptyStatus, ErrorStatus, LoadingStatus } from "@/components/AsyncStatus";
import { useAsyncResource } from "@/hooks/useAsyncResource";
import { useTracker } from "@/hooks/useTracker";
import { filterCandidates } from "@/lib/filters";
import { formatNotesCount } from "@/lib/format";
import { labelStage, labelStatus } from "@/lib/labels";

export function CandidateBrowser() {
  const api = useTracker();
  const loadRecords = useCallback((signal: AbortSignal) => api.listAllRecords(signal), [api]);
  const searchParams = useSearchParams();
  const query = {
    status: searchParams.get("status") ?? "",
    stage: searchParams.get("stage") ?? "",
    q: searchParams.get("q") ?? "",
  };
  const resource = useAsyncResource("records", loadRecords);
  const records = resource.data?.data ?? [];
  const visible = filterCandidates(records, query);
  const returnQuery = searchParams.toString();

  return (
    <>
      <CandidateFilters />
      {resource.status === "loading" && !resource.data ? (
        <LoadingStatus label="Cargando candidaturas…" />
      ) : null}
      {resource.status === "error" ? (
        <ErrorStatus
          message={resource.error ?? "No se pudo cargar el listado."}
          onRetry={resource.retry}
        />
      ) : null}
      {resource.status === "loading" && resource.data ? (
        <LoadingStatus label="Actualizando candidaturas…" />
      ) : null}
      {resource.data && records.length === 0 ? (
        <EmptyStatus title="No hay candidaturas registradas">
          <p>Registra la primera desde el formulario.</p>
          <Link className="button button-primary" href="/candidates/new">
            Registrar candidatura
          </Link>
        </EmptyStatus>
      ) : null}
      {resource.data && records.length > 0 ? (
        <>
          <p className="count" aria-live="polite">
            {visible.length} de {resource.data.total} candidaturas
          </p>
          {visible.length === 0 ? (
            <EmptyStatus title="Ninguna candidatura coincide">
              <p>Prueba con otro nombre, correo, estado o etapa.</p>
            </EmptyStatus>
          ) : (
            <ul className="candidate-list">
              {visible.map((candidate) => {
                const href = returnQuery
                  ? `/candidates/${candidate.id}?from=${encodeURIComponent(returnQuery)}`
                  : `/candidates/${candidate.id}`;
                return (
                  <li key={candidate.id}>
                    <Link className="candidate-row" href={href}>
                      <span className="candidate-name">{candidate.full_name}</span>
                      <span className="candidate-role">{candidate.position}</span>
                      <span className="candidate-mail">{candidate.email}</span>
                      <span className="badge">{labelStatus(candidate.status)}</span>
                      <span className="badge badge-stage">{labelStage(candidate.stage)}</span>
                      <span className="candidate-notes">{formatNotesCount(candidate.notes_count)}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          )}
        </>
      ) : null}
    </>
  );
}
