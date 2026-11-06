"use client";

import { useEffect, useState } from "react";

import { readStack } from "@/lib/stack";

const FILTER_KEY = "nexova-backoffice-filter";

type Stack =
  | { phase: "loading" }
  | { phase: "ok"; upstream: string }
  | { phase: "error"; message: string };

export function StackStatus() {
  const [attempt, setAttempt] = useState(0);
  const [stack, setStack] = useState<Stack>({ phase: "loading" });
  const [filter, setFilter] = useState("");
  const [arrived, setArrived] = useState(false);

  useEffect(() => {
    const saved = window.sessionStorage.getItem(FILTER_KEY);
    if (saved) setFilter(saved);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    let ignore = false;
    setStack({ phase: "loading" });
    setArrived(false);
    readStack(controller.signal)
      .then((body) => {
        if (ignore) return;
        if (body.ok && body.upstream) {
          setStack({ phase: "ok", upstream: body.upstream });
          setArrived(true);
          return;
        }
        setStack({
          phase: "error",
          message: body.message || "No hay conexión con la API.",
        });
      })
      .catch((error: unknown) => {
        if (ignore || (error instanceof DOMException && error.name === "AbortError")) return;
        setStack({ phase: "error", message: "No hay conexión con la API." });
      });
    return () => {
      ignore = true;
      controller.abort();
    };
  }, [attempt]);

  function onFilter(value: string) {
    setFilter(value);
    window.sessionStorage.setItem(FILTER_KEY, value);
  }

  const query = filter.trim().toLowerCase();
  const emptyCopy = query
    ? "Ninguna incidencia coincide con ese texto."
    : "Este proceso no guarda incidencias. El listado está en el portal.";

  return (
    <>
      <section
        className="result-panel"
        data-motion-node
        data-arrived={arrived ? "true" : "false"}
        aria-live="polite"
      >
        <p
          className={stack.phase === "error" ? "alert stack-status" : "note stack-status"}
          role={stack.phase === "error" ? "alert" : "status"}
        >
          {stack.phase === "error"
            ? `${stack.message} El filtro se conserva.`
            : stack.phase === "ok"
              ? "La API responde."
              : "Comprobando la conexión con la API."}
        </p>
        <div className="table-scroll" role="region" aria-label="Comprobación de la API" tabIndex={0}>
          <table>
            <caption>Conexión con la API</caption>
            <thead>
              <tr>
                <th scope="col">Comprobación</th>
                <th scope="col">Resultado</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">Destino interno</th>
                <td className="mono">{stack.phase === "ok" ? stack.upstream : "—"}</td>
              </tr>
              <tr>
                <th scope="row">Estado</th>
                <td>
                  {stack.phase === "loading" ? "Comprobando la API." : null}
                  {stack.phase === "ok" ? "En marcha" : null}
                  {stack.phase === "error" ? "Sin conexión" : null}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="actions">
          <button type="button" onClick={() => setAttempt((value) => value + 1)} disabled={stack.phase === "loading"}>
            Reintentar
          </button>
        </div>
      </section>

      <section>
        <h2>Incidencias de este proceso</h2>
        <label className="field" htmlFor="filtro">
          Filtrar por texto
          <input
            id="filtro"
            name="filtro"
            value={filter}
            onChange={(event) => onFilter(event.target.value)}
            autoComplete="off"
          />
        </label>
        <p>{emptyCopy}</p>
      </section>
    </>
  );
}
