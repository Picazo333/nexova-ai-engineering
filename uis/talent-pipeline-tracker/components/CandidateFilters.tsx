"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { labelStage, labelStatus, stageOptions, statusOptions } from "@/lib/labels";

export function CandidateFilters() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const status = searchParams.get("status") ?? "";
  const stage = searchParams.get("stage") ?? "";
  const q = searchParams.get("q") ?? "";
  const active = Boolean(status || stage || q.trim());

  function replace(next: { status?: string; stage?: string; q?: string }) {
    const params = new URLSearchParams(searchParams.toString());
    assign(params, "status", next.status ?? status);
    assign(params, "stage", next.stage ?? stage);
    assign(params, "q", next.q ?? q);
    const query = params.toString();
    router.replace(query ? `/?${query}` : "/", { scroll: false });
  }

  return (
    <section className="filters" aria-label="Filtros del listado">
      <div className="filter-grid">
        <label className="field" htmlFor="status">
          <span>Estado</span>
          <select
            id="status"
            value={status}
            onChange={(event) => replace({ status: event.target.value })}
          >
            <option value="">Todos los estados</option>
            {statusOptions(status).map((value) => (
              <option key={value} value={value}>
                {labelStatus(value)}
              </option>
            ))}
          </select>
        </label>
        <label className="field" htmlFor="stage">
          <span>Etapa</span>
          <select
            id="stage"
            value={stage}
            onChange={(event) => replace({ stage: event.target.value })}
          >
            <option value="">Todas las etapas</option>
            {stageOptions(stage).map((value) => (
              <option key={value} value={value}>
                {labelStage(value)}
              </option>
            ))}
          </select>
        </label>
        <label className="field field-search" htmlFor="q">
          <span>Buscar por nombre o correo</span>
          <input
            id="q"
            type="search"
            value={q}
            autoComplete="off"
            onChange={(event) => replace({ q: event.target.value })}
          />
        </label>
      </div>
      {active ? (
        <ul className="chips" aria-label="Filtros activos">
          {status ? (
            <li>
              <button type="button" onClick={() => replace({ status: "" })}>
                Quitar estado: {labelStatus(status)}
              </button>
            </li>
          ) : null}
          {stage ? (
            <li>
              <button type="button" onClick={() => replace({ stage: "" })}>
                Quitar etapa: {labelStage(stage)}
              </button>
            </li>
          ) : null}
          {q.trim() ? (
            <li>
              <button type="button" onClick={() => replace({ q: "" })}>
                Quitar búsqueda: {q.trim()}
              </button>
            </li>
          ) : null}
          <li>
            <button type="button" onClick={() => replace({ status: "", stage: "", q: "" })}>
              Quitar todos los filtros
            </button>
          </li>
        </ul>
      ) : null}
    </section>
  );
}

function assign(params: URLSearchParams, key: string, value: string) {
  if (value.trim()) params.set(key, value);
  else params.delete(key);
}
