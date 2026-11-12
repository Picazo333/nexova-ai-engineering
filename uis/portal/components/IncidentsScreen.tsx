"use client";

import { useRef, useState } from "react";

import { ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { ApiError, apiDownload, apiFetch } from "@/lib/api";
import type { IncidentReport } from "@/lib/types";

export function IncidentsScreen() {
  const [report, setReport] = useState<IncidentReport | null>(null);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  const [status, setStatus] = useState("");
  const request = useRef(0);
  const alertRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const file = fileRef.current?.files?.[0];
    if (!file) {
      setError("Elige un CSV antes de analizar.");
      alertRef.current?.focus();
      return;
    }
    const id = ++request.current;
    setPending(true);
    setError("");
    setStatus("Analizando el fichero…");
    const body = new FormData();
    body.set("file", file);
    try {
      const next = await apiFetch<IncidentReport>("/api/incidents/analyze", { method: "POST", body });
      if (id !== request.current) return;
      setReport(next);
      setStatus("Análisis listo.");
    } catch (caught: unknown) {
      if (id !== request.current) return;
      setError(caught instanceof ApiError ? caught.message : "No se pudo analizar el fichero.");
      setStatus("");
      alertRef.current?.focus();
    } finally {
      if (id === request.current) setPending(false);
    }
  }

  async function download() {
    setError("");
    try {
      const blob = await apiDownload("/api/incidents/results/export");
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "results.csv";
      link.click();
      URL.revokeObjectURL(url);
    } catch (caught: unknown) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo descargar el CSV.");
      alertRef.current?.focus();
    }
  }

  const rules = report?.invalid_breakdown.filter((item) => item.count > 0) ?? [];

  return (
    <>
      <h1>Análisis de tickets de soporte</h1>
      <p className="lead">
        Sube el CSV del helpdesk. La API cuenta filas válidas e inválidas. El fichero no sale de esta
        máquina y el portal no pinta correos.
      </p>
      {error ? (
        <ErrorBanner
          title="No se pudo analizar"
          message={error}
          alertRef={alertRef}
          onRetry={() => {
            const selected = fileRef.current?.files?.[0];
            if (!selected) {
              fileRef.current?.focus();
              return;
            }
            const form = fileRef.current?.form;
            form?.requestSubmit();
          }}
        />
      ) : null}
      <form className="panel stack" onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="csv-file">Fichero CSV</label>
          <input
            id="csv-file"
            ref={fileRef}
            name="file"
            type="file"
            accept=".csv,text/csv"
            aria-describedby="file-hint"
          />
          <p id="file-hint" className="note">
            Columnas: ticket_id, date, client_company, category, description, agent_id, status,
            customer_email, satisfaction_score.
          </p>
        </div>
        <p className="actions">
          <button className="button" type="submit" disabled={pending} aria-busy={pending}>
            Analizar fichero
          </button>
        </p>
        {pending ? <LoadingState label={status || "Analizando el fichero…"} /> : <p role="status">{status}</p>}
      </form>
      {!report ? (
        <p className="note">Aún no hay un análisis en esta visita. Elige el CSV de tickets.</p>
      ) : (
        <section className="result-panel" data-motion-node="" data-arrived="true" aria-labelledby="resultado">
          <h2 id="resultado">Resultado</h2>
          <p>{report.summary_es}</p>
          <div className="table-scroll" role="region" aria-label="Desplazamiento horizontal de los totales">
            <table>
              <caption>Totales del fichero</caption>
              <thead>
                <tr>
                  <th scope="col">Métrica</th>
                  <th className="num" scope="col">
                    Cantidad
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Registros en el fichero</td>
                  <td className="num">{report.total_records}</td>
                </tr>
                <tr>
                  <td>Válidos</td>
                  <td className="num">{report.valid_records}</td>
                </tr>
                <tr>
                  <td>Inválidos o incompletos</td>
                  <td className="num">{report.invalid_records}</td>
                </tr>
              </tbody>
            </table>
          </div>
          {rules.length === 0 ? (
            <p>Ninguna fila inválida en este fichero.</p>
          ) : (
            <div className="table-scroll" role="region" aria-label="Desplazamiento horizontal de las reglas">
              <table>
                <caption>Reglas con filas inválidas</caption>
                <thead>
                  <tr>
                    <th scope="col">Problema</th>
                    <th className="num" scope="col">
                      Registros
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {rules.map((rule) => (
                    <tr key={rule.code}>
                      <td>{rule.label_es}</td>
                      <td className="num">{rule.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="actions">
            <button className="button secondary" type="button" onClick={download}>
              Descargar results.csv
            </button>
          </p>
        </section>
      )}
    </>
  );
}
