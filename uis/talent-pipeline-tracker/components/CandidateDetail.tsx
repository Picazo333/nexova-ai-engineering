"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ErrorStatus, LoadingStatus } from "@/components/AsyncStatus";
import { NotesPanel } from "@/components/NotesPanel";
import { PipelineControls } from "@/components/PipelineControls";
import { useAsyncResource } from "@/hooks/useAsyncResource";
import { useTracker } from "@/hooks/useTracker";
import { formatDate, formatExperience } from "@/lib/format";
import { labelStage, labelStatus } from "@/lib/labels";
import type { Candidate } from "@/types/candidate";

export function CandidateDetail({ id }: { id: string }) {
  const api = useTracker();
  const loadRecord = useCallback((signal: AbortSignal) => api.getRecord(id, signal), [api, id]);
  const searchParams = useSearchParams();
  const from = searchParams.get("from") ?? "";
  const backHref = from ? `/?${from}` : "/";
  const editHref = from
    ? `/candidates/${id}/edit?from=${encodeURIComponent(from)}`
    : `/candidates/${id}/edit`;
  const resource = useAsyncResource(id, loadRecord);
  const [patched, setPatched] = useState<Candidate | null>(null);
  const record = patched && patched.id === id ? patched : (resource.data ?? null);

  useEffect(() => {
    if (record) document.title = `${record.full_name} · Nexova Solutions`;
  }, [record]);

  return (
    <>
      <p className="back">
        <Link href={backHref}>Volver al listado</Link>
      </p>
      {resource.status === "loading" && !record ? <LoadingStatus label="Cargando la candidatura…" /> : null}
      {resource.status === "error" && !record ? (
        <ErrorStatus message={resource.error ?? "No se pudo cargar la candidatura."} onRetry={resource.retry} />
      ) : null}
      {record ? (
        <>
          <header className="detail-head">
            <h1>{record.full_name}</h1>
            <p className="lead">{record.position}</p>
            <Link className="button button-secondary" href={editHref}>
              Editar datos
            </Link>
          </header>
          <PipelineControls key={record.id} candidate={record} onUpdated={setPatched} />
          <dl className="facts">
            <div>
              <dt>Correo</dt>
              <dd>
                <a href={`mailto:${record.email}`}>{record.email}</a>
              </dd>
            </div>
            <div>
              <dt>Teléfono</dt>
              <dd>
                <a href={`tel:${record.phone}`}>{record.phone}</a>
              </dd>
            </div>
            <div>
              <dt>Puesto</dt>
              <dd>{record.position}</dd>
            </div>
            <div>
              <dt>Años de experiencia</dt>
              <dd>{formatExperience(record.experience_years)}</dd>
            </div>
            <div>
              <dt>LinkedIn</dt>
              <dd>
                {record.linkedin_url ? (
                  <a href={record.linkedin_url} target="_blank" rel="noopener noreferrer">
                    Perfil de LinkedIn (se abre en otra pestaña)
                  </a>
                ) : (
                  "No indicado"
                )}
              </dd>
            </div>
            <div>
              <dt>CV</dt>
              <dd>
                {record.cv_url ? (
                  <a href={record.cv_url} target="_blank" rel="noopener noreferrer">
                    Abrir CV (se abre en otra pestaña)
                  </a>
                ) : (
                  "No indicado"
                )}
              </dd>
            </div>
            <div>
              <dt>Estado</dt>
              <dd>{labelStatus(record.status)}</dd>
            </div>
            <div>
              <dt>Etapa</dt>
              <dd>{labelStage(record.stage)}</dd>
            </div>
            <div>
              <dt>Fecha de aplicación</dt>
              <dd>
                <time dateTime={record.applied_at}>{formatDate(record.applied_at)}</time>
              </dd>
            </div>
            <div>
              <dt>Última actualización</dt>
              <dd>
                <time dateTime={record.updated_at}>{formatDate(record.updated_at)}</time>
              </dd>
            </div>
          </dl>
          <NotesPanel key={record.id} recordId={record.id} />
        </>
      ) : null}
    </>
  );
}
